
from flask import Flask, request, jsonify, render_template_string
import openai
import pandas as pd
import os
import requests

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def index():
    return "LINE Stock Bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    body = request.json
    try:
        events = body["events"]
        for event in events:
            if event["type"] == "message" and event["message"]["type"] == "text":
                user_msg = event["message"]["text"]
                reply_token = event["replyToken"]
                if user_msg.startswith("สินค้า:") or user_msg.startswith("@บอท") or user_msg.startswith("ถาม:"):
                    keyword = user_msg.split(":", 1)[1].strip()
                    df = pd.read_excel("data_ready.xlsx")
                    result = df[df["สินค้า"].str.contains(keyword, case=False, na=False)]
                    if result.empty:
                        answer = "ขออภัย ไม่พบสินค้านี้ค่ะ"
                    else:
                        row = result.iloc[0]
                        answer = f"พบแล้ว: {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"
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
    requests.post("https://api.line.me/v2/bot/message/reply", json=payload, headers=headers)

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            return "ไม่พบไฟล์ที่อัปโหลด", 400
        file = request.files['file']
        if file.filename == '':
            return "กรุณาเลือกไฟล์", 400
        if file and file.filename.endswith('.xlsx'):
            file.save("BU.xlsx")
            try:
                df_raw = pd.read_excel("BU.xlsx", skiprows=9, usecols="E,F,I,J")
                df_ready = df_raw.rename(columns={
                    "ItemNo": "ไอเท็ม",
                    "Description": "สินค้า",
                    "Selling Price": "ราคา",
                    "ASOH": "มี Stock อยู่ที่"
                })
                df_ready.to_excel("data_ready.xlsx", index=False)
                df_ready.to_csv("data_ready.csv", index=False)
                df_ready.to_json("data_ready.json", orient="records", force_ascii=False)
                return "✅ แปลงข้อมูลสำเร็จแล้ว! ได้ทั้ง .xlsx / .csv / .json"
            except Exception as e:
                return f"เกิดข้อผิดพลาด: {str(e)}", 500
        else:
            return "กรุณาอัปโหลดเฉพาะไฟล์ .xlsx", 400

    html_form = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>อัปโหลด Stock Excel</title>
    </head>
    <body>
        <h2>📤 อัปโหลดไฟล์ Stock BU (.xlsx)</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xlsx" required>
            <button type="submit">อัปโหลดและแปลง</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html_form)

@app.route("/api/upload-file", methods=["POST"])
def api_upload_file():
    if 'file' not in request.files:
        return "❌ ไม่พบไฟล์ที่ส่งมา", 400
    file = request.files['file']
    if file.filename.endswith('.xlsx'):
        file.save("BU.xlsx")
        try:
            df_raw = pd.read_excel("BU.xlsx", skiprows=9, usecols="E,F,I,J")
            df_ready = df_raw.rename(columns={
                "ItemNo": "ไอเท็ม",
                "Description": "สินค้า",
                "Selling Price": "ราคา",
                "ASOH": "มี Stock อยู่ที่"
            })
            df_ready.to_excel("data_ready.xlsx", index=False)
            df_ready.to_csv("data_ready.csv", index=False)
            df_ready.to_json("data_ready.json", orient="records", force_ascii=False)
            return "✅ อัปโหลดและแปลงไฟล์สำเร็จ!"
        except Exception as e:
            return f"❌ Error: {str(e)}", 500
    return "❌ รองรับเฉพาะไฟล์ .xlsx", 400
