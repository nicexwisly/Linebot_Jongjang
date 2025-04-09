from flask import Flask, request, jsonify
import pandas as pd
import os
import requests

app = Flask(__name__)

FILE_NAME = "data.xlsx"
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN") or "9spdlar4aOXRzhHf+XTwS3ZOC+Ya6KsET864BZwnAJPlJZspkRCoYpVWFNLmowSPQlANaXWCgmU8JpDx6asksVn5768f8j150oksJA84zBOdWV/3jWPpgbCb89RT2I0fTWSyAMnJ1HF5vQokPCrkbQdB04t89/1O/w1cDnyilFU="

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
                    answer = f"คุณค้นหาสินค้า: {keyword}"
                else:
                    answer = "กรุณาพิมพ์ว่า สินค้า: ตามด้วยชื่อสินค้าที่ต้องการค้นหา"
                print("✅ ตอบกลับ:", answer)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/upload-json", methods=["POST"])
def upload_json_file():
    try:
        data = request.get_json()
        with open("data_ready.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "success", "message": "อัปโหลด JSON สำเร็จ!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def search_product(keyword):
    try:
        df = pd.read_excel(FILE_NAME, skiprows=9, usecols="E,F,I,J")
        df.columns = ["ไอเท็ม", "สินค้า", "ราคา", "มี Stock อยู่ที่"]
    except FileNotFoundError:
        return "❌ ไม่พบไฟล์ข้อมูล กรุณาอัปโหลดไฟล์ก่อน"
    result = df[df["สินค้า"].str.contains(keyword, case=False, na=False)]
    if result.empty:
        return "❌ ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"
    row = result.iloc[0]
    return f"พบแล้วค่ะ: {row['ไอเท็ม']} {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"

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