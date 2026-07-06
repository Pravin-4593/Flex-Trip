from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session
)

from app import app
from db import db, cursor


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
        select trip.trip_id,trip.title,trip.description,trip.thumbnail_url,trip.created_at,COUNT(likes.trip_id),trip.is_complete
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
    select trip.trip_id,trip.title,trip.description,trip.thumbnail_url,trip.created_at,COUNT(likes.trip_id),trip.is_complete
    from trip
    left join likes on likes.trip_id=trip.trip_id
    where trip.user_id=%s and trip.is_complete=true
    group by trip.trip_id
    order by trip.created_at desc"""
    cursor.execute(sql2,(user_id,))
    trips=cursor.fetchall()
    return render_template("profile.html",username=details[0],trips=trips,bio=bio,owner=owner)
