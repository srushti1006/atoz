from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
import instaloader
import json
from twython import Twython
import os
import tempfile
import torch

# Load BLIP model and processor for image captioning
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Set device to CUDA if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def fetch_instagram_content(url):
    try:
        loader = instaloader.Instaloader()
        
        # Login if needed
        # loader.login('your_username', 'your_password')  # replace with your Instagram credentials
        
        shortcode = url.split('/')[-2]  # Extract the shortcode from URL
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        return {
            "caption": post.caption,
            "media_url": post.url,
            "likes": post.likes,
            "comments": post.comments
        }
    except Exception as e:
        return extract_instagram_data(url)  # Fallback to web scraping

# Fallback function to scrape Instagram content without API
def extract_instagram_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        image_url = soup.find('meta', property='og:image').get('content', None)
        caption = soup.find('meta', property='og:description').get('content', None)
        video_url = soup.find('meta', property='og:video')
        audio_url = soup.find('meta', property='og:audio')

        # Extract comments if available
        comments = []
        script_tag = soup.find('script', text=lambda t: t and 'window._sharedData' in t)
        if script_tag:
            json_data = script_tag.string.split(' = ', 1)[1].rstrip(';')
            data = json.loads(json_data)
            comments = [
                comment['node']['text']
                for comment in data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
                .get('edge_media_to_comment', {}).get('edges', [])
            ]

        return {
            'image_url': image_url,
            'caption': caption,
            'video_url': video_url,
            'audio_url': audio_url,
            'comments': comments
        }
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

# Function to fetch Facebook content
def fetch_facebook_content(url, access_token):
    post_id = url.split('/')[-1]
    graph_url = f"https://graph.facebook.com/{post_id}?fields=message,attachments&access_token={access_token}"
    response = requests.get(graph_url)
    return response.json() if response.status_code == 200 else {"error": "Failed to fetch Facebook content"}

# Function to fetch content from X (formerly Twitter)
def fetch_x_content(url, api_key, api_secret, access_token, access_secret):
    twitter = Twython(api_key, api_secret, access_token, access_secret)
    tweet_id = url.split('/')[-1]
    try:
        tweet = twitter.show_status(id=tweet_id)
        media_url = tweet['entities']['media'][0]['media_url'] if 'media' in tweet['entities'] else None
        return {"text": tweet['text'], "media_url": media_url}
    except Exception as e:
        return {"error": str(e)}

# Function to analyze image using BLIP model
def analyze_image(image_path):
    try:
        # Open the image from the file path
        image = Image.open(image_path)
        inputs = processor(image, return_tensors="pt").to(device)

        prompts = [
            "Describe the image: ",
        ]

        detailed_analysis = []
        for prompt in prompts:
            prompt_inputs = processor(image, text=prompt, return_tensors="pt").to(device)
            output = model.generate(
                **prompt_inputs,
                max_length=100,
                num_beams=5,
                no_repeat_ngram_size=2
            )
            caption = processor.decode(output[0], skip_special_tokens=True)
            detailed_analysis.append(caption)

        return "\n".join(detailed_analysis)
    except Exception as e:
        return str(e)

# Main function to fetch content based on URL
def fetch_content_from_url(url):
    if "instagram.com" in url:
        return fetch_instagram_content(url)
    elif "facebook.com" in url:
        return fetch_facebook_content(url, access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"))
    elif "twitter.com" in url or "x.com" in url:
        return fetch_x_content(
            url,
            api_key=os.getenv("TWITTER_API_KEY"),
            api_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_secret=os.getenv("TWITTER_ACCESS_SECRET")
        )
    return {"error": "Unsupported platform"}

# Django view to process the URL
def process_url(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    data = fetch_content_from_url(url)
    if 'error' in data:
        return JsonResponse({'error': data['error']}, status=400)

    # If media content is found, analyze it
    if 'media_url' in data and data['media_url']:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            print(temp_file.name)
            image_response = requests.get(data['media_url'], stream=True)
            if image_response.status_code == 200:
                temp_file.write(image_response.content)
                temp_file.close()  # Make sure the file is closed before passing the path
                
                # Pass the image path to the analyze_image function
                data['image_analysis'] = analyze_image(temp_file.name)
            else:
                data['image_analysis'] = "Failed to download image."

    return JsonResponse(data)
