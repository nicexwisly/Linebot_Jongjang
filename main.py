from flask import Flask, request, jsonify
import pandas as pd
import os
import requests
from datetime import datetime

app = Flask(__name__)

FILE_NAME = "data.xlsx"
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN") or "9spdlar4aOXRzhHf+XTwS3ZOC+Ya6KsET864BZwnAJPlJZspkRCoYpVWFNLmowSPQlANaXWCgmU8JpDx6asksVn5768f8j150oksJA84zBOdWV/3jWPpgbCb89RT2I0fTWSyAMnJ1HF5vQokPCrkbQdB04t89/1O/w1cDnyilFU="

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

@app.route("/api/upload-file", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "fail", "message": "ไม่พบไฟล์ในคำขอ"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "fail", "message": "ชื่อไฟล์ว่าง"}), 400
    try:
        file.save(FILE_NAME)
        return jsonify({"status": "success", "message": f"อัปโหลดไฟล์ {FILE_NAME} สำเร็จ!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def search_product(keyword):
    global json_data
    print(f"[DEBUG] keyword ที่รับมา: {keyword}")
    print(f"[DEBUG] จำนวน json_data ทั้งหมด: {len(json_data)}")

    if not json_data:
        return "❌ ยังไม่มีข้อมูลสินค้า กรุณาอัปโหลดไฟล์ก่อน"

    results = [row for row in json_data if keyword in str(row.get("สินค้า", ""))]
    print(f"[DEBUG] พบ {len(results)} รายการที่ match กับ keyword")

    if not results:
        return "❌ ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"

    row = results[0]
    print(f"[DEBUG] รายการที่เจอ:", row)

    try:
        return f"{row.get('ไอเท็ม')} {row.get('สินค้า')} ราคา {row.get('ราคา')} บาท เหลือ {row.get('มี Stock อยู่ที่')} ชิ้น"
    except Exception as e:
        return f"⚠️ เกิดข้อผิดพลาดในการอ่านข้อมูล: {str(e)}"

@app.route("/callback", methods=["POST"])
def callback():
    body = request.json
    try:
        print("📥 body:", body)
        events = body.get("events", [])
        for event in events:
            if event.get("type") == "message" and event["message"]["type"] == "text":
                user_msg = event["message"]["text"]
                reply_token = event["replyToken"]
                print("👤 user_msg:", user_msg)

                if user_msg.startswith("@@"):
                    keyword = user_msg.replace("@@", "").strip()
                    answer = search_product(keyword)
                else:
                    answer = "กรุณาพิมพ์ว่า @@ ตามด้วยชื่อสินค้าที่ต้องการค้นหา"

                reply_to_line(reply_token, answer)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()  # ✅ พิมพ์ error แบบละเอียด
        return jsonify({"error": str(e)}), 500
    
json_data = []  # ตัวแปรสำหรับเก็บ JSON ที่ upload เข้ามา

@app.route("/api/upload-json", methods=["POST"])
def upload_json():
    global json_data
    try:
        json_data = request.get_json()
        print("✅ ได้รับ JSON แล้ว:", len(json_data), "รายการ")
        return jsonify({"status": "success"})
    except Exception as e:
        print("ERROR:", str(e)) 
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    user_agent = request.headers.get("User-Agent", "")
    if "UptimeRobot" in user_agent:
        print("📡 ตรวจพบการ Ping จาก UptimeRobot")
        return "Ping จาก UptimeRobot", 200
    return "ระบบพร้อมทำงานแล้ว!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)  # ✅ debug=Truez   