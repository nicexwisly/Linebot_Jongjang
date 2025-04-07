from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

FILE_NAME = "data.xlsx"

# ตรวจสอบว่าไฟล์มีอยู่ก่อนพยายามอ่าน
if os.path.exists(FILE_NAME):
    df = pd.read_excel(FILE_NAME, skiprows=9, usecols="E,F,I,J")
    df.columns = ["ไอเท็ม", "สินค้า", "ราคา", "มี Stock อยู่ที่"]
else:
    df = pd.DataFrame(columns=["ไอเท็ม", "สินค้า", "ราคา", "มี Stock อยู่ที่"])

def search_product(keyword):
    result = df[df["สินค้า"].str.contains(keyword, case=False, na=False)]
    if result.empty:
        return "ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"
    row = result.iloc[0]
    return f"พบแล้วจ้ะ: {row['ไอเท็ม']} {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"

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
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "ระบบพร้อมทำงานแล้ว!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)