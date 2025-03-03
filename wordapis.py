import requests
import os

WORDS_API_KEY = os.getenv("96567406bbmshaa4226434acd2afp1d4852jsn0a600bcb52e7")  # Зарегистрируйтесь и получите ключ

def get_random_word():
    url = "https://wordsapiv1.p.rapidapi.com/words/"
    headers = {
        "X-RapidAPI-Key": WORDS_API_KEY,
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params={"random": "true"})
    if response.status_code == 200:
        data = response.json()
        return {
            "word": data["word"],
            "definition": data["results"][0]["definition"]
        }
    return None