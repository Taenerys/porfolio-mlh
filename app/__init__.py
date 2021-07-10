import os
from flask import (
    Flask,
    request,
    Response,
    render_template,
    send_file,
    send_from_directory,
    jsonify,
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import smtplib

load_dotenv()
app = Flask(__name__)

app.secret_key = "development key"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}".format(
    user=os.getenv("POSTGRES_USER"),
    passwd=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=5432,
    table=os.getenv("POSTGRES_DB"),
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.init_app(app)


class UserModel(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"


headerInfo = {
    "img": "./static/img/coverimg.jpg",
    "name": "Fellow Name",
    "intro": "Short intro here",
}

aboutInfo = {
    "shortParagraph": "Hi! My name is Fellow. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu sapien and lorem fermentum hendrerit quis mattis arcu. Nulla eget efficitur ex. Proin hendrerit ligula quis vehicula interdum.",
    "education": [
        {"schoolName": "MLH 1", "year": "2017 - 2020"},
        {"schoolName": "MLH 2", "year": "2020 - Present"},
    ],
    "interest": ["Interest 1", "Interest 2", "Interest 3"],
    "experience": [
        {
            "jobTitle": "Title 1",
            "year": "2020",
            "jobDesc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu sapien and lorem fermentum hendrerit quis mattis arcu. Nulla eget efficitur ex. Proin hendrerit ligula quis vehicula interdum.",
        },
        {
            "jobTitle": "Title 2",
            "year": "2021",
            "jobDesc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu sapien and lorem fermentum hendrerit quis mattis arcu. Nulla eget efficitur ex. Proin hendrerit ligula quis vehicula interdum.",
        },
    ],
    "skill": ["Skill 1", "Skill 2", "Skill 3"],
}

projects = [
    {
        "title": "Flask Web App",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu sapien and lorem fermentum hendrerit quis mattis arcu. Nulla eget efficitur ex. Proin hendrerit ligula quis vehicula interdum.",
        "date": "06/09/2021",
        "img": "./static/img/projects/web-dev.jpg",
        "url": "www.github.com",
    },
    {
        "title": "Machine Learning Project For Data Prediction",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu sapien and lorem fermentum hendrerit quis mattis arcu. Nulla eget efficitur ex. Proin hendrerit ligula quis vehicula interdum.",
        "date": "06/09/2021",
        "img": "./static/img/projects/machine-learning.jpg",
        "url": "www.github.com",
    },
]


# Pages
@app.route("/")
def index():
    return render_template(
        "about.html",
        title="MLH Fellow",
        url=os.getenv("URL"),
        headerInfo=headerInfo,
        aboutInfo=aboutInfo,
    )


@app.route("/about")
def aboutMe():
    return render_template("about.html", headerInfo=headerInfo, aboutInfo=aboutInfo)


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html", headerInfo=headerInfo, projects=projects)


@app.route("/blog")
def blogPage():
    blog_posts = get_posts()
    path = "app/static/img/blog/"
    for post in blog_posts:
        post.content = post.content[:255] + "..."
        with open(path + post.img_name, "wb") as binary_file:
            # Write bytes to file
            binary_file.write(post.img)
    return render_template(
        "blog.html", url=os.getenv("URL"), headerInfo=headerInfo, blog_posts=blog_posts
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", url=os.getenv("URL"), headerInfo=headerInfo)


@app.route("/sendMsg", methods=["POST"])
def sendMsg():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]
    if not name or not email or not message:
        return "Not enough data!", 400

    message2Send = "\nName: " + name + " \nEmail: " + email + "\nMessage: " + message
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("testmlh.pod.333@gmail.com", "iampod333")
    server.sendmail(
        "testmlh.pod.333@gmail.com", "testmlh.pod.333@gmail.com", message2Send
    )
    return render_template("success.html", url=os.getenv("URL"), headerInfo=headerInfo)


# Creating new blog posts
@app.route("/new-blog")
def new_blog():
    return render_template(
        "new_blog.html", title="New Blog", url=os.getenv("URL"), projects=projects
    )


@app.route("/upload", methods=["POST"])
def upload():
    pic = request.files["pic"]
    title = request.form["name"]
    content = request.form["blog-content"]

    if not pic or not title or not content:
        return "Not enough data!", 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return "Not enough data!", 400

    post = Blog(
        title=title,
        content=content,
        img=pic.read(),
        img_name=filename,
        img_mimetype=mimetype,
    )
    db.session.add(post)
    db.session.commit()

    return render_template("success.html", url=os.getenv("URL"), headerInfo=headerInfo)


@app.route("/blog/<int:id>")
def get_post(id):
    post = Blog.query.filter_by(id=id).first()
    if not post:
        return "Post Not Found!", 404

    return render_template(
        "detail_blog.html", url=os.getenv("URL"), title=post.title, post=post
    )


@app.route("/health", methods=["GET"])
def check_health():
    return Response("SUCCESS", status=200)


def get_posts():
    posts = Blog.query.order_by(Blog.date_created).all()
    return posts


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif UserModel.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        if error is None:
            new_user = UserModel(username, generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    ## TODO: Return a restister page
    return "Register Page not yet implemented", 501


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            return "Login Successful", 200
        else:
            return error, 418

    ## TODO: Return a login page
    return "Login Page not yet implemented", 501
