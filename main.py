from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)
CHANNEL_ACCESS_TOKEN = "spdlar4aOXRzhHf+XTwS3ZOC+Ya6KsET864BZwnAJPlJZspkRCoYpVWFNLmowSPQlANaXWCgmU8JpDx6asksVn5768f8j150oksJA84zBOdWV/3jWPpgbCb89RT2I0fTWSyAMnJ1HF5vQokPCrkbQdB04t89/1O/w1cDnyilFU="

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
    global json_data
    print("🔍 keyword ที่ค้นหา:", keyword)
    print("📊 จำนวนข้อมูลทั้งหมด:", len(json_data))

    results = [row for row in json_data if keyword in row.get("สินค้า", "")]
    print("✅ เจอสินค้าตรงกับ keyword:", len(results))

    if not results:
        return "ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"

    row = results[0]
    print("📦 รายการแรก:", row)

    try:
        return f"พบแล้วค่ะ: {row['ไอเท็ม']} | {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"
    except Exception as e:
        return f"⚠️ พบข้อมูลแล้วแต่มีข้อผิดพลาด: {str(e)}"

def reply_to_line(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post(url, headers=headers, json=payload)
    print("📤 ส่งข้อความกลับ:", res.status_code, res.text)

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