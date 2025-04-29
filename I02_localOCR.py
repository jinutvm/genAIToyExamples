# pulled the information from the bill.
# llama3 is a text only one and hence picked up llava (4GB) model. Wanted to pull gemma3 models, but not too much space available in my machine
# The response is not that satisfactory with llava model, but it is pulling out information.

import requests
import base64

def ask_llava(question, image_path: str, model="llava"):
    """Send a prompt to Ollama and get a response from llava to review the images."""
    url = 'http://localhost:11434/api/generate'

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    payload = {
        'model': model,
        'prompt': question,
        'stream': False,
        'images': [encoded_image]
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        answer = response.json().get('response', '')
        return answer.strip()
    
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return None

if __name__ == "__main__":
    question ="""Analyze the text in the provided image. Extract all readable content
                and present it in a structured Markdown format that is clear, concise, 
                and well-organized. Ensure proper formatting (e.g., headings, lists, or
                code blocks) as necessary to represent the content effectively"""
    image_path = "/users/jinubabu/downloads/bill computer.jpeg"  
    answer = ask_llava(question, image_path=image_path)
    print(f"llava Analysis: {answer}")