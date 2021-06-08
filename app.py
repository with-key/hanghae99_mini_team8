from flask import Flask

app = Flask(__name__)


@app.route('/')
def main_page():
	return '메인페이지 랜딩'

@app.route('/login', methods=['POST'])
def login():
	#로그인
	return '로그인 성공 or 로그인 실패 반환'



if __name__ == '__main__':
	app.run()
