from flask import Flask, request, jsonify
import pyrebase
import os
import sys

app = Flask(__name__)

# 🌟 Firebase Config ของบอส
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

@app.route('/plisio-webhook', methods=['POST', 'GET'])
def plisio_webhook():
    try:
        data = request.get_json(silent=True) or request.form.to_dict() or request.args.to_dict()
        
        print(f"\n[🚨 WEBHOOK TRIGGERED] Data: {data}\n", flush=True)

        if not data:
            return jsonify({"error": "No data"}), 400

        status = data.get('status')
        order_number = data.get('order_number', '')

        if status in ['completed', 'mismatch']:
            print(f"[✅ PAYMENT COMPLETED] Order: {order_number}", flush=True)
            parts = order_number.split('_')
            
            if len(parts) >= 3:
                uid = parts[0]
                pkg_type = f"{parts[1]}_{parts[2]}" 
                coins_to_add = PKG_COINS.get(pkg_type, 0)
                
                if coins_to_add > 0:
                    # 🌟 ระบบล็อกเป้าหมาย ยิงเหรียญเข้ายูสเซอร์ตรงๆ ไม่ตกหล่นที่หน้าบ้าน
                    current_data = db.child("users").child(uid).get().val()
                    current_coins = current_data.get("coins", 0) if current_data else 0
                    new_coins = current_coins + coins_to_add
                    
                    db.child("users").child(uid).update({"coins": new_coins})
                    
                    print(f"[🎉 SUCCESS] บวก {coins_to_add} เหรียญ ให้ {uid} | ยอดใหม่: {new_coins}", flush=True)
                else:
                    print(f"[❌ ERROR] ไม่รู้จักแพ็กเกจ {pkg_type}", flush=True)
            else:
                print(f"[❌ ERROR] โครงสร้าง Order พัง: {order_number}", flush=True)
        else:
            print(f"[⚠️ PENDING/OTHER] Status: {status} | Order: {order_number}", flush=True)

        return jsonify({"status": "received"}), 200
    except Exception as e:
        print(f"[🔥 FATAL ERROR] ระบบพัง: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "V.MAX Webhook Server is Running 🟢", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
