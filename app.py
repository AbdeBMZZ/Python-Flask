from datetime import timedelta
import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import pickle
import json

app = Flask(__name__)
app.secret_key = "abdellahboumaiza"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///etudiants.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=15)

db = SQLAlchemy(app)


class etudiants(db.Model):
    cin = db.Column(db.String(100), primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Integer)

    def __init__(self, cin, nom, prenom, password, is_admin):
        self.cin = cin
        self.nom = nom
        self.prenom = prenom
        self.password = password
        self.is_admin = is_admin


@app.route('/')
def index():
    if "etudiant" in session:
        etd = session["etudiant"]
        updated_etd = db.session.query(
            etudiants).filter_by(cin=etd["cin"]).first()

        flash(f"Welcome {etd['prenom']} {etd['nom']}")
        return render_template("home.html", etudiant=etd)
    else:
        return redirect(url_for('login'))


@app.route('/register/', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.permanent = True

        found_etudiant = etudiants.query.filter_by(
            cin=request.form["cin"]).first()

        if found_etudiant:
            flash("il y a un compte avec ce CIN, pensez à vous connecter!", "error")
            return redirect(url_for("register"))
        else:
            etudiant = etudiants(request.form["cin"], request.form["nom"],
                                 request.form["prenom"], request.form["password"], 0)
            db.session.add(etudiant)
            db.session.commit()
            flash(
                "Compte créé avec succès, vous pouvez maintenant vous connecter", "info")
            return redirect(url_for("login"))
    else:
        if "etudiant" in session:
            return redirect(url_for("index"))
        return render_template('register.html')


@app.route('/login/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        found_etudiant = etudiants.query.filter_by(
            cin=request.form["cin"]).first()

        if found_etudiant:
            if found_etudiant.password == request.form["password"]:
                user = {'cin': found_etudiant.cin,
                        'nom': found_etudiant.nom,
                        'prenom': found_etudiant.prenom,
                        'password': found_etudiant.password,
                        'is_admin': found_etudiant.is_admin
                        }
                session["etudiant"] = user
                return redirect(url_for("index"))
            else:
                flash("Mot de passe incorrect", "error")
                return redirect(url_for("login"))
        else:
            flash("Check your infos", "error")
            return redirect(url_for("login"))

    else:
        if "etudiant" in session:
            return redirect(url_for("index"))
        return render_template('login.html')


@app.route('/logout')
def logout():
    if "etudiant" in session:
        session.pop("etudiant", None)
        return redirect(url_for("login"))


@app.route('/profile', methods=["POST", "GET"])
def profile():
    if request.method == "POST":
        if "etudiant" in session:
            curr_etd = session["etudiant"]
            if curr_etd["password"] == request.form["password"]:
                db.session.query(etudiants).filter_by(
                    cin=curr_etd["cin"]).update({"nom": request.form["nom"], "prenom": request.form["prenom"]})
                flash("Mis à jour avec succés!", "info")
                db.session.commit()
                updated_etd = db.session.query(etudiants).filter_by(
                    cin=curr_etd["cin"]).first()
                user = {'cin': updated_etd.cin,
                        'nom': updated_etd.nom,
                        'prenom': updated_etd.prenom,
                        'password': updated_etd.password,
                        'is_admin': updated_etd.is_admin
                        }
                session["etudiant"] = user
                return render_template("profile.html", etudiant=session["etudiant"])

            else:
                flash("password incorrect!", "info")

    if "etudiant" in session:
        etd = session["etudiant"]
        return render_template("profile.html", etudiant=etd)
    else:
        return redirect(url_for("login"))


@app.route('/getEtudiant', methods=["GET"])
def getEtudiant():

    id = request.args['id']

    found_etd = db.session.query(etudiants).filter_by(cin=id).first()

    etudiant = {
        "cin": found_etd.cin,
        "nom": found_etd.nom,
        "prenom": found_etd.prenom,
        "password": found_etd.password,
        "is_admin": found_etd.is_admin
    }
    return etudiant


@app.route('/admin', methods=["POST", "GET",  "PUT"])
def admin():
    if "etudiant" in session:
        if request.method == "POST":
            etudiant = etudiants(
                request.form["cin"], request.form["nom"], request.form["prenom"], request.form["password"], 0)
            user = {'cin': etudiant.cin,
                    'nom': etudiant.nom,
                    'prenom': etudiant.prenom,
                    'password': etudiant.password,
                    'is_admin': etudiant.is_admin
                    }
            if etudiants.query.filter_by(cin=user["cin"]).first():

                flash("Étudiant Existe veuillez entrer un nouveau etudiant!", "error")
                return redirect(url_for("admin"))
            else:
                db.session.add(etudiant)
                db.session.commit()
                flash("Étudiant ajouté avec succès!", "info")
                return redirect(url_for("admin"))
        if request.method == "PUT":
            flash("Étudiant modifie avec succès!", "info")
            return redirect(url_for("admin"))
        else:
            etd = session["etudiant"]
            if etd['is_admin'] == 1:
                return render_template("admin.html", etudiants=etudiants.query.filter(etudiants.cin != "admin").all())

            else:
                return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))


@app.route('/admin/update', methods=["POST"])
def update_etd():
    etd = db.session.query(etudiants).filter_by(
        cin=request.form["password_confirm"]).update({"cin": request.form["cin"], "nom": request.form["nom"], "prenom": request.form["prenom"], "password": request.form["password"]})

    db.session.commit()
    flash("Mis à jour avec succés!", "info")
    return redirect(url_for("admin"))


@app.route("/deleteEtudiant", methods=["POST"])
def etudiant_delete():
    id = request.form['id']
    etudiants.query.filter(etudiants.cin == id).delete()
    db.session.commit()
    flash("Etudiant supprimé avec succès!", "info")
    return json.dumps({'status': 'OK'})


@app.route("/export")
def export():
    etd = session["etudiant"]
    if etd['is_admin'] == 1:
        conn = sqlite3.connect('etudiants.sqlite3')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM etudiants")
        rows = cursor.fetchall()

        students = []
        content = {}

        for row in rows:
            content = {'cin': row[0], 'nom': row[1], 'prenom': row[2],
                       'password': row[3], 'is_admin': row[4]}
            students.append(content)
            content = {}

        return jsonify(students)
    else:
        return redirect(url_for("index"))


if __name__ == "__main__":
    db.create_all()
    app.run(host='127.0.0.1', debug=True)
