
from flask import Flask, request, jsonify
import os
import pandas as pd
import openai
import requests

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# default path
DATA_PATH = "data.xlsx"

def load_data():
    try:
        df = pd.read_excel(DATA_PATH, skiprows=9, usecols="E,F,I,J")
        df.columns = ["ไอเท็ม", "สินค้า", "ราคา", "มี Stock อยู่ที่"]
        return df
    except Exception as e:
        return None

def search_product(keyword):
    df = load_data()
    if df is None:
        return "❌ ไม่สามารถโหลดข้อมูลได้"
    result = df[df["สินค้า"].str.contains(keyword, case=False, na=False)]
    if result.empty:
        return "❌ ไม่พบสินค้าในระบบ"
    row = result.iloc[0]
    return f"พบแล้วค่ะ: {row['ไอเท็ม']} | {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"

@app.route("/", methods=["GET"])
def home():
    return "✅ Server is running!", 200

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
                    keyword = user_msg.replace("สินค้า:", "").strip()
                    answer = search_product(keyword)
                    reply_to_line(reply_token, answer)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def reply_to_line(reply_token, msg):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": msg}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=payload)

@app.route("/upload", methods=["GET"])
def upload_page():
    return """
    <form method="post" action="/api/upload-file" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    """

@app.route("/api/upload-file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "❌ ไม่พบไฟล์"
    file = request.files["file"]
    file.save(DATA_PATH)
    return "✅ อัปโหลดไฟล์เรียบร้อยแล้ว"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
