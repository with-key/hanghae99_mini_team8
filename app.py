from pymongo import MongoClient
import jwt
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)

client = MongoClient('54.180.31.166/', 27017, username="test", password="test")
db = client.first_mini_project

SECRET_KEY = 'honeyshare'


#############################
###       router          ###
#############################


@app.route('/')
def main_page():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template("home.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/signup_page")
def signup_page():
    return render_template("sign_up.html")


#############################
###        API            ###
#############################


@app.route("/signup", methods=["POST"])
def signup():
    # 회원가입
    return "회원정보 DB에 저장후 jsonify에 success 반환"


@app.route("/login", methods=["POST"])
def login():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})
    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route("/signup/check_dup", methods=["POST"])
def check_dup():
    # 회원가입시 아이디 중복 체크
    return "아이디가 중복시 success 반환"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
