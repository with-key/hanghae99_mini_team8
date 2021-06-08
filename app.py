from flask import Flask

app = Flask(__name__)


@app.route('/')
def main_page():
	return '메인페이지 랜딩'


if __name__ == '__main__':
	app.run()
