
from flask import Flask, request, jsonify
import openai
import pandas as pd
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

# โหลดข้อมูลสินค้าจาก Excel
df = pd.read_excel("data.xlsx")

def search_product(keyword):
    result = df[df["ชื่อสินค้า"].str.contains(keyword, case=False, na=False)]
    if result.empty:
        return "ขออภัยค่ะ ไม่พบสินค้าที่ค้นหาในระบบ"
    row = result.iloc[0]
    return f"พบแล้วค่ะ: {row['ชื่อสินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['คงเหลือ']} ชิ้น"

@app.route("/callback", methods=["POST"])
def callback():
    body = request.json
    try:
        events = body["events"]
        for event in events:
            if event["type"] == "message" and event["message"]["type"] == "text":
                user_msg = event["message"]["text"]
                reply_token = event["replyToken"]
                if user_msg.startswith("สินค้า:"):
                    keyword = user_msg.split(":", 1)[1].strip()
                    answer = search_product(keyword)
                    reply_to_line(reply_token, answer)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import requests
def reply_to_line(reply_token, msg):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": msg}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", json=payload, headers=headers)

@app.route("/", methods=["GET"])
def index():
    return "LINE Stock Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

