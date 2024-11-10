# !pip install torch --upgrade  # Upgrade to the latest PyTorch version
# !pip install transformers==4.30.2
# !pip install autoawq

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Set device to GPU if available, otherwise CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the tokenizer and model (quantized LLaMA-2 4-bit model)
tokenizer = AutoTokenizer.from_pretrained("jamesdborin/llama2-7b-chat-4bit-AWQ")
model = AutoModelForCausalLM.from_pretrained("jamesdborin/llama2-7b-chat-4bit-AWQ").to(device)

# Data for product description
extracted_data = {
    'image_keywords': "smart fitness tracker, heart rate monitor, wearable technology",
    'video_descriptions': "Demonstration of fitness tracker usage, highlighting heart rate and sleep tracking features.",
    'audio_text': "Narration explaining the benefits of personalized fitness goals and health monitoring.",
    'caption_summary': "Stay fit with our new Smart Fitness Tracker! Monitor your heart rate, track your sleep, and achieve your fitness goals easily.",
    'comment_summary': "Waterproof, sleek design, includes step counter."
}

input_prompt = f"""
    Product: Smart Fitness Tracker
    Image Keywords: {extracted_data['image_keywords']}
    Video Descriptions: {extracted_data['video_descriptions']}
    Audio Text: {extracted_data['audio_text']}
    Caption Summary: {extracted_data['caption_summary']}
    Comment Insights: {extracted_data['comment_summary']}

    Generate a detailed product listing with title, description, features, and specifications:
"""

# Tokenize and prepare the input text
input_ids = tokenizer.encode(input_prompt, return_tensors="pt").to(device)

# Generate the product listing
with torch.no_grad():
    output = model.generate(input_ids, max_length=500, num_return_sequences=1, pad_token_id=tokenizer.pad_token_id)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

# Print the generated product listing
print(generated_text)