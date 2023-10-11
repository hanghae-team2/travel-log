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


@app.route("/")
def home():
    title = '전국팔도 구석구석'
    return render_template('home.html', data=title)

@app.route("/byuser/")
def byuser():
    return render_template('by-user.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signin')
def signin():
    return render_template('signin.html')


if __name__ == "__main__":
    app.run(debug=True)
