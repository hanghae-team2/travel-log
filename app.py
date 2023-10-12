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


# Check Authentication function


def isAuth():
    token = request.cookies.get('token')
    # print("Token", token)

    # token 있는지 확인
    if not token:
        print("no token")
        return False

    user = ''
    # token 유효한지 확인
    try:
        decoded = jwt.decode(token, os.environ.get(
            "JWT_SECRET"), algorithms=["HS256"])
        user = User.query.filter_by(username=decoded["username"]).all()[0]
        # 계정 없는 경우 - e.g. 계정 삭제
        if not user:
            return False
    except:
        print('Invalid Token')
        return False
    return user


def paginate_destinations(page, per_page):
    destinations = TravelDestination.query.paginate(page=page, per_page=per_page, error_out=False)
    return destinations



@app.route("/")
def home():
    current_user = isAuth()

    page = request.args.get('page', type=int, default=1)
    per_page = 8  # 페이지당 아이템 수 설정

    favorite_list = db.session.query(TravelDestination, User).join(
        User).filter(User.id == TravelDestination.user_id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('home.html', data=favorite_list, user=current_user)



@app.route("/bylocation/<location>", methods=["GET", "POST"])
def byLocation(location):
    current_user = isAuth()

    filter_list = db.session.query(TravelDestination, User).join(
        User).filter(User.id == TravelDestination.user_id).filter(TravelDestination.location == location).all()

    return render_template('home.html', data=filter_list, user=current_user)


@app.route("/byuser/<int:user_id>", methods=["GET", "POST"])
def byuser(user_id):
    page = request.args.get('page', type=int, default=1)
    per_page = 8  # 페이지당 아이템 수 설정

    filter_list = db.session.query(TravelDestination, User).join(
        User).filter(User.id == TravelDestination.user_id).filter(User.id == user_id).paginate(page=page, per_page=per_page, error_out=False)

    print(filter_list)
    return render_template('by-user.html', data=filter_list)

# likes


@app.route("/update_likes/<int:id>", methods=["POST"])
def update_likes(id):
    # 현재 likes 값을 가져온다
    like = TravelDestination.query.filter_by(id=id).first()

    # 현재 likes값을 증가시킨다
    like.likes += 1

    # 데이터베이스에 변경사항을 저장
    db.session.commit()

    favorite_list = TravelDestination.query.all()
    return render_template('home.html', data=favorite_list)


# 게시물 수정
@app.route("/edit_post/<int:id>", methods=['GET', 'POST'])
def edit_post(id):
    post = TravelDestination.query.get_or_404(id)

    if request.method == 'POST':
        new_title = request.form['title']
        post.title = new_title

        new_location = request.form['location']
        post.location = new_location

        new_description = request.form['description']
        post.description = new_description

        db.session.commit()

        # 게시물 수정 후, 라우트로 리디렉션
        return redirect(url_for('view_post', id=id))

    return render_template('post.html', post=post)


# 게시물 수정 후, 바뀐 POST보여주기
@app.route("/view_post/<int:id>")
def view_post(id):
    post = TravelDestination.query.get_or_404(id)

    return render_template('view_post.html', post=post)


@app.route("/registration/create/")
def registration():
    user_id_receive = 1
    location_receive = request.args.get("loction")
    title_receive = request.args.get("title")
    explanation_receive = request.args.get("explanation")
    image_url_receive = request.args.get("image_url")
    print(request.args)
    # db 저장
    # favourite = favourite(user_id=user_id_receive, location=location_receive, title=title_receive, explanation=explanation_receive, image_url=image_url_receive)
    # db.session.add(favourite)
    # db.session.commit()
    return render_template('registration.html')


# JWT token generator
def generate_jwt_token(username):
    jwt_token = jwt.encode({
        "username": username,
        "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=int(os.environ.get('JWT_EXPIRES_SEC')))},  # TODO(Joonyoung) exp 시간 변경
        os.environ.get('JWT_SECRET'), algorithm="HS256")

    return jwt_token


@app.route('/login', methods=['GET'])
def getLogin():
    return render_template('login.html'), 200


@app.route('/login', methods=['POST'])
def postLogin():
    username = request.form.get('username')
    # user가 있는지 확인
    user = User.query.filter_by(username=username).all()

    # user 없는 경우
    error_message = '아이디 또는 비밀번호가 일치하지 않습니다'
    if not user:
        print('username not found')
        return render_template('login.html', error_message=error_message), 401

    # user가 있는 경우
    password = request.form.get('password')
    password_match = bcrypt.check_password_hash(user[0].password, password)

    # password 틀린 경우
    if not password_match:
        print('wrong password')
        return render_template('login.html', error_message=error_message), 401

    # password 일치하는 경우 JWT token 생성
    token = generate_jwt_token(username)

    # TODO(Joonyoung): login하면 home말고 이전 page로 redirect하기
    res = make_response(redirect(url_for('home')))
    res.set_cookie('token', token, max_age=int(
        int(os.environ.get('JWT_EXPIRES_SEC'))), httponly=True, secure=True, samesite="none")
    return res


@app.route('/signup',  methods=['GET'])
def getSignup():
    return render_template('signup.html'), 200


@app.route('/signup',  methods=['POST'])
def postSignup():
    username = request.form.get('username')

    # user가 있는지 확인
    user = User.query.filter_by(username=username).all()

    # user 있는 경우
    if user:
        print('username already exists')
        return render_template('signup.html', error_message='이미 존재하는 아이디입니다.'), 409

    # user 없는 경우
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    # password 다른 경우
    if password1 != password2:
        print("passwords do not match")
        return render_template('signup.html', error_message='비밀번호가 일치하지 않습니다.'), 400

    # password 같은 경우
    hashed = bcrypt.generate_password_hash(password1).decode('utf-8')

    new_user = User(username=username, password=hashed)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('getLogin')), 201


@app.route('/logout', methods=['POST'])
def logout():
    res = make_response(redirect(url_for('home')))
    res.set_cookie('token', '')
    return res, 200

# authentication 파트
# if not isAuth():
#     return redirect(url_for("getLogin"))


@app.route('/favourite/<id>',  methods=['GET'])
def post(id):

    post = db.session.get(TravelDestination, id)
    if not post:
        return redirect(url_for("home"))

    joined = db.session.query(TravelDestination, User).join(
        User).filter(User.id == TravelDestination.user_id).filter(TravelDestination.id == id).all()[0]

    data = {
        "id": id,
        "title": joined[0].title,
        "description": joined[0].description,
        "location": joined[0].location,
        "image_url": joined[0].image_url,
        "likes": joined[0].likes,
        "user_id": joined[1].username
    }

    # post owner만 수정 가능
    current_user = isAuth()
    post_owner = joined[1].username
    is_owner = current_user.username == post_owner if current_user else False
    print(is_owner)

    return render_template('post.html', data=data, user=current_user, is_owner=is_owner), 200


if __name__ == "__main__":
    app.run(debug=True)
