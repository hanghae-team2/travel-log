# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from datetime import datetime, timezone, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from flask_bcrypt import Bcrypt
import os
import jwt
from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
bcrypt = Bcrypt(app)


# DB 기본 코드
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(72),  nullable=False)
    travel_destinations = db.relationship(
        'TravelDestination', backref='user', lazy=True)

    def __repr__(self):
        return f'{self.username} {self.password}'

# TravelDestination DB를 만들기 위한 설계도


class TravelDestination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(10000), nullable=False)
    likes = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'{self.location} {self.title} {self.likes} 추천 by {self.user_id}'


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    favorite_list = TravelDestination.query.all()
    return render_template('home.html', data=favorite_list)


@app.route("/byuser/")
def byuser():
    return render_template('by-user.html')

# Registration Page


@app.route("/create/")
def registration():
    # 나중에 주소 바꿔야 합니다
    return render_template('registration.html')


# JWT token generator
def generate_jwt_token(username):
    jwt_token = jwt.encode({
        "username": username,
        "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=int(os.environ.get('JWT_EXPIRES_SEC')))},  # TODO(Joonyoung) exp 시간 변경
        os.environ.get('JWT_SECRET'), algorithm="HS256")

    # decoded = jwt.decode(jwt_token, os.environ.get(
    #     "JWT_SECRET"), algorithms=["HS256"])
    return jwt_token


@app.route('/login', methods=['GET'])
def getLogin():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def postLogin():
    username = request.form.get('username')
    # user가 있는지 확인
    user = User.query.filter_by(username=username).all()

    # user 없는 경우
    error_message = '아이디 또는 비밀번호가 일치하지 않습니다'
    if not user:
        print('username not found')
        return render_template('login.html', error_message=error_message)

    # user가 있는 경우
    password = request.form.get('password')
    password_match = bcrypt.check_password_hash(user[0].password, password)

    # password 틀린 경우
    if not password_match:
        print('wrong password')
        return render_template('login.html', error_message=error_message)

    # password 일치하는 경우 JWT token 생성
    token = generate_jwt_token(username)

    # TODO(Joonyoung): login하면 home말고 이전 page로 redirect하기
    # res = make_response(redirect('home'))
    res = make_response(redirect('test_jwt'))
    res.set_cookie('token', token, max_age=int(
        int(os.environ.get('JWT_EXPIRES_SEC'))), httponly=True, secure=True, samesite="none")
    return res


@app.route('/signup',  methods=['GET'])
def getSignup():
    return render_template('signup.html')


@app.route('/signup',  methods=['POST'])
def postSignup():
    username = request.form.get('username')

    # user가 있는지 확인
    user = User.query.filter_by(username=username).all()

    # user 있는 경우
    if user:
        print('username already exists')
        return render_template('signup.html', error_message='이미 존재하는 아이디입니다.')

    # user 없는 경우
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    # password 다른 경우
    if password1 != password2:
        print("passwords do not match")
        return render_template('signup.html', error_message='비밀번호가 일치하지 않습니다.')

    # password 같은 경우
    hashed = bcrypt.generate_password_hash(password1).decode('utf-8')

    new_user = User(username=username, password=hashed)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('getLogin'))


@app.route('/logout', methods=['POST'])
def logout():
    # res = make_response(redirect('home'))
    res = make_response(redirect('test_jwt'))
    res.set_cookie('token', '')
    return res


@app.route('/favourite/<id>',  methods=['GET'])
def post(id):
    post = TravelDestination.query.get(id)
    if not post:
        return redirect(url_for("home"))

    data = {
        "id": id,
        "title": post.title,
        "description": post.description,
        "location": post.location,
        "image_url": post.image_url,
        "likes": post.likes,
        # TODO(Joonyoung) username으로 변경
        "user_id": post.user_id
    }
    return render_template('post.html', data=data)


@app.route('/test_jwt')
def test_jwt():
    return render_template('test_jwt.html')


if __name__ == "__main__":
    app.run(debug=True)
