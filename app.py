from datetime import timedelta
from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "abdellah boumaiza"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///etudiants.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)


class etudiants(db.Model):
    cin = db.Column(db.String(100), primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, cin, nom, prenom, password):
        self.cin = cin
        self.nom = nom
        self.prenom = prenom
        self.password = password


@app.route('/<etd>')
def index(etd):
    return render_template('home.html', user=etd)


@app.route('/show')
def show():
    return 'show working'


@app.route('/register/', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        etudiant1 = request.form["cin"]
        return redirect(url_for("index", etd=etudiant1))
    else:
        return render_template('register.html')


@app.route('/login/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        etudiant1 = request.form["cin"]
        return redirect(url_for("etudiant", etd=etudiant1))
    else:
        return render_template('login.html')


@app.route('/<etd>')
def etudiant(etd):
    return f"<h1>{etd}</h1>"


if __name__ == "__main__":
    # db.create_all()
    app.run()
