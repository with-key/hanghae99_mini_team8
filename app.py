from flask import Flask, render_template

app = Flask(__name__)


#############################
###       router          ###
#############################


@app.route("/")
def main_page():
    return render_template("home.html")


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
    # 로그인
    return "로그인 성공 or 로그인 실패 반환"


@app.route("/signup/check_dup", methods=["POST"])
def check_dup():
    # 회원가입시 아이디 중복 체크
    return "아이디가 중복시 success 반환"


if __name__ == "__main__":
    app.run(host="0.0.0.0")  # ㅜㅜ
    app.run(debug=True)  # debug mode on, 사용하면 server restart 불필요
