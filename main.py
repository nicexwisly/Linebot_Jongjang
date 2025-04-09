
from flask import Flask, request, jsonify
import pandas as pd
import json
import requests

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "YEECvUaqmXwCfMq2iFPTrzctFgj/BBMLcalaHei2myZT+9mOheNn8QFzwNPA6zvWrD/F5BSXgZ7noMupqPXgTzetpUAswQ3as+BY2Az/GYE3JCKAMhlhc3ayOvk/tW7tiwDS/9RYz12PKOZ9z4nTBwdB04t89/1O/w1cDnyilFU="

json_data = []

@app.route("/api/upload-json", methods=["POST"])
def upload_json():
    global json_data
    try:
        json_data = request.get_json()
        print("📥 ได้รับ JSON แล้ว:", len(json_data), "รายการ")
        return jsonify({"status": "success", "message": f"รับข้อมูลแล้ว {len(json_data)} รายการ"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def search_product(keyword):
    results = [row for row in json_data if keyword in row.get("สินค้า", "")]
    if not results:
        return "ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"
    row = results[0]
    return f"พบแล้วค่ะ: {row['ไอเท็ม']} | {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"

def reply_to_line(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": message}
        ]
    }
    res = requests.post(url, headers=headers, json=body)
    print("📤 ตอบกลับ:", res.status_code, res.text)

@app.route("/callback", methods=["POST"])
def callback():
    body = request.json
    try:
        events = body.get("events", [])
        for event in events:
            if event.get("type") == "message" and event["message"]["type"] == "text":
                user_msg = event["message"]["text"]
                reply_token = event["replyToken"]
                if user_msg.startswith("สินค้า:"):
                    keyword = user_msg.replace("สินค้า:", "").strip()
                    answer = search_product(keyword)
                else:
                    answer = "กรุณาพิมพ์ว่า สินค้า: ตามด้วยชื่อสินค้าที่ต้องการค้นหา"
                reply_to_line(reply_token, answer)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "ระบบพร้อมทำงานแล้ว!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
