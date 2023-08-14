import requests

def generate_gpt_response(prompt_text):
    openai_api_key="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"

    response = requests.post(
        "https://api.openai.com/v1/engines/gpt-3.5-turbo/completions",
        headers={"Authorization": f"Bearer {openai_api_key}"},
        json={"prompt": prompt_text, "max_tokens": 50},  # Adjust parameters as needed
    )
    data = response.json()
    
    if "choices" in data:
        completion_text = data["choices"][0]["text"]
        return completion_text
    else:
        return None





