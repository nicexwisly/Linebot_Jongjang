
from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# path ของไฟล์ Excel ที่อยู่ใน Render
FILE_NAME = "data.xlsx"
FILE_PATH = os.path.join(os.getcwd(), FILE_NAME)

# ฟังก์ชันค้นหาสินค้า
def search_product(keyword):
    try:
        df = pd.read_excel(FILE_PATH, skiprows=9, usecols="E,F,I,J")
        df.columns = ["ไอเท็ม", "สินค้า", "ราคา", "มี Stock อยู่ที่"]
    except FileNotFoundError:
        return "❌ ไม่พบไฟล์ข้อมูล กรุณาอัปโหลดไฟล์ก่อน"
    except Exception as e:
        return f"⚠️ เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}"
    
    result = df[df["สินค้า"].str.contains(keyword, case=False, na=False)]
    if result.empty:
        return "❌ ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"
    row = result.iloc[0]
    return f"พบแล้วจ้า: {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"

# endpoint สำหรับ webhook จาก LINE
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
                    return jsonify({"status": "ok", "reply": answer})
                return jsonify({"status": "ignored"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# endpoint สำหรับอัปโหลดไฟล์ Excel
@app.route("/api/upload-file", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "fail", "message": "ไม่พบไฟล์ในคำขอ"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "fail", "message": "ชื่อไฟล์ว่าง"}), 400

    try:
        file.save(FILE_PATH)
        return jsonify({"status": "success", "message": f"อัปโหลดไฟล์ {FILE_NAME} สำเร็จ!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ตรวจสอบระบบ
@app.route("/", methods=["GET"])
def home():
    return "ระบบพร้อมทำงานแล้ว!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
