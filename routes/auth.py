from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import app
from db import db, cursor


#Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        username = username.strip().lower()
        email = email.strip().lower()

        if username=="" or email=="" or password=="":
            return render_template("signup.html",error="Please fill all fields")

        sql1 = """
        select email from users
        where users.email=%s"""
        cursor.execute(sql1,(email,))
        echeck = cursor.fetchone()

        if echeck:
            return render_template("signup.html",error="email already exists !")
        

        sql2 = """
        select username from users
        where users.username=%s"""
        cursor.execute(sql2,(username,))
        ucheck = cursor.fetchone()

        if ucheck:
            return render_template("signup.html",error="username already exists !") 
        
        password = generate_password_hash(password)
        sql = """
        insert into users(username,email,password)
        values(%s,%s,%s)
        """
        values = (
            username,
            email,
            password
        )

        cursor.execute(sql, values)

        db.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")


#Login page
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        action=request.form["action"]
        if action=="login":
            username = request.form["username"]
            password = request.form["password"]

            username = username.strip().lower()
            sql = """
            select password,id
            from users
            where username=%s or email=%s"""

            cursor.execute(sql,(username,username,))
            details = cursor.fetchone()

            if details:
                stored_password = details[0]
                if check_password_hash(stored_password,password):
                    session["id"]=details[1]
                    return redirect(url_for("feed"))
                else:
                    return render_template("login.html",error="incorrect username or password")
            else:
                return render_template("login.html",error="username do not exists")
        elif action=="signup":
            return redirect(url_for("signup"))

    return render_template("login.html")


#logout
@app.route("/logout" ,methods=["GET","POST"])
def logout():
    if session.get("id"):
        session.pop("id")
    return redirect(url_for("login"))
    
