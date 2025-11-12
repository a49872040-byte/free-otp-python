from flask import Flask, request, render_template_string
import random
import requests
import time

app = Flask(__name__)

# মেমরিতে OTP স্টোর (প্রোডাকশনে Redis/DB ব্যবহার করো)
otp_storage = {}

# ফ্রি SMS পাঠানোর ফাংশন (Textbelt - প্রতিদিন ১টা ফ্রি)
def send_otp_free(phone, otp):
    url = "https://textbelt.com/text"
    data = {
        'phone': phone,
        'message': f'Your OTP is {otp}. Valid for 5 minutes.',
        'key': 'textbelt'
    }
    try:
        response = requests.post(url, data=data)
        return response.json()
    except:
        return {"success": False}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        phone = request.form['phone']
        
        if phone.startswith('0'):
            phone = '+88' + phone
        elif not phone.startswith('+'):
            phone = '+880' + phone.lstrip('0')
            
        otp = random.randint(100000, 999999)
        otp_storage[phone] = {'otp': otp, 'time': time.time()}
        
        result = send_otp_free(phone, otp)
        
        if result.get('success'):
            return f"SMS sent to {phone}! Check your phone.<br><a href='/verify'>Go to Verify</a>"
        else:
            return f"Free quota over today or error. Try tomorrow! Error: {result}"
    
    return render_template_string('''
    <h2>ফ্রি OTP ভেরিফিকেশন সিস্টেম</h2>
    <form method="post">
        <input type="text" name="phone" placeholder="017xxxxxxxxxx" required style="width:200px;padding:10px;font-size:18px;">
        <button type="submit" style="padding:10px 20px;font-size:18px;">Send OTP</button>
    </form>
    <p><small>প্রতিদিন ১টা ফ্রি SMS। শুধু টেস্টের জন্য।</small></p>
    ''')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        phone = request.form['phone']
        user_otp = request.form['otp']
        
        if phone in otp_storage:
            stored = otp_storage[phone]
            if time.time() - stored['time'] > 300:
                del otp_storage[phone]
                return "OTP expired! Request new one."
            if str(stored['otp']) == user_otp:
                del otp_storage[phone]
                return "<h3 style='color:green'>✅ সফলভাবে ভেরিফাইড!</h3>"
            else:
                return "ভুল OTP!"
        else:
            return "কোনো OTP পাঠানো হয়নি!"
    
    return render_template_string('''
    <h2>OTP ভেরিফাই করো</h2>
    <form method="post">
        <input type="text" name="phone" placeholder="ফোন নম্বর" required><br><br>
        <input type="text" name="otp" placeholder="OTP দাও" required><br><br>
        <button type="submit">ভেরিফাই</button>
    </form>
    <br><a href='/'>নতুন OTP নাও</a>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
