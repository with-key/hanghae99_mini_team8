from flask import Flask,render_template

app = Flask(__name__)


@app.route('/')
def main_page():
    return render_template('메인페이지 렌딩')


@app.route('/login_page')
def login_page():
    return render_template('로그인페이지 랜딩')


@app.route('/signup_page')
def signup_page():
    return render_template('회원가입 페이지 렌딩')


@app.route('/signup', methods=['POST'])
def signup():
    # 회원가입
    return '회원정보 DB에 저장후 jsonify에 success 반환'


@app.route('/login', methods=['POST'])
def login():
    # 로그인
    return '로그인 성공 or 로그인 실패 반환'


@app.route('/signup/check_dup', methods=['POST'])
def check_dup():
    # 회원가입시 아이디 중복 체크
    return '아이디가 중복시 success 반환'


if __name__ == '__main__':
    app.run()
