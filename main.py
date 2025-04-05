from flask import Flask, request, jsonify, render_template_string
import openai
import pandas as pd
import os
import requests

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

df = pd.read_excel("data.xlsx")

def search_product(keyword):
    result = df[df["ชื่อสินค้า"].str.lower().str.contains(keyword.lower().strip(), na=False)]
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
                if user_msg.startswith("สินค้า:") or user_msg.startswith("@บอท") or user_msg.startswith("ถาม:"):
                    keyword = user_msg.split(":", 1)[1].strip()
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
    requests.post("https://api.line.me/v2/bot/message/reply", json=payload, headers=headers)

@app.route("/", methods=["GET"])
def index():
    return "LINE Stock Bot is running!"

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            return "ไม่พบไฟล์ที่อัปโหลด", 400
        file = request.files['file']
        if file.filename == '':
            return "กรุณาเลือกไฟล์", 400
        if file and file.filename.endswith('.xlsx'):
            file.save("data.xlsx")
            global df
            df = pd.read_excel("data.xlsx")
            return "✅ อัปโหลดข้อมูลใหม่สำเร็จ!"
        else:
            return "กรุณาอัปโหลดเฉพาะไฟล์ .xlsx", 400

    html_form = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>อัปโหลด Stock Excel</title>
    </head>
    <body>
        <h2>📤 อัปโหลดไฟล์ Stock ใหม่ (.xlsx)</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xlsx" required>
            <button type="submit">อัปโหลด</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html_form)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

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

            # อ่านข้อมูลจากแถวที่ 10 (skiprows=9), คอลัมน์ E, F, I, J
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
                return f"เกิดข้อผิดพลาดขณะอ่านไฟล์: {str(e)}", 500

        else:
            return "กรุณาอัปโหลดเฉพาะไฟล์ .xlsx", 400
        
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

    # HTML ฟอร์ม
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

