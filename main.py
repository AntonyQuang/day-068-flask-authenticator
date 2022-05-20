from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FILES'] = 'static/files'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB. 
# db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        entry = request.form

        new_entry = User(
            email=entry["email"],
            password=generate_password_hash(entry["password"], method='pbkdf2:sha256', salt_length=8),
            name=entry["name"]
        )
        db.session.add(new_entry)
        db.session.commit()
        print(new_entry.name)
        return redirect(url_for('secrets', name=new_entry.name))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = request.form

        user = User(
            email=form["email"],
            password=form["password"],
        )
        user_in_database = db.session.query(User).filter(User.email == user.email).first()

        if check_password_hash(user_in_database.password, user.password):
            login_user(user)
            flash("logged in successfully")
            return "logged in"
    return render_template("login.html")


@app.route('/secrets', methods=["GET"])
def secrets():
    return render_template("secrets.html", name=request.args.get('name'))


@app.route('/logout')
def logout():
    pass


@app.route('/download', methods=["GET"])
def download():
    try:
        return send_from_directory(app.config['FILES'], path="cheat_sheet.pdf")
    except FileNotFoundError:
        return "File not found", 404


if __name__ == "__main__":
    app.run(debug=True)
