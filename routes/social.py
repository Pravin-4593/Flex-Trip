from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session
)

from app import app
from db import db, cursor


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


#like
@app.route("/like/<int:trip_id>", methods=["POST"])
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
