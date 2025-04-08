# main.py

import requests
import time
import schedule
from datetime import datetime
from config import OPENAI_API_KEY


# === НАСТРОЙКИ ===
WB_API_TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1OTg2MTcwNCwiaWQiOiIwMTk2MTQxNS1mMGRmLTczNjAtYTljNS04MDhhYzIzZGVhMTciLCJpaWQiOjUyMzMzMTczLCJvaWQiOjEzMTM1MSwicyI6MTI4LCJzaWQiOiJkZWIyM2I2Yy1lZDhmLTQwMDUtODNiZS1mYzg0MGU0ZTZkNjYiLCJ0IjpmYWxzZSwidWlkIjo1MjMzMzE3M30.kr0tPwZ0VbhHqU8G-NqrWdpN4CJmkMJFSd5PrUgMenDo1ERMXoJFpoKPRcDaOnfcfrwZgi2bDQk8ObtwBWmg6w"

client = OpenAI(api_key=OPENAI_API_KEY)

# === ПОЛУЧЕНИЕ НЕОТВЕЧЕННЫХ ОТЗЫВОВ ===
def get_feedbacks():
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
    headers = {"Authorization": WB_API_TOKEN}
    params = {"isAnswered": False, "take": 30, "skip": 0}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    return res.json().get("data", {}).get("feedbacks", [])

# === ИИ-ГЕНЕРАЦИЯ ОТВЕТА ===
def generate_ai_reply(rating, text, username):
    prompt = f"""
    Составь вежливый и индивидуальный ответ на отзыв покупателя о товаре на маркетплейсе.
    Оценка: {rating}/5
    Имя покупателя: {username}
    Отзыв: "{text if text else 'без текста'}"

    Ответ должен начинаться с "Здравствуйте!" и заканчиваться "Приятных Вам покупок!".
    Не пиши шаблон, а постарайся сделать его живым, как будто пишет человек.
    Тональность и стиль подбирай по настроению отзыва и оценке.
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=300
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("Ошибка генерации ответа:", e)
        return "Здравствуйте! Спасибо за вашу оценку. Приятных Вам покупок!"

# === ОТПРАВКА ОТВЕТА НА ОТЗЫВ ===
def send_reply(feedback_id, text):
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer"
    headers = {"Authorization": WB_API_TOKEN, "Content-Type": "application/json"}
    payload = {"id": feedback_id, "text": text}
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code == 204

# === ОБРАБОТКА ОТЗЫВОВ ===
def process_feedbacks():
    feedbacks = get_feedbacks()
    for fb in feedbacks:
        fid = fb["id"]
        rating = fb.get("productValuation", 0)
        text = fb.get("text", "").strip()
        username = fb.get("userName", "Покупатель")

        reply = generate_ai_reply(rating, text, username)
        success = send_reply(fid, reply)

        print(f"{'✅' if success else '❌'} Ответ {'отправлен' if success else 'не отправлен'} на отзыв {fid}.")
        time.sleep(2)

# === ЗАПУСК ===
def main():
    print("Автоответ бот запущен. Работаем каждые 10 минут...")
    process_feedbacks()  # Сразу запускаем первую обработку
    schedule.every(10).minutes.do(process_feedbacks)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
