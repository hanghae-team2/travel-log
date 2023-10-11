# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

# DB 기본 코드
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

# TravelDestination DB를 만들기 위한 설계도
# class TravelDestination(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     description = db.Column(db.String(500), nullable=False)
#     title = db.Column(db.String(100), nullable=False)
#     location = db.Column(db.String(100), nullable=False)
#     image_url = db.Column(db.String(10000), nullable=False)
#     likes = db.Column(db.Integer, nullable=False)

#     def __repr__(self):
#         return f'{self.location} {self.title} {self.likes} 추천 by {self.user_id}'

# with app.app_context():
#     db.create_all()


@app.route("/")
def home():
    title = '전국팔도 구석구석'
    return render_template('home.html', data=title)

@app.route("/byuser/")
def byuser():
    return render_template('by-user.html')

# Registration Page
@app.route("/create/")
def registration():
    # 나중에 주소 바꿔야 합니다
    return render_template('by-user.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signin')
def signin():
    return render_template('signin.html')


if __name__ == "__main__":
    app.run(debug=True)
