import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")

def hf_generate(model, prompt, max_tokens=500):
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens}
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    return data[0]["generated_text"]
