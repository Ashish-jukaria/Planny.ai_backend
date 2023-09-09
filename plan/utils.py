import requests
import os

def generate_gpt_response(prompt_text):

    openai_api_key = os.environ.get("OPENAI_API_KEY")  # Access the environment variable

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",  # Use the chat completions endpoint
        headers={"Authorization": f"Bearer {openai_api_key}"},
        json={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text}
            ],
            "model": "gpt-3.5-turbo"  # Specify the model parameter
        },
    )
    data = response.json()

    if "choices" in data:
        completion_text = data["choices"][0]["message"]["content"]
        return completion_text
    else:
        return None




