from flask import Flask, request, jsonify
import pyrebase
import os

app = Flask(__name__)

# 🌟 ใส่ Firebase Config ของบอสให้ครบถ้วนนะครับ
firebaseConfig = {
    "apiKey": "AIzaSyDgM6eehnIpIFZ20ZJdvoIvrQEmGklareM",
    "authDomain": "vmax-titan-5d42d.firebaseapp.com",
    "databaseURL": "https://vmax-titan-5d42d-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "vmax-titan-5d42d",
    "storageBucket": "vmax-titan-5d42d.firebasestorage.app",
    "messagingSenderId": "803523967441",
    "appId": "1:803523967441:web:6da9fa4cd4b3bb6d0048f0"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

PKG_COINS = {
    "1_DAY": 150,
    "7_DAYS": 1200,
    "15_DAYS": 3000,
    "30_DAYS": 7000
}

@app.route('/plisio-webhook', methods=['POST'])
def plisio_webhook():
    # 🌟 FIX: สั่งให้รองรับทั้ง JSON และ Form Data จาก Plisio
    data = request.json or request.form.to_dict()
    
    if not data:
        print("❌ Webhook Error: ไม่พบข้อมูลส่งมา")
        return "No data", 400

    print("🔔 มีข้อความเข้าจาก Plisio! Status:", data.get('status'))

    status = data.get('status')
    if status in ['completed', 'mismatch']:
        order_number = data.get('order_number', '')
        parts = order_number.split('_')
        
        if len(parts) >= 3:
            uid = parts[0]
            pkg_type = f"{parts[1]}_{parts[2]}" 
            
            coins_to_add = PKG_COINS.get(pkg_type, 0)
            
            if coins_to_add > 0:
                user_ref = db.child("users").child(uid)
                current_data = user_ref.get().val()
                
                if current_data:
                    current_coins = current_data.get("coins", 0)
                    new_coins = current_coins + coins_to_add
                    user_ref.update({"coins": new_coins})
                    print(f"✅ SUCCESS: เติม {coins_to_add} เหรียญ ให้ UID: {uid} เรียบร้อย!")
                    
    return jsonify({"status": "received"}), 200

@app.route('/', methods=['GET'])
def home():
    return "V.MAX Webhook Server is Running 🟢", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
