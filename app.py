import time
from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user
from flask_http_middleware import MiddlewareManager, BaseHTTPMiddleware

login_manager = LoginManager()

app = Flask(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self):
        super().__init__()

    def dispatch(self, request, call_next):
        t0 = time.time()
        response = call_next(request)
        response_time = time.time()-t0
        response.headers.add("response_time", response_time)
        return response

app.wsgi_app = MiddlewareManager(app)
app.wsgi_app.add_middleware(MetricsMiddleware)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SECRET_KEY'] = "thisissecret"
db = SQLAlchemy(app)

login_manager.init_app(app) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    if request.method == "POST":
        username = request.form.get("username")
        user = User.query.filter_by(username=username)
        if user:
            login_user(user)
            return redirect('/')
        else:
            flash('Invalid Credentials', 'Warning')
            return redirect('/login')
        
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username_ = request.form.get("username")
        email_ = request.form.get("email")
        print(username_, email_)
        user = User(username=username_, email=email_)
        db.session.add(user)
        db.session.commit()
        flash("User Registered Successfully.", "success")
        return redirect('/login')
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/login')

# @app.route("/blog-detail/<int:id>", methods=["GET", "POST"])
# def blog_detail(id):
#     blog = Blog.query.get(id)

#     return render_template('blog_detail.html', blog=blog)

# @app.route("/delete-blog/<int:id>", methods=["GET", "POST"])
# def delete_blog(id):
#     blog = Blog.query.get(id)
#     db.session.delete(blog)
#     db.session.commit()
#     flash("Post has been deleted.", "success")

#     return render_template('blogs.html')

# @app.route("/edit-blog/<int:id>", methods=["GET", "POST"])
# def edit_blog(id):
#     blog = Blog.query.get(id)
#     if request.method == 'POST':
#         blog.title = request.form.get('title')
#         db.session.commit()
#         flash('POST has been updated')
#         return redirect('/')
#     db.session.delete(blog)
#     db.session.commit()
#     flash("Post has been deleted.", "success")

#     return render_template('blogs.html')


if __name__ == "__main__":
    app.run(debug=True)