from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

# TODO: get static CSS working

app = Flask(__name__, static_url_path='/static')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'super_secret_key'
app.static_folder = 'static'
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)

    def __init__(self, title, body, owner_id, date=None):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        if date is None:
            date = datetime.utcnow()
        self.date = date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(14))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title='Home Page', users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    post_title = ''
    post_body = ''
    post_title_error = ''
    post_body_error = ''

    if request.method == 'POST':

        # request data
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        owner = User.query.filter_by(username=session['username']).first()

        # checking forms
        if post_title == '':
            post_title_error = 'This field cannot be empty!'
        elif post_body == '':
            post_body_error = 'This field cannot be empty!'
        elif len(post_title) > 3:
            # flash('title too short', 'error')
            new_post = Blog(post_title, post_body, owner.id)
            db.session.add(new_post)
            db.session.commit()

            # take post.id from db after commit
            post_id = new_post.id

            url = "/blog?id=" + str(post_id)
            return redirect(url)

    return render_template('newpost.html', title="New Post page", post_title=post_title,
                           post_body=post_body, post_title_error=post_title_error,
                           post_body_error=post_body_error)


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        username_error = ''
        password_error = ''

        user = User.query.filter_by(username=username).first()

        # TODO: refactor all error messages to flash messages

        if user and user.password == password:
            session['username'] = username
            flash('Logged in', 'flash-error-message')
            return redirect('/newpost')
        elif user and user.password != password:
            flash('User password incorrect!', 'error-message')
            return render_template('login.html', password_error='Password is incorrect')
        elif not user:
            return render_template('login.html', username_error='User doesn\'t exist')

    return render_template('login.html', title='Login Page')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args:

        username = request.args.get('user')
        post_id = request.args.get('id')

        if username:
            user = User.query.filter_by(username=username).first()
            user_posts = Blog.query.filter_by(owner_id=user.id).order_by(Blog.date.desc()).all()
            return render_template('user.html', title="user", user=user, posts=user_posts)

        if post_id:
            blog_post = Blog.query.get(post_id)
            return render_template('post.html', title='Single Post', post=blog_post)

    blog_posts = Blog.query.order_by(Blog.date.desc()).all()
    return render_template('blog.html', title='Blog Page', posts=blog_posts)  # validation function


def is_invalid(text):
    return re.search(r'\s+', text) or re.search(r'^.{0,2}$', text) or re.search(r'^\w{20}', text)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''

        # checking for errors
        if is_invalid(username):
            username_error = 'This is not valid username'
        if is_invalid(password):
            password_error = 'This is not valid password'
        if verify == '':
            verify_error = 'Please, repeat your password'
        if verify != password:
            verify_error = 'Password\'s doesnt\'t match'

        # if no validation errors, go to user duplicate check
        if not (username_error or password_error or verify_error):
            # check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                # TODO - user better response message
                return 'Duplicate user'
        else:
            # return form with errors
            return render_template('register.html', username=username, username_error=username_error,
                                   password_error=password_error, verify_error=verify_error)

    return render_template('register.html', title='Register Page')


if __name__ == '__main__':
    app.run()