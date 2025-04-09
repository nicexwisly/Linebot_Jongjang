
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

LINE_TOKEN = "YOUR_LINE_CHANNEL_ACCESS_TOKEN"  # เปลี่ยนเป็น Token จริง

def search_product(keyword):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for row in data:
            if keyword in row.get("สินค้า", ""):
                return f"พบแล้วค่ะ: {row['ไลน์คี']}, {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"
        return "ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}"

def reply_to_line(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📨 LINE response:", response.status_code, response.text)

@app.route("/callback", methods=["POST"])
def callback():
    body = request.json
    print("📩 ได้รับ webhook:", json.dumps(body, ensure_ascii=False))
    try:
        events = body.get("events", [])
        for event in events:
            if event.get("type") == "message" and event["message"]["type"] == "text":
                user_msg = event["message"]["text"]
                reply_token = event["replyToken"]
                print("👤 ข้อความจากผู้ใช้:", user_msg)
                
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
