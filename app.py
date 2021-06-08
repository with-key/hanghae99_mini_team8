from pymongo import MongoClient
import jwt
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

client = MongoClient("54.180.31.166", 27017, username="test", password="test")
db = client.first_mini_project

SECRET_KEY = "honeyshare"


#############################
###       router          ###
#############################


@app.route("/")
def main_page():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template("home.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page", msg="로그인 정보가 존재하지 않습니다."))


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
    id_receive = request.form["id"]
    pw_receive = request.form["pw"]
    name_receive = request.form["name"]
    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()
    doc = {
        "userid": id_receive,  # 아이디
        "password": pw_hash,  # 비밀번호
        "username": name_receive,  # 사용자 이름
    }
    db.users.insert_one(doc)
    return jsonify({"result": "success"})


@app.route("/login", methods=["POST"])
def login():
    # 로그인
    id_receive = request.form["id_give"]
    pw_receive = request.form["password_give"]

    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one({"userid": id_receive, "password": pw_hash})
    if result is not None:
        payload = {
            "id": id_receive,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"result": "success", "token": token})
    # 찾지 못하면
    else:
        return jsonify({"result": "fail", "msg": "아이디/비밀번호가 일치하지 않습니다."})


@app.route("/signup/check_dup", methods=["POST"])
def check_dup():
    id_receive = request.form["id"]
    exists = bool(db.users.find_one({"userid": id_receive}))
    return jsonify({"result": "success", "exists": exists})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
