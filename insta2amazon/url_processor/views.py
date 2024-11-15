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
import cv2
from torchvision.transforms import Compose, Normalize, Resize, ToTensor
import pytesseract
import numpy as np
import whisper
import moviepy.editor as mp

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#Video Analysis:
# Load MiDaS model for depth estimation
def load_midas_model():
    midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small").eval()
    return midas

# Depth estimation function
def estimate_depth(img, midas, transform):
    img_input = transform(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))).unsqueeze(0)
    with torch.no_grad():
        depth_map = midas(img_input).squeeze().cpu().numpy()
    return depth_map

# Get transform function for MiDaS model
def get_transform():
    return Compose([Resize((384, 384)), ToTensor(), Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])])

# OCR function to extract text from frames
def extract_text_with_ocr(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray_frame)
    return text

# Extract and transcribe audio from video using Whisper
def transcribe_audio_from_video(video_path):
    model = whisper.load_model("base")
    video_clip = mp.VideoFileClip(video_path)
    with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as temp_audio:
        video_clip.audio.write_audiofile(temp_audio.name)
        temp_audio.close()
        result = model.transcribe(temp_audio.name)
        return result["text"]

# Generate Amazon-style product listing
def generate_amazon_listing(captions, transcription, ocr_texts, dimensions):
    title = captions[0] if captions else "Product Title"
    description = f"{title}. {' '.join(captions[1:])}"
    key_features = [f"Dimension Range: {dim[0]:.2f}m to {dim[1]:.2f}m" for dim in dimensions]
    listing = {
        "title": title,
        "description": description,
        "key_features": key_features,
        "additional_text": " ".join(ocr_texts),
        "transcription_summary": transcription[:150] if transcription else "No transcription available"
    }
    return listing

# Main video analysis function
def analyze_video(video_path, analyze_audio=True, frame_interval=2, ocr_interval=2):
    midas = load_midas_model()
    transform = get_transform()
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Load BLIP model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    captions = []
    dimensions = []
    ocr_texts = []

    for i in range(0, frame_count, frame_interval * fps):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break

        # Caption the frame
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        prompt_inputs = processor(image, text="Describe the product in detail.", return_tensors="pt").to(device)
        output = model.generate(**prompt_inputs, max_length=100, num_beams=5, no_repeat_ngram_size=2)
        caption = processor.decode(output[0], skip_special_tokens=True)
        captions.append(caption)

        # Estimate depth for dimension analysis
        depth_map = estimate_depth(frame, midas, transform)
        depth_range = (depth_map.min(), depth_map.max())
        dimensions.append(depth_range)

        # Perform OCR at specific intervals
        if i % (ocr_interval * fps) == 0:
            ocr_text = extract_text_with_ocr(frame)
            if ocr_text:
                ocr_texts.append(ocr_text)

    cap.release()

    # Transcribe audio if enabled
    transcription = transcribe_audio_from_video(video_path) if analyze_audio else None

    # Generate and return the Amazon listing
    listing = generate_amazon_listing(captions, transcription, ocr_texts, dimensions)
    return listing
#-------------------------------------------------------------------------------------------------------

#Image analysis:
# Load BLIP model and processor for image captioning
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
# Set device to CUDA if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Function to analyze image using BLIP model
def analyze_image(image_path):
    try:
        # Open the image from the file path
        image = Image.open(image_path)
        inputs = processor(image, return_tensors="pt").to(device)

        prompts = [
            "What colors?",
            "Describe the object visible in the image.",
            "Describe color of every part of the object",
            "Is the object of any brand?",
            "Provide a detailed description of the setting or background.",
            "What size?"
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
#----------------------------------------------------------------------------------------------------------

#Content Extraction:
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
            "video_url": post.video_url,
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
        audio_url = soup.find('meta', property='og:audio')
        video_url = soup.find('meta', property='og:video')
        # 
        video_url = video_url['content'] if video_url else None

        # Fallback: Look for JSON data in a script tag if video URL not found
        if not video_url:
            script_tag = soup.find('script', text=lambda t: t and 'window._sharedData' in t)
            if script_tag:
                json_data = script_tag.string.split(' = ', 1)[1].rstrip(';')
                data = json.loads(json_data)
                video_url = data['entry_data']['PostPage'][0]['graphql']['shortcode_media'].get('video_url')

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
# -----------------------------------------------------------------------------------------------------------------

# Django view to process the URL
def process_url(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    data = fetch_content_from_url(url)
    if 'error' in data:
        return JsonResponse({'error': data['error']}, status=400)
    
    # If video content is found, analyze it
    if 'video_url' in data and data['video_url']:
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                video_response = requests.get(data['video_url'], stream=True)
                video_response.raise_for_status()  # Raise error for failed download
                temp_file.write(video_response.content)
                temp_file.close()  # Close file before analysis
                
                # Pass the video path to the analyze_video function
                data['video_analysis'] = analyze_video(temp_file.name, analyze_audio=True)
        except requests.exceptions.RequestException as e:
            data['video_analysis'] = f"Failed to download or analyze video: {str(e)}"
    else:
        data['video_analysis'] = "No video URL found in the provided content."

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
