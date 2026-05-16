from flask import Flask, request, jsonify
import pyrebase
import os

app = Flask(__name__)

# 🌟 ใส่ Firebase Config ของบอสตรงนี้ให้ครบนะครับ
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
        # 🌟 FIX: ดูดข้อมูลทุกรูปแบบ ไม่ว่า Plisio จะส่งแบบไหนมา
        data = request.get_json(silent=True) or request.form.to_dict() or request.args.to_dict()
        
        print("\n===================================")
        print("🚨 INCOMING WEBHOOK FROM PLISIO 🚨")
        print(f"RAW DATA: {data}")
        print("===================================\n")

        if not data:
            return jsonify({"error": "No data received"}), 400

        status = data.get('status')
        
        if status in ['completed', 'mismatch']:
            order_number = data.get('order_number', '')
            print(f"✅ ตรวจพบการชำระเงินสำเร็จ! Order: {order_number}")
            
            parts = order_number.split('_')
            if len(parts) >= 3:
                uid = parts[0]
                pkg_type = f"{parts[1]}_{parts[2]}" 
                
                coins_to_add = PKG_COINS.get(pkg_type, 0)
                
                if coins_to_add > 0:
                    print(f"⏳ กำลังดึงข้อมูล Firebase เพื่อเติม {coins_to_add} เหรียญ ให้ UID: {uid}...")
                    user_ref = db.child("users").child(uid)
                    current_data = user_ref.get().val()
                    
                    if current_data:
                        current_coins = current_data.get("coins", 0)
                        new_coins = current_coins + coins_to_add
                        user_ref.update({"coins": new_coins})
                        print(f"🎉 SUCCESS: เติมเหรียญเรียบร้อย! ยอดใหม่คือ: {new_coins} V.Coins")
                    else:
                        print(f"❌ ERROR: ไม่พบ UID {uid} ในระบบ Firebase!")
                else:
                    print(f"❌ ERROR: ไม่รู้จักแพ็กเกจ {pkg_type}!")
            else:
                print(f"❌ ERROR: รูปแบบ Order Number พัง ({order_number})")
        else:
            print(f"⚠️ บิลยังไม่สมบูรณ์ สถานะตอนนี้คือ: {status}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"🔥 FATAL ERROR ข้อมูลพังตอนอัปเดต: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "V.MAX Webhook Server is Running 🟢", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
