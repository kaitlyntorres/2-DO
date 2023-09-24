from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/kaitlyntorres/Desktop/2-DO-main/database.db'
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

class register_users(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

@app.route("/main")
def main():
    return render_template("index.html")

    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        e= request.form['e']
        p = request.form['p']

        register = register_users(email = e, password= p)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "POST":
        e = request.form["e"]
        p = request.form["p"]
        
        login = register_users.query.filter_by(email=e, password=p).first()
        if login is not None:
            return redirect(url_for("main"))
    return render_template("login.html")
    
def register():
    if request.method == "POST":
        e= request.form['e']
        p = request.form['p']

        register = register_users(email = e, password= p)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("main"))
    return render_template("register.html")

if __name__ == "__main__":
    db.create_all()
    app.run(port=4000,debug=True)