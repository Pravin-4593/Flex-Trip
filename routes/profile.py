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


# Profile
@app.route("/profile")
def profile():

    user_id = session.get("id")
    if user_id is None:
        return redirect(url_for("login"))

    sql = """
    select username,email,bio,profile_url
    from users
    where id=%s
    """
    cursor.execute(sql, (user_id,))
    details = cursor.fetchone()

    sql2 = """
    select
        trip.trip_id,
        trip.title,
        trip.description,
        trip.thumbnail_url,
        trip.created_at,
        COUNT(likes.trip_id),
        trip.is_complete
    from trip
    left join likes
        on likes.trip_id=trip.trip_id
    where trip.user_id=%s
    group by trip.trip_id
    order by trip.created_at desc
    """
    cursor.execute(sql2, (user_id,))
    trips = cursor.fetchall()

    return render_template(
        "profile.html",
        username=details[0],
        email=details[1],
        bio=details[2],
        profile_url=details[3],
        trips=trips,
        owner=True
    )


# View Profile
@app.route("/user/<int:user_id>")
def view_profile(user_id):

    current_user_id = session.get("id")
    if current_user_id is None:
        return redirect(url_for("login"))

    if current_user_id == user_id:
        return redirect(url_for("profile"))

    sql = """
    select username,bio,profile_url
    from users
    where id=%s
    """
    cursor.execute(sql, (user_id,))
    details = cursor.fetchone()

    if details is None:
        return redirect(url_for("search"))

    sql2 = """
    select
        trip.trip_id,
        trip.title,
        trip.description,
        trip.thumbnail_url,
        trip.created_at,
        COUNT(likes.trip_id),
        trip.is_complete
    from trip
    left join likes
        on likes.trip_id=trip.trip_id
    where trip.user_id=%s
      and trip.is_complete=true
    group by trip.trip_id
    order by trip.created_at desc
    """
    cursor.execute(sql2, (user_id,))
    trips = cursor.fetchall()

    return render_template(
        "profile.html",
        username=details[0],
        bio=details[1],
        profile_url=details[2],
        trips=trips,
        owner=False
    )

# Edit Profile
@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():

    user_id = session.get("id")
    if user_id is None:
        return redirect(url_for("login"))

    sql = """
    SELECT username,
           bio,
           profile_url,
           profile_public_id
    FROM users
    WHERE id=%s
    """
    cursor.execute(sql, (user_id,))
    details = cursor.fetchone()

    if details is None:
        return redirect(url_for("profile"))

    username = details[0]
    bio = details[1]
    profile_url = details[2]
    old_public_id = details[3]

    if request.method == "POST":

        username = request.form["username"].strip().lower()
        bio = request.form["bio"].strip()
        picture = request.files["profile_picture"]

        if username == "":
            return render_template(
                "edit_profile.html",
                error="Username cannot be empty.",
                username=username,
                bio=bio,
                profile_url=profile_url
            )

        sql = """
        SELECT id
        FROM users
        WHERE username=%s AND id!=%s
        """
        cursor.execute(sql, (username, user_id))

        if cursor.fetchone():
            return render_template(
                "edit_profile.html",
                error="Username already exists.",
                username=username,
                bio=bio,
                profile_url=profile_url
            )

        if picture.filename == "":

            sql = """
            UPDATE users
            SET username=%s,
                bio=%s
            WHERE id=%s
            """

            cursor.execute(sql, (username, bio, user_id))
            db.commit()

            return redirect(url_for("profile"))

        try:
            image = upload_image(picture, "profile_pictures")

        except Exception:

            return render_template(
                "edit_profile.html",
                error="Image upload failed.",
                username=username,
                bio=bio,
                profile_url=profile_url
            )

        sql = """
        UPDATE users
        SET username=%s,
            bio=%s,
            profile_url=%s,
            profile_public_id=%s
        WHERE id=%s
        """

        cursor.execute(
            sql,
            (
                username,
                bio,
                image["url"],
                image["public_id"],
                user_id
            )
        )

        try:
            db.commit()

        except Exception:

            db.rollback()
            delete_image(image["public_id"])

            return render_template(
                "edit_profile.html",
                error="Something went wrong.",
                username=username,
                bio=bio,
                profile_url=profile_url
            )

        try:
            delete_image(old_public_id)
        except Exception:
            pass

        return redirect(url_for("profile"))

    return render_template(
        "edit_profile.html",
        username=username,
        bio=bio,
        profile_url=profile_url
    )

# Delete Account
@app.route("/delete_account", methods=["POST"])
def delete_account():

    user_id = session.get("id")
    if user_id is None:
        return redirect(url_for("login"))

    sql = """
    SELECT profile_public_id
    FROM users
    WHERE id=%s
    """
    cursor.execute(sql, (user_id,))
    profile = cursor.fetchone()

    profile_public_id = None
    if profile:
        profile_public_id = profile[0]

    sql = """
    SELECT thumbnail_public_id
    FROM trip
    WHERE user_id=%s
    """
    cursor.execute(sql, (user_id,))
    thumbnails = cursor.fetchall()

    sql = """
    SELECT photo_public_id
    FROM trip_stops
    JOIN trip
        ON trip.trip_id = trip_stops.trip_id
    WHERE trip.user_id=%s
    """
    cursor.execute(sql, (user_id,))
    stop_photos = cursor.fetchall()


    sql = """
    SELECT image_public_id
    FROM gallary
    JOIN trip
        ON trip.trip_id = gallary.trip_id
    WHERE trip.user_id=%s
    """
    cursor.execute(sql, (user_id,))
    gallery_images = cursor.fetchall()

    sql = """
    DELETE FROM users
    WHERE id=%s
    """
    cursor.execute(sql, (user_id,))

    try:
        db.commit()

    except Exception:
        db.rollback()
        return redirect(url_for("profile"))


    if profile_public_id:
        try:
            delete_image(profile_public_id)
        except Exception:
            pass

    for image in thumbnails:
        if image[0]:
            try:
                delete_image(image[0])
            except Exception:
                pass

    for image in stop_photos:
        if image[0]:
            try:
                delete_image(image[0])
            except Exception:
                pass

    for image in gallery_images:
        if image[0]:
            try:
                delete_image(image[0])
            except Exception:
                pass

    session.pop("id", None)

    return redirect(url_for("login"))