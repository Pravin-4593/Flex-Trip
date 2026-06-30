# Flex Trip 🌍

A travel social media web application where users can create trips, share travel memories, upload photos, and interact with other travelers.

Built using Flask and MySQL.

---

## Live Demo

Add after deployment:
`https://your-app-name.onrender.com`

---

## Screenshots

### Login Page

[Add Screenshot Here]

---

### Feed

[Add Screenshot Here]

---

### Profile

[Add Screenshot Here]

---

### Trip Details

[Add Screenshot Here]

---

### Gallery

[Add Screenshot Here]

---

## Tech Stack

### Backend

* Flask
* MySQL
* mysql-connector-python

### Frontend

* HTML
* CSS
* JavaScript

### Security

* Werkzeug Password Hashing

---

## Features

### Authentication

✔ Signup

✔ Login

✔ Logout

---

### Trip Management

✔ Create Trip

✔ Add Trip Stops

✔ Upload Stop Photos

✔ Upload Gallery Photos

✔ View Trip Details

---

### Social Features

✔ Feed

✔ Likes

✔ Comments

✔ Search Users

✔ View Public Profiles

---

### Media

✔ Trip Thumbnail

✔ Stop Photos

✔ Gallery Photos

---

## Database Tables

* users
* trip
* trip_stops
* gallary
* likes
* comments

---

## Project Structure

```text
FlexTrip

├── app.py

├── db.py

├── requirements.txt

├── README.md

├── templates/

│   ├── base.html

│   ├── login.html

│   ├── signup.html

│   ├── feed.html

│   ├── profile.html

│   ├── search.html

│   ├── create_trip.html

│   ├── add_stops.html

│   └── trip_details.html


├── static/

│   ├── css/

│   │   ├── base.css

│   │   ├── login.css

│   │   ├── signup.css

│   │   ├── feed.css

│   │   ├── profile.css

│   │   ├── search.css

│   │   ├── create_trip.css

│   │   ├── add_stops.css

│   │   └── trip_details.css


│   └── uploads/

│       ├── web/

│       ├── gallery/

│       └── ...

```

---

## How to Run

### 1. Clone the repository

```bash
git clone <repository-link>
```

### 2. Move into project folder

```bash
cd FlexTrip
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

Create a MySQL database and update the credentials in `db.py`.

---

### 5. Run the application

```bash
python app.py
```

---

### 6. Open in browser

```text
http://127.0.0.1:5000
```

---

## Future Improvements

* Follow Users
* Notifications
* Saved Trips
* Explore Page
* Interactive Maps
* Mobile Responsive Design

---

## Author

Created by **PRAVIN** using Flask and MySQL.
