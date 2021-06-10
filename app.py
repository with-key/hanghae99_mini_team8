from pymongo import MongoClient
import jwt
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

client = MongoClient("54.180.31.166", 27017, username="test", password="test")
# client = MongoClient('localhost', 27017)
db = client.first_mini_project

SECRET_KEY = "honeyshare"


#############################
###       router          ###
#############################

@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return redirect(url_for("main"))  # 없는 페이지로 클라에서 요청했을 때 메인으로 보내기


@app.route("/main")
def main():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"userid": payload["id"]})
        posts = list(db.posts.find({}).sort("date", -1))
        ##date값 유효성만 확인되면 date값으로 넣으면 됨
        return render_template("main.html", user_info=user_info, posts=posts)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page"))


@app.route("/<categories>")
def categories(categories):
    token_receive = request.cookies.get("mytoken")
    try:

        if (  # 클라에서 받은 url이 아래 3개 중에 1개에 해당하면, home rendering
                categories == "desk_item"
                or categories == "time_item"
                or categories == "health_item"
        ):

            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"userid": payload["id"]})
            posts = list(db.posts.find({"categories": categories}).sort("date", -1))
            ## date 값 유효성 인증 시 date 값 사용
            return render_template("home.html", user_info=user_info, posts=posts, categories=categories)
        else:  # 클라에서 받은 url이 유효하지 않으면 메인으로 redirect
            return redirect(url_for("main"))

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page"))


@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/signup_page")
def signup_page():
    return render_template("sign_up.html")


@app.route("/register")
def register_page():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_id = payload['id']
        return render_template("register.html", user_id=user_id)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page", msg="로그인 정보가 존재하지 않습니다."))


#############################
###        API            ###
#############################


@app.route("/signup", methods=["POST"])
def signup():
    # 회원가입
    id_receive = request.form["id"]
    id_db = db.users.find_one({"userid":id_receive})
    if id_db is None:

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

    else:
        return jsonify({"result": "fail"})


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


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("userid", None)
    return redirect("/main")


@app.route("/signup/check_dup", methods=["POST"])
def check_dup():
    id_receive = request.form["id"]
    exists = bool(db.users.find_one({"userid": id_receive}))
    return jsonify({"result": "success", "exists": exists})


@app.route("/post", methods=["POST", "GET"])
def posting():
    token_receive = request.cookies.get("mytoken")
    if request.method == "GET":

        # 작성자 id노출
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

            user_id = payload["id"]

            return jsonify({"userid": user_id})
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login"))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login"))

    elif request.method == "POST":
        # 포스팅하기
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

            user_info = db.users.find_one({"username": payload["id"]})

            userid = db.users.find_one({"userid": payload["id"]})

            # 웹에서 오는것
            postname = request.form["postname"]
            categories = request.form["categories"]
            mdurl = request.form["mdurl"]
            grade = request.form["grade"]
            recommendation = request.form["recommendation"]
            honeytip = request.form["honeytip"]
            date = request.form["date"]
            image = ""
            price = ""
            product_name = ""
            # 스크래핑 하는것
            gmarket = "http://item.gmarket.co.kr/"
            naver = "https://shopping.naver.com/"
            naver2 = "https://smartstore.naver.com/"
            naver_lowprice = "https://search.shopping.naver.com/catalog"
            # 좋았던점, 꿀팁 유효성 검사
            if recommendation == "":
                return
            if honeytip == "":
                return

            ##url 유효성 검사

            if gmarket not in mdurl:
                if naver not in mdurl:
                    if naver2 not in mdurl:
                        if naver_lowprice not in mdurl:
                            return jsonify({"msg": "fail"})

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
            }
            data = requests.get(mdurl, headers=headers)
            soup = BeautifulSoup(data.text, "html.parser")
            ##지마켓
            if gmarket in mdurl:
                image = soup.select_one("meta[property='og:image']")["content"]
                price = soup.select_one(
                    "#itemcase_basic > div > p > span > strong"
                ).text
                product_name = soup.select_one(
                    "#itemcase_basic > div.box__item-title > h1"
                ).text
            ##네이벼 쇼핑
            elif naver in mdurl:
                image = soup.select_one("meta[property='og:image']")["content"]
                price = soup.select_one(
                    "#content > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div._1ziwSSdAv8 > "
                    "div.WrkQhIlUY0 > div > strong > span._1LY7DqCnwR"
                ).text
                price = price + "원"
                product_name = soup.select_one(
                    "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div._1ziwSSdAv8 > div.CxNYUPvHfB > h3"
                )
                if product_name is None:
                    product_name = soup.select_one(
                        "#content > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div._1ziwSSdAv8 > div.CxNYUPvHfB > h3"
                    )
                    ##네이버 플레이 윈도
                product_name = product_name.text

            elif naver2 in mdurl:
                image = soup.select_one("meta[property='og:image']")["content"]
                price = soup.select_one(
                    "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div._1ziwSSdAv8 > div.WrkQhIlUY0 > div > strong > span._1LY7DqCnwR"
                ).text
                price = price + "원"
                product_name = soup.select_one(
                    "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div._1ziwSSdAv8 > div.CxNYUPvHfB > h3"
                ).text
            ##네이버 최저가 비교 상품일 때
            elif naver_lowprice in mdurl:
                image = soup.select_one(
                    "#__next > div > div.style_container__3iYev > div.style_inner__1Eo2z > div.style_content_wrap__2VTVx > div.style_content__36DCX > div > div.image_thumb_area__1dzNx > div > div > img"
                )["src"]
                price = soup.select_one(
                    "#__next > div > div.style_container__3iYev > div.style_inner__1Eo2z > div.style_content_wrap__2VTVx > div.style_content__36DCX > div > div.summary_info_area__3XT5U > div.lowestPrice_price_area__OkxBK > div.lowestPrice_low_price__fByaG > em"
                ).text
                price = price + "원"
                product_name = soup.select_one(
                    "#__next > div > div.style_container__3iYev > div.style_inner__1Eo2z > div.top_summary_title__15yAr > h2"
                ).text

            print(product_name, postname)

            doc = {
                "userid": userid,
                "postname": postname,
                "product_name": product_name,
                "categories": categories,
                "mdurl": mdurl,
                "grade": grade,
                "recommendation": recommendation,
                "honeytip": honeytip,
                "image": image,
                "price": price,
                "post_id": "",
                "date": date,
            }

            db.posts.insert_one(doc)
            return jsonify({"msg": "success"})

        except jwt.ExpiredSignatureError:
            return redirect(url_for("login"))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login"))


@app.route("/post/<date>")
def post_detail(date):
    token_receive = request.cookies.get("mytoken")
    try:
        db_detail = db.posts.find_one({"date": date})
        if db_detail is None:
            return redirect(url_for("main"))

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        date = db.posts.find_one({"date": date})
        print(date)
        user_id = payload["id"]
        status = user_id == date["userid"]

        return render_template("detail.html", user_id=user_id, date=date)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page", msg="로그인 정보가 존재하지 않습니다."))
        # 클라에서 받은 url이 유효하지 않으면 메인으로 redirect


@app.route("/post_delete", methods=["POST"])
def post_delete():
    try:
        date = request.form["date"]
        # 게시글 delete 버튼을 본인만 누를 수 있음 (bon in ah nim button an Dum)
        db.posts.delete_one({"date": date})
        return jsonify({"result": "success"})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/edit/<date>', methods=['GET'])
def edit_detail(date):
    try:
        # 상세페이지에서 수정 버튼을 누르면 해당하는 DB를 리스트로 던져줌
        if request.method == 'GET':
            date = db.posts.find_one({"date": date})
            return render_template("edit.html", date=date)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page", msg="로그인 정보가 존재하지 않습니다."))

    
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])


        user_info = db.users.find_one({"username": payload["id"]})

        date_receive = request.form["post_date"]
    ##액션은 사용자가 해당 게시물에 좋아요를 했는지 여부
        action_receive = request.form["action_give"]

        post_info = db.posts.find_one({"date":date_receive},{"_id":False})
        post_like = post_info["like"]

        ##액션은 like , unlike로 줌
        if action_receive == "like":
            post_like += 1
            db.posts.update_one({'date':date_receive},{'$set':{'like':post_like}})
            db.posts.update_one({'userid': user_info}, {'$set': {'action': "like"}})


        else:
            post_like -= 1
            db.posts.update_one({'date': date_receive}, {'$set': {'like': post_like}})
            db.posts.update_one({'userid': user_info}, {'$set': {'action': "unlike"}})

        like_count = db.posts.find_one({"date": date_receive})["like"]

        like_info = {"count":like_count, "action":action_receive, "date":date_receive}

        return jsonify({"result": "success", 'msg': 'updated', "user_info":user_info, "like_info":like_info})


    except jwt.ExpiredSignatureError:
        return redirect(url_for("login_page", msg="로그인 시간이 만료되었습니다."))

    except jwt.exceptions.DecodeError:
        return redirect(url_for("login_page", msg="로그인 정보가 존재하지 않습니다."))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
