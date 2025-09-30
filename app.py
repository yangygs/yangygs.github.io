from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import timedelta
import random
import os

from qqeamil import send_mail
from sql import opensql

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

def get_random_file(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    if file_paths:
        return random.choice(file_paths)
    else:
        return None

yzm = "aghhssghjajitkjluiawgtfiseauygfaweolifgwgeiehg"
@app.route('/base', methods=[ 'POST'])
def base():
    session.pop("yzm", None)
    session["yzm"] = yzm
    screen = request.get_json()
    session["screen"] = screen
    if screen["width"] > 1200: #pc
        filename = get_random_file("./static/backgroundshow/PC/")
        if "mp4" in filename:
            return {"yzm":yzm,"type":"mp4","file": filename}
        else:
            return {"yzm":yzm,"type":"jpg","file": filename}
    elif screen["width"] <= 800:
        filename = get_random_file("./static/backgroundshow/Phone")
        if "mp4" in filename:
            return {"yzm":yzm,"type":"mp4","file": filename}
        else:
            return {"yzm":yzm,"type":"jpg","file": filename}
    else:
        filename = get_random_file("./static/backgroundshow/Pad")
        if "mp4" in filename:
            return {"yzm":yzm,"type":"mp4","file": filename}
        else:
            return {"yzm":yzm,"type":"jpg","file": filename}

@app.route('/')
def index():
    username = session.get('username')
    if username == "yangygs":
        return redirect(url_for('home'))
    else:

        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")
@app.route('/tologin',methods=["POST"])
def tologin():
    username = request.get_json()['username']
    password = request.get_json()['password']
    yzm = request.get_json()['yzm']
    if session.get("yzm") == yzm:
        with opensql("Users.db") as sql:
            try:
                result = sql("SELECT user, password FROM usernamepassword WHERE user='{}' and password='{}'".format(username, password))[0]
                if username == result[0] and password == result[1]:
                    print(result)
                    session.clear()
                    session["username"] = username
                    session["password"] = password
                    return {"status": "success"}
                else:
                    return {"status": "failure", "reson": "账号密码错误"}
            except IndexError:
                return {"status": "failure", "reson": "账号密码错误"}
    else:

        return {"status":"failure","reson":"因某种原因登录失败，请重试"}

@app.route('/toregister',methods=["POST"])
def toregister():
    data = request.get_json()
    username = data.get('username')
    password1 = data.get('password1')
    password2 = data.get('password2')
    phoneemail = data.get('phoneemail')
    captcha = data.get('captcha')
    print(data)
    if username == "yangygs":
        return {"status":"success"}
    else:
        return {"status":"failure","message":"因某种原因注册失败，请重试"}

@app.route('/home',methods=["GET","POST"])
def home():
    return render_template("index.html")

@app.route('/seedcaptcha',methods=["POST"])
def seedcaptcha():
    data = request.get_json()
    if data["seedtype"] == "email":
        yzm1 = random.randint(100000,999999)
        print(yzm1)
        r = send_mail(data["phoneemail"], data["username"], "您的验证码是: {}".format(yzm1))
        if r:
            session["yzm"] = yzm
            return {"status":"success"}
        else:
            return {"status": "failure"}
    elif data["seedtype"] == "phone":
        return {"status": "failure"}
    else:
        return {"status": "failure"}




if __name__ == '__main__':

    app.run(host='0.0.0.0')
