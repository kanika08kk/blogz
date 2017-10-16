from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))

    def __init__(self, title,body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_name = request.form['title']
        body_name = request.form['body']
        new_blog = Blog(blog_name,body_name)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()
    return render_template('todos.html',title="Build a blog!", 
        blogs=blogs)
@app.route('/blog', methods=['POST', 'GET'])
 

@app.route('/new-entry', methods=['POST', 'GET'])
def render_entry_form():
    success="true"
    if request.method == 'POST':
        blog_name = request.form['title']
        err1=""
        
        if(blog_name==""):
            err1="Please enter Title"
            success="false"
        body_name = request.form['body']
        err2=""
        if(body_name==""):
            err2="Please enter Body"
            success="false"
    
        if(success=="true"):
            new_blog = Blog(blog_name,body_name)
            db.session.add(new_blog)
            db.session.commit()
    blogs = Blog.query.all()
    if(success=="false"):
        return render_template("new-entry.html", title="Build a blog!",blogs=blogs,err1=err1,err2=err2)
    else:
        return render_template("new-entry.html", title="Build a blog!",blogs=blogs,err1="",err2="")
@app.route('/single-entry', methods=['POST', 'GET'])
def render_singleentry_form():
    blog_id = request.args.get('id')
    blogs = Blog.query.filter_by(id=blog_id).all()
    return render_template("todos.html", title="Build a blog!",blogs=blogs)

if __name__ == '__main__':
    app.run()