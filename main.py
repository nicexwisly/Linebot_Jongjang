from flask import Flask, request, jsonify
import pandas as pd
import json
import os
import requests

app = Flask(__name__)

FILE_NAME = "data.xlsx"
JSON_FILE_NAME = "data_ready.json"
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN") or "9spdlar4aOXRzhHf+XTwS3ZOC+Ya6KsET864BZwnAJPlJZspkRCoYpVWFNLmowSPQlANaXWCgmU8JpDx6asksVn5768f8j150oksJA84zBOdWV/3jWPpgbCb89RT2I0fTWSyAMnJ1HF5vQokPCrkbQdB04t89/1O/w1cDnyilFU=นี่"

# ===== ส่งข้อความกลับ LINE =====
def reply_to_line(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    r = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
    print("LINE API response:", r.status_code, r.text)

# ===== อัปโหลด Excel แบบเดิม =====
@app.route("/api/upload-file", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "fail", "message": "ไม่พบไฟล์"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "fail", "message": "ชื่อไฟล์ว่าง"}), 400
    try:
        file.save(FILE_NAME)
        return jsonify({"status": "success", "message": f"อัปโหลดไฟล์ {FILE_NAME} สำเร็จ!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== อัปโหลด JSON แบบใหม่ =====
@app.route("/api/upload-json", methods=["POST"])
def upload_json():
    try:
        data = request.get_json()
        with open(JSON_FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "success", "message": "อัปโหลด JSON สำเร็จ!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== ค้นหาข้อมูลจาก JSON =====
def search_product(keyword):
    if not os.path.exists(JSON_FILE_NAME):
        return "❌ ไม่พบไฟล์ข้อมูล กรุณาอัปโหลดก่อน"
    with open(JSON_FILE_NAME, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        if keyword in item["สินค้า"]:
            return f"พบแล้วค่ะ: {item['ไอเท็ม']} {item['สินค้า']} ราคา {item['ราคา']} บาท เหลือ {item['มี Stock อยู่ที่']} ชิ้น"
    return "❌ ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"

# ===== Webhook LINE Bot =====
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