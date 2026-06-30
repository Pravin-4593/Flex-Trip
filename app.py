from flask import Flask, render_template, request, redirect, url_for, session, render_template
from db import db, cursor
from werkzeug.security import generate_password_hash,check_password_hash
from dotenv import load_dotenv
import os
import time

load_dotenv()

app = Flask(__name__)


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
    

#Profile 
@app.route("/profile",methods=["GET","POST"])
def profile():
    user_id=session.get("id")
    if user_id is None:
        return redirect(url_for("login"))
    else:
        sql="""
        select username,email,bio
        from users
        where id=%s"""
        cursor.execute(sql,(user_id,))
        details = cursor.fetchone()
        bio=details[2]

        sql2="""
        select trip.trip_id,trip.title,trip.description,trip.thumbnail,trip.created_at,COUNT(likes.trip_id),trip.is_complete
        from trip
        left join likes on likes.trip_id=trip.trip_id
        where trip.user_id=%s
        group by trip.trip_id
        order by trip.created_at desc"""
        cursor.execute(sql2,(user_id,))
        trips=cursor.fetchall()
        if request.method=="POST":
            bio=request.form["new_bio"]
            if not bio=="":
                sql3="""
                update users
                set bio=%s
                where id=%s"""
                cursor.execute(sql3,(bio,user_id,))
                db.commit()
                return redirect(url_for("profile"))
            
        return render_template("profile.html",username=details[0],email=details[1],trips=trips,bio=bio,owner=True)
    
    
#ViewProfile 
@app.route("/user/<int:user_id>",methods=["GET","POST"])
def view_profile(user_id):
    current_user_id=session.get("id")
    if current_user_id is None:
        return redirect(url_for("login"))
    owner=False
    if current_user_id==user_id:
        return redirect(url_for("profile"))
    sql="""
    select username,bio
    from users
    where id=%s"""
    cursor.execute(sql,(user_id,))
    details = cursor.fetchone()
    if details is None:
        return redirect(url_for("search"))
    bio=details[1]

    sql2="""
    select trip.trip_id,trip.title,trip.description,trip.thumbnail,trip.created_at,COUNT(likes.trip_id)
    from trip
    left join likes on likes.trip_id=trip.trip_id
    where trip.user_id=%s
    group by trip.trip_id
    order by trip.created_at desc"""
    cursor.execute(sql2,(user_id,))
    trips=cursor.fetchall()
    return render_template("profile.html",username=details[0],trips=trips,bio=bio,owner=owner)
  

# create trip
@app.route("/create_trip",methods=["GET","POST"])
def create_trip():
    user_id=session.get("id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method=="POST":
        title=request.form["triptitle"]
        description=request.form["description"]
        thumbnail=request.files["thumbnail"]
        if(title=="" or description=="" or thumbnail.filename==""):
            return render_template("create_trip.html",error="Fill all details") 
        t=int(time.time())
        new_filename=str(user_id)+"_"+str(t)+"_"+thumbnail.filename
        path=os.path.join(
            "static",
            "uploads",
            "thumbnail",
            new_filename
        )
        sql="""
        insert into trip(user_id,title,description,thumbnail)
        values(%s,%s,%s,%s)
        """
        thumbnail.save(path)
        cursor.execute(sql,(user_id,title,description,path,))
        db.commit()
        trip_id=cursor.lastrowid
        return redirect(url_for("add_stops",trip_id=trip_id))
    return render_template("create_trip.html")


# add stops
@app.route("/add_stops/<int:trip_id>",methods=["GET","POST"])
def add_stops(trip_id):

    user_id=session.get("id")
    if(not user_id):
        return redirect(url_for("login"))
    
    sql="""
    select user_id,is_complete
    from trip
    where trip_id=%s"""
    cursor.execute(sql,(trip_id,))
    details=cursor.fetchone()
    uid=details[0]
    is_complete=details[1]
    if uid is None:
        return redirect(url_for("profile"))

    if not user_id==uid:
        return redirect(url_for("profile"))
    
    if is_complete:
        return redirect(url_for("trip_details",trip_id=trip_id))
    
    sql1="""
    select sequence_number , stop_name,photo
    from trip_stops
    where trip_id=%s
    order by sequence_number"""
    cursor.execute(sql1,(trip_id,))
    stops=cursor.fetchall()

    if request.method=="POST":

        action=request.form["action"]

        if(action=="add"):

            stop_name=request.form["stop_name"]
            description=request.form["description"]
            photo=request.files["photo"]
            if(stop_name=="" or photo.filename==""):
                return render_template("add_stops.html",error="Fill all details",stops=stops) 
                       
            sql2="""
            select max(sequence_number)
            from trip_stops
            where trip_id=%s"""
            cursor.execute(sql2,(trip_id,))
            sequence_number=cursor.fetchone()
            sequence_number=sequence_number[0]
                
            if sequence_number is None:
                sequence_number=0
            sequence_number+=1

            new_filename=str(trip_id)+"_"+str(sequence_number)+"_"+photo.filename
            path=os.path.join(
                "static",
                "uploads",
                "stops",
                new_filename
            )
            photo.save(path)

            sql3="""
            insert into trip_stops(trip_id,sequence_number,stop_name,description,photo)
            values(%s,%s,%s,%s,%s)"""
            cursor.execute(sql3,(trip_id,sequence_number,stop_name,description,path))
            db.commit()

        elif action=="delete":

            sql2="""
            select max(sequence_number)
            from trip_stops
            where trip_id=%s"""
            cursor.execute(sql2,(trip_id,))
            sequence_number=cursor.fetchone()

            if sequence_number is None:
                return redirect(url_for("add_stops",trip_id=trip_id))
            sequence_number=sequence_number[0]

            sql3="""
            delete from trip_stops
            where trip_id=%s and sequence_number=%s"""
            cursor.execute(sql3,(trip_id,sequence_number,))
            db.commit()
        
        elif action=="done":
            return redirect(url_for("gallary",trip_id=trip_id))
       
        return redirect(url_for("add_stops",trip_id=trip_id))

    return render_template("add_stops.html",stops=stops)


#gallary
@app.route("/gallary/<int:trip_id>",methods=["GET","POST"])
def gallary(trip_id):

    user_id=session.get("id")
    if(not user_id):
        return redirect(url_for("login"))
    
    sql="""
    select user_id,is_complete
    from trip
    where trip_id=%s"""
    cursor.execute(sql,(trip_id,))
    details=cursor.fetchone()
    uid=details[0]
    is_complete=details[1]
    if uid is None:
        return redirect(url_for("profile"))

    if not user_id==uid:
        return redirect(url_for("trip_details",trip_id=trip_id))
    
    if is_complete:
        return redirect(url_for("trip_details",trip_id=trip_id))
    
    sql1="""
    select pics
    from gallary
    where trip_id=%s
    order by sequence_number"""
    cursor.execute(sql1,(trip_id,))
    images=cursor.fetchall()

    if request.method=="POST":
        action=request.form["action"]
        
        if action=="add":

            picture=request.files["picture"]
            if picture.filename=="":
                return render_template("gallary.html",error="Please upload file",images=images) 
            
            sql2="""
            select max(sequence_number)
            from gallary
            where trip_id=%s"""
            cursor.execute(sql2,(trip_id,))
            sequence_number=cursor.fetchone()
            sequence_number=sequence_number[0]

            if sequence_number is None:
                sequence_number=-1
            sequence_number+=1

            new_filename=str(trip_id)+"_"+str(sequence_number)+"_"+picture.filename
            new_filename=os.path.join(
                "static",
                "uploads",
                "gallary",
                new_filename
            )
            picture.save(new_filename)

            sql2="""
            insert into gallary(trip_id,sequence_number,pics)
            values(%s,%s,%s)"""
            cursor.execute(sql2,(trip_id,sequence_number,new_filename))
            db.commit()

        elif action=="delete":

            sql2="""
            select max(sequence_number)
            from gallary
            where trip_id=%s"""
            cursor.execute(sql2,(trip_id,))
            sequence_number=cursor.fetchone()
            sequence_number=sequence_number[0]

            if sequence_number is None:
                return redirect(url_for("gallary",trip_id=trip_id))
            
            sql3="""
            delete from gallary
            where trip_id=%s and sequence_number=%s"""
            cursor.execute(sql3,(trip_id,sequence_number,))
            db.commit()


        elif action=="done":
            sql5="""
            update trip
            set is_complete=true
            where trip_id=%s"""
            cursor.execute(sql5,(trip_id,))
            db.commit()
            return redirect(url_for("trip_details",trip_id=trip_id))
        
        return redirect(url_for("gallary",trip_id=trip_id))

    return render_template("gallary.html",images=images)


#trip_details
@app.route("/trip_details/<int:trip_id>",methods=["GET","POST"])
def trip_details(trip_id):

    current_user_id=session.get("id")
    if(not current_user_id):
        return redirect(url_for("login"))
    
    
    sql1="""
    select title,description,thumbnail,user_id,created_at
    from trip
    where trip_id=%s"""
    cursor.execute(sql1,(trip_id,))
    details=cursor.fetchone()
    if details is None:
        return redirect(url_for("profile"))
    trip_title=details[0]
    description=details[1]
    thumbnail=details[2]
    user_id=details[3]
    created_on=details[4]

    sql4="""
    select username 
    from users
    where id=%s"""
    cursor.execute(sql4,(user_id,))
    username=cursor.fetchone()
    username=username[0]

    sql2="""
    select sequence_number , stop_name ,photo,description
    from trip_stops
    where trip_id=%s
    order by sequence_number"""
    cursor.execute(sql2,(trip_id,))
    stops=cursor.fetchall()

    sql3="""
    select pics
    from gallary
    where trip_id=%s
    order by sequence_number"""
    cursor.execute(sql3,(trip_id,))
    images=cursor.fetchall()

    sql4="""
    select *
    from likes
    where user_id=%s and trip_id=%s"""
    cursor.execute(sql4,(current_user_id,trip_id,))
    like=cursor.fetchone()
    if like is None:
        like=False
    else:
        like=True

    sql5="""
    select COUNT(trip_id)
    from likes
    where trip_id=%s"""
    cursor.execute(sql5,(trip_id,))
    like_count=cursor.fetchone()

    if like_count is None:
        like_count=0
    else:
        like_count=like_count[0]

    if request.method=="POST":
        comment=request.form["comment"]
        if comment.strip()=="":
            return "Enter valid comment!"
        if comment.__len__()>1000:
            return "comment too big!"
        sql6="""
        insert into comments(user_id,trip_id,comment)
        values(%s,%s,%s)"""
        cursor.execute(sql6,(current_user_id,trip_id,comment,))
        db.commit()
        return redirect(url_for("trip_details",trip_id=trip_id))

    sql7="""
    select comments.comment,users.username ,comments.created_at
    from comments
    join users on users.id=comments.user_id
    where comments.trip_id=%s
    order by comments.created_at
    """
    cursor.execute(sql7,(trip_id,))
    comments=cursor.fetchall()

    return render_template("trip_details.html",username=username,trip_title=trip_title,user_id=user_id,thumbnail=thumbnail,description=description,stops=stops,images=images,trip_id=trip_id,like=like,created_on=created_on,like_count=like_count,comments=comments)


#Search
@app.route("/search")
def search():

    user_id=session.get("id")
    if(not user_id):
        return redirect(url_for("login"))
    
    username=request.args.get("username")
    search=False
    if username:
        search=True
        username.lower()
        username="%"+username+"%"
        sql="""
        select id, username, count(trip.trip_id), users.created_at
        from users
        left join trip on trip.user_id=users.id and trip.is_complete=true
        where username like %s
        group by users.id
        """
        cursor.execute(sql,(username,))
        users=cursor.fetchall()

    else:

        users=[]

    return render_template("search.html",users=users,search=search)


#Feed
@app.route("/",methods=["get","post"])
def feed():

    user_id=session.get("id")
    if(not user_id):
        return redirect(url_for("login"))

    sql="""
    select trip.trip_id ,trip.user_id,trip.title,trip.description,trip.thumbnail,trip.created_at,users.username,COUNT(likes.trip_id)
    from trip
    join users on users.id=trip.user_id
    left join likes on likes.trip_id=trip.trip_id
    where is_complete=true
    group by trip.trip_id
    order by trip.created_at desc"""
    cursor.execute(sql)
    trips=cursor.fetchall()

    return render_template("feed.html",trips=trips)  


#like
@app.route("/like/<int:trip_id>",methods=["get","post"])
def likes(trip_id):
    user_id=session.get("id")
    sql="""
    select *
    from likes
    where user_id=%s and trip_id=%s"""
    cursor.execute(sql,(user_id,trip_id,))
    flag=cursor.fetchone()
    if flag is None:
        sql2="""
        insert into likes (user_id,trip_id)
        values(%s,%s)"""
        cursor.execute(sql2,(user_id,trip_id,))
        db.commit()
    else:
        sql2="""
        delete from likes
        where user_id=%s and trip_id=%s"""
        cursor.execute(sql2,(user_id,trip_id,))
        db.commit()

    return redirect(url_for("trip_details",trip_id=trip_id))

app.secret_key = os.getenv("SECRET_KEY")
if __name__ == "__main__":
    app.run(debug=True)