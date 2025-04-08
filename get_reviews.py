# get_reviews.py

import requests
from config import WB_TOKEN_V2

def get_reviews():
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
    headers = {
        "Authorization": WB_TOKEN_V2
    }
    params = {
        "isAnswered": "false",
        "take": 5,
        "skip": 0,
        "order": "dateDesc"
    }

    response = requests.get(url, headers=headers, params=params)
    print("Статус:", response.status_code)
    print("Ответ:", response.json())
