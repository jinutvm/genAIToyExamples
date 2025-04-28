# Running a local model in my machine - Macbook Air M1 chip with only 8GB Ram
# Ran only llama3.2 version just 2GB model
# To pull llama3 - ollama pull llama3
# Identify the list of implementations - ollama list

import requests

def ask_llama3(question, model="llama3.2:latest"):
    """Send a prompt to Ollama and get a response from Llama 3."""
    url = 'http://localhost:11434/api/generate'
    
    payload = {
        'model': model,
        'prompt': question,
        'stream': False
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
    question = "Explain the theory of relativity in simple words."
    answer = ask_llama3(question)
    print(f"Llama 3 Answer: {answer}")