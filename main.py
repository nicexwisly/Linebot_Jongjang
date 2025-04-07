from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# อ่านเฉพาะคอลัมน์สำคัญ เริ่มที่แถว 10
df = pd.read_excel("data.xlsx", skiprows=9, usecols="E,F,I,J")
df.columns = ["ไอเท็ม", "สินค้า", "ราคา", "มี Stock อยู่ที่"]

def search_product(keyword):
    result = df[df["สินค้า"].str.contains(keyword, case=False, na=False)]
    if result.empty:
        return "ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"
    row = result.iloc[0]
    return f"พบแล้วค่ะ: {{row['ไอเท็ม']}} {{row['สินค้า']}} ราคา {{row['ราคา']}} บาท เหลือ {{row['มี Stock อยู่ที่']}} ชิ้น"

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

@app.route("/", methods=["GET"])
def home():
    return "ระบบพร้อมทำงานแล้ว!"
