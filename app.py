from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from datetime import datetime
import datetime
import jwt
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from pymongo import MongoClient

client = MongoClient('')
db = 

SECRET_KEY = 

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"


##  HTML ##

# 토큰 없을 경우 login페이지로 리다이렉트. 토큰 있을 경우 index 렌더링.
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.feelingusers.find_one({"userid": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign-up')
def sigh_up():
    return render_template('index.html')

# 회원가입 받은 정보 저장
@app.route('/sign-up/save', methods=['POST'])
def sign_up():
    userid_receive = request.form['userid_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "userid": userid_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": userid_receive  # 프로필 이름 기본값은 아이디
    }
    db.feelingusers.insert_one(doc)
    return render_template('login.html')

# 회원가입 아이디 중복체크
@app.route('/sign-up/check-dup', methods=['POST'])
def check_dup():
    userid_receive = request.form['userid_give']
    exists = bool(db.feelingusers.find_one({"userid": userid_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 로그인 입력값 검사
@app.route('/sign-in', methods=['POST'])
def sign_in():
    userid_receive = request.form['userid_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.feelingusers.find_one({'userid': userid_receive, 'password': pw_hash})
    if result is not None:
        payload = {
            'id': userid_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token, 'msg':'님, 환영합니다!'})
            # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 작성글 db에 저장
@app.route('/upload', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.feelingusers.find_one({"userid": payload["id"]})
        ytburl_receive = request.form["ytburl_give"]
        ytbcode = ytburl_receive[-11:]
        comment_receive = request.form["comment_give"]
        feel_recive = request.form['feel_give']
        date_receive = request.form.get('date_give', False)
        file = request.files["file_give"]
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        extension = file.filename.split('.')[-1]
        filename = f'file-{mytime}'
        save_to = f'static/img/{filename}.{extension}'
        file.save(save_to)
        doc = {
            "userid": user_info["userid"],
            "profile_name": user_info["profile_name"],
            "ytburl": ytburl_receive,
            "ytbcode": ytbcode,
            "comment": comment_receive,
            "feel": feel_recive,
            'file': f'{filename}.{extension}',
            "date": date_receive
        }
        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '등록되었습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    except (KeyError):
        return jsonify({"msg": "파일을 등록해주세요!"})


# 작성글, 좋아요 get (post, user id, like)
@app.route("/get-posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.posts.find({}).sort("_id", -1).limit(20))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})  # 좋아요
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "userid": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 좋아요 값 type(like/unlike)에 따라 db에 저장/삭제
@app.route('/update-like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.feelingusers.find_one({"userid": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "userid": user_info['userid'],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

