from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session
)

from app import app
from db import db, cursor
from utils import upload_image, delete_image


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
        
        try:
            image = upload_image(thumbnail, "trip_thumbnails")

        except Exception:
            return render_template(
                "create_trip.html",
                error="Image upload failed. Please try again."
            )
        
        sql="""
        insert into trip(user_id,title,description,thumbnail_url,thumbnail_public_id)
        values(%s,%s,%s,%s,%s)
        """
        cursor.execute(sql,(user_id,title,description,image["url"],image["public_id"]))

        try:
            db.commit()
        except Exception:
            db.rollback()
            #delete uploaded image
            return render_template(
                "create_trip.html",
                error="Something went wrong. Please try again."
            )

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
    select sequence_number , stop_name,photo_url
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

            try:
                image = upload_image(photo, "trip_stops")

            except Exception:
                return render_template(
                    "add_stops.html",
                    error="Image upload failed. Please try again."
                )
        

            sql3="""
            insert into trip_stops(trip_id,sequence_number,stop_name,description,photo_url,photo_public_id)
            values(%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql3,(trip_id,sequence_number,stop_name,description,image["url"],image["public_id"]))

            try:
                db.commit()
            except Exception:
                db.rollback()
                delete_image(image["public_id"])
                return render_template(
                    "add_stops.html",
                    error="Something went wrong. Please try again."
                )


        elif action=="delete":

            sql2="""
            select max(sequence_number)
            from trip_stops
            where trip_id=%s"""
            cursor.execute(sql2,(trip_id,))
            sequence_number=cursor.fetchone()[0]

            if sequence_number is None:
                return redirect(url_for("add_stops",trip_id=trip_id))

            sql4="""
            select photo_public_id
            from trip_stops
            where trip_id=%s and sequence_number=%s """
            cursor.execute(sql4,(trip_id,sequence_number,))
            public_id=cursor.fetchone()[0]

            sql3="""
            delete from trip_stops
            where trip_id=%s and sequence_number=%s"""
            cursor.execute(sql3,(trip_id,sequence_number,))
            
            try:
                db.commit()
            except Exception:
                db.rollback()
                return render_template(
                    "add_stops.html",
                    error="Unable to delete image. Please try again.",
                    stops=stops
                )
            
            try:
                delete_image(public_id)
            except Exception:
                pass
        
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
    select image_url
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

            try:
                image = upload_image(picture, "gallary")

            except Exception:
                return render_template(
                    "gallary.html",
                    error="Image upload failed. Please try again."
                )        

            sql2="""
            insert into gallary(trip_id,sequence_number,image_url,image_public_id)
            values(%s,%s,%s,%s)"""
            cursor.execute(sql2,(trip_id,sequence_number,image["url"],image["public_id"]))
            try:
                db.commit()
            except Exception:
                db.rollback()
                delete_image(image["public_id"])
                return render_template(
                    "gallary.html",
                    error="Something went wrong. Please try again."
                )

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
            
            sql6="""
            select image_public_id
            from gallary
            where trip_id=%s and sequence_number=%s"""
            cursor.execute(sql6,(trip_id,sequence_number,))
            public_id=cursor.fetchone()[0]

            sql3="""
            delete from gallary
            where trip_id=%s and sequence_number=%s"""
            cursor.execute(sql3,(trip_id,sequence_number,))

            try:
                db.commit()
            except Exception:
                db.rollback()
                return render_template(
                    "gallary.html",
                    error="Unable to delete image. Please try again.",
                    images=images
                )
            
            try:
                delete_image(public_id)
            except Exception:
                pass



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
    select title,description,thumbnail_url,user_id,created_at
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

    owner=False
    if(current_user_id==user_id):
        owner=True

    sql4="""
    select username 
    from users
    where id=%s"""
    cursor.execute(sql4,(user_id,))
    username=cursor.fetchone()
    username=username[0]

    sql2="""
    select sequence_number , stop_name ,photo_url,description
    from trip_stops
    where trip_id=%s
    order by sequence_number"""
    cursor.execute(sql2,(trip_id,))
    stops=cursor.fetchall()

    sql3="""
    select image_url
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

    return render_template("trip_details.html",username=username,trip_title=trip_title,user_id=user_id,thumbnail=thumbnail,description=description,stops=stops,images=images,trip_id=trip_id,like=like,created_on=created_on,like_count=like_count,comments=comments,owner=owner)


#Feed
@app.route("/",methods=["get","post"])
def feed():

    user_id=session.get("id")
    if(not user_id):
        return redirect(url_for("login"))

    sql="""
    SELECT
        trip.trip_id,
        trip.user_id,
        trip.title,
        trip.description,
        trip.thumbnail_url,
        trip.created_at,
        users.username,
        COUNT(DISTINCT likes.user_id) AS likes,
        COUNT(DISTINCT trip_stops.sequence_number) AS stops,
        COUNT(DISTINCT gallary.sequence_number) AS photos
    FROM trip
    JOIN users
        ON users.id = trip.user_id
    LEFT JOIN likes
        ON likes.trip_id = trip.trip_id
    LEFT JOIN trip_stops
        ON trip_stops.trip_id = trip.trip_id
    LEFT JOIN gallary
        ON gallary.trip_id = trip.trip_id
    WHERE trip.is_complete = TRUE
    GROUP BY trip.trip_id
    ORDER BY trip.created_at DESC;"""
    cursor.execute(sql)
    trips=cursor.fetchall()
    
    return render_template("feed.html",trips=trips)  


#edit trip
@app.route("/edit_trip/<int:trip_id>",methods=["GET"])
def edit_trip(trip_id):
    user_id=session.get("id")
    if(not user_id):
        return redirect(url_for("login"))
    
    sql="""
    select user_id
    from trip
    where trip_id=%s"""
    cursor.execute(sql,(trip_id,))
    details = cursor.fetchone()

    if details is None:
        return redirect(url_for("profile"))

    uid = details[0]
    
    if not user_id==uid:
        return redirect(url_for("profile"))
    
    sql1="""
    UPDATE trip
    SET is_complete = false
    WHERE trip_id = %s"""
    cursor.execute(sql1,(trip_id,))
    try:
        db.commit()
    except Exception:
        db.rollback()
        return redirect(url_for("profile"))
    return redirect(url_for("add_stops", trip_id=trip_id))
    

#delete trip
@app.route("/delete_trip/<int:trip_id>", methods=["POST"])
def delete_trip(trip_id):

    user_id = session.get("id")
    if not user_id:
        return redirect(url_for("login"))

    sql = """
    SELECT user_id, thumbnail_public_id
    FROM trip
    WHERE trip_id=%s
    """
    cursor.execute(sql, (trip_id,))
    details = cursor.fetchone()

    if details is None:
        return redirect(url_for("profile"))

    if details[0] != user_id:
        return redirect(url_for("profile"))

    thumbnail_public_id = details[1]

    sql = """
    SELECT photo_public_id
    FROM trip_stops
    WHERE trip_id=%s
    """
    cursor.execute(sql, (trip_id,))
    stop_images = cursor.fetchall()

    sql = """
    SELECT image_public_id
    FROM gallary
    WHERE trip_id=%s
    """
    cursor.execute(sql, (trip_id,))
    gallery_images = cursor.fetchall()


    sql = """
    DELETE FROM trip
    WHERE trip_id=%s
    """
    cursor.execute(sql, (trip_id,))

    try:
        db.commit()
    except Exception:
        db.rollback()
        return redirect(url_for("trip_details", trip_id=trip_id))

    
    try:
        delete_image(thumbnail_public_id)
    except Exception:
        pass

    
    for image in stop_images:
        try:
            delete_image(image[0])
        except Exception:
            pass

    
    for image in gallery_images:
        try:
            delete_image(image[0])
        except Exception:
            pass

    return redirect(url_for("profile"))
