from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, check, is_valid_linkedin_url, generate_key


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database/eventlink.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# REFRESH MATES
def refresh_mates(id):
    '''Takes a users id as input, and adds all mates to the mates table'''
    # Step 1: get a list of the id of every joined room
    joined_rooms = db.execute("SELECT room_id FROM members WHERE user_id = ?", id)
    joined_room_ids = [room["room_id"] for room in joined_rooms]

    # Step 2: Iterate through the rooms and find other users
    for room_id in joined_room_ids:
        mate_infos = db.execute("SELECT user_id, room_id FROM members WHERE room_id = ? AND user_id != ?",
                                room_id, id)

        # Step 3: Add other users to the mates table if not already present
        for mate_info in mate_infos:
            mate = db.execute("SELECT * FROM mates WHERE user_id1 = ? AND user_id2 = ? AND room_id=?", 
                                    id, mate_info["user_id"], mate_info["room_id"])    
            if mate: continue
            db.execute("INSERT INTO mates (user_id1, user_id2, room_id, status) VALUES (?, ?, ?, ?)",
                id, mate_info["user_id"], mate_info["room_id"], 0)

# HOMEPAGE
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    refresh_mates(id)
    return render_template("index.html", info=info)

####
######## ADMIN
####

# ADMIN
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    # verify admin status
    if info["role"] != 1: 
        flash("You do not possess admin Privileges")
        return redirect("/")
    
    if request.method == "GET":
        return render_template("admin.html", info=info) 
    else:
        action = request.form.get("action")
        if action == "user":
            username = request.form.get("username")
            if username:
                users = db.execute("SELECT * FROM users WHERE username LIKE ?", f'%{username}%')
                return render_template("admin.html", users=users, info=info)
            else:
                flash("Please provide a username.")
                return redirect("/admin")

        elif action == "room":
            room_key = request.form.get("key")
            if room_key:
                rooms = db.execute("SELECT * FROM rooms WHERE key = ?", room_key)
                return render_template("admin.html", rooms=rooms, info=info)
            else:
                flash("Please provide a room key.")
                return redirect("/admin")



# ADMIN ACTIONS
@app.route("/admin/action", methods=["POST"])
@login_required
def admin_actions():
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    # verify admin status
    if info["role"] != 1: 
        flash("You do not possess admin Privileges")
        return redirect("/")
    action = request.form.get("action")
    if action == "user_update":
        target_user_id = request.form.get("user_id")
        if not target_user_id:
            flash("No user specified.")
            return redirect("/admin")

        # Toggle the user's role
        current_role = db.execute("SELECT role FROM users WHERE id = ?", target_user_id)
        if current_role:
            new_role = 1 - current_role[0]["role"]
            db.execute("UPDATE users SET role = ? WHERE id = ?", new_role, target_user_id)
            flash(f"User role updated successfully.")
        else:
            flash("User not found.")
        return redirect("/admin")

    elif action == "room_update":
        target_room_id = request.form.get("room_id")
        if not target_room_id:
            flash("No room specified.")
            return redirect("/admin")

        # Toggle the room's status
        current_status = db.execute("SELECT status FROM rooms WHERE id = ?", target_room_id)
        if current_status:
            new_status = 1 - current_status[0]["status"]
            db.execute("UPDATE rooms SET status = ? WHERE id = ?", new_status, target_room_id)
            flash("Room status updated successfully.")
        else:
            flash("Room not found.")
        return redirect("/admin")

    flash("Invalid action.")
    return redirect("/admin")

####
######## PROFILE
####

# VIEW PROFILE ...only allows get requests
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    '''Only accepts get requests, returns profile INFO, and created ROOMS to profile.html'''
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    if request.method == "GET":
        rooms = db.execute('''SELECT id, name, description, key, status, created_at, updated_at
                 FROM rooms WHERE creator_id=?;''', id)
    return render_template("profile.html", info=info, rooms=rooms)


# EDIT PROFILE 
@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    if request.method == "GET":
        # return the page used to update username and linkedin profile url...
        return render_template("edit_profile.html", info=info)
    else:
        username = request.form.get("username")
        profile_link = request.form.get("profile_link")
        db.execute('''UPDATE users 
            SET username=?, profile_link=? WHERE id=?;''', username, profile_link, id)
        flash("Profile Updated")
        return redirect("/profile")


####
######## ROOMS
####


# ROOMS
@app.route("/rooms", methods=["GET", "POST"])
@login_required
def rooms():
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    if request.method == "GET":
        rooms = db.execute('''SELECT
                rooms.id AS id,
                rooms.name AS name,
                rooms.description AS description,
                rooms.key AS key,
                rooms.status AS status,
                rooms.creator_id AS creator_id,
                rooms.created_at AS created_at,
                rooms.updated_at AS updated_at    
                FROM users
            JOIN members ON users.id = members.user_id
            JOIN rooms ON members.room_id = rooms.id
            WHERE members.user_id=?''', id)# sort the rooms in descending order
        return render_template("rooms.html", rooms=rooms, info=info)
    else:
        action = request.form.get("action")# get the action to be performed
        if action == "join":
            # add the person to the room
            key = request.form.get("key")
            room = db.execute("SELECT * FROM rooms WHERE key=? AND status=?;", key, 1)
            if not room:
                flash("The room with the key provided does not exist or is not active")
                return redirect("/rooms")
            
            # insert the event id and room_id pair in members table
            db.execute("INSERT INTO members (user_id, room_id) VALUES (?, ?);", id, room[0]["id"])
            return redirect("/rooms")
        elif action == "filter":
            status = request.form.get("status")
            if status == "all": return redirect("/rooms")
            elif status == "0" or status == "1": status = int(status)

            # return a list of rooms filtered by closed or open
            rooms = db.execute('''SELECT
                rooms.id AS id,
                rooms.name AS name,
                rooms.description AS description,
                rooms.key AS key,
                rooms.status AS status,
                rooms.creator_id AS creator_id,
                rooms.created_at AS created_at,
                rooms.updated_at AS updated_at    
                FROM users
            JOIN members ON users.id = members.user_id
            JOIN rooms ON members.room_id = rooms.id
            WHERE members.user_id=? AND rooms.status=?''', id, status)
            return render_template("rooms.html", rooms=rooms, info=info)
            
        else:
            # remove the person from the room, if they want to leave
            room_id = request.form.get("room_id")
            db.execute("DELETE FROM members WHERE user_id=? AND room_id=?;", id, room_id)
            flash("You have been removed from the room succesfully")
            return redirect("/rooms")


# CREATE ROOM
@app.route("/rooms/create", methods=["GET", "POST"])
@login_required
def create_room():
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    if request.method == "GET":
        # show the page used to create a new room...rooms must have a description and a unique name
        return render_template("edit_room.html", info=info)
    else:
        status = 0 # inactive until activated by an admin
        name = request.form.get("name")
        description = request.form.get("description")
        key = generate_key(db.execute("SELECT key FROM rooms;"))
        db.execute('''INSERT INTO rooms (name, description, key, status, creator_id) 
                   VALUES (?, ?, ?, ?, ?);''', name, description, key, status, id)
        flash("Request for room creation submitted")
        return redirect("/profile")

# UPDATE ROOM
@app.route("/rooms/update", methods=["GET", "POST"])
@login_required
def update_room():
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    if request.method == "GET":
        # you'll get the room id from wherever the edit  request was sent
        room_id = request.args.get("room_id")
        room = db.execute("SELECT * FROM rooms WHERE id=?;", room_id)[0]
        return render_template("edit_room.html", info=info, room=room)
    else:
        room_id = request.form.get("room_id")
        name = request.form.get("name")
        description = request.form.get("description")
        db.execute('''UPDATE rooms 
            SET name=?, description=? WHERE creator_id=? AND rooms.id=?;''', name, description, id, room_id)
        return redirect("/profile")


####
######## MATES
####

# MATES
@app.route("/mates", methods=["GET", "POST"])
@login_required
def mates():
    id = session["user_id"]
    info = db.execute("SELECT * FROM users WHERE id=?;", id)[0]
    if request.method == "GET":
        rooms = db.execute('''SELECT 
                                members.room_id AS id, 
                                rooms.name AS name
                            FROM members 
                            JOIN rooms ON members.room_id=rooms.id 
                            WHERE members.user_id=?;''', id)
        mates = db.execute(''' SELECT
                                            users.id AS user_id,
                                            users.username AS user_name,
                                            users.profile_link AS profile_link,
                                            rooms.name AS room,
                                            mates.status AS status
                                        FROM users 
                                        JOIN mates ON users.id = mates.user_id2
                                        JOIN rooms ON mates.room_id = rooms.id
                                        WHERE mates.user_id1=? ;''', id)
        return render_template("mates.html", info=info, rooms=rooms, mates=mates)
        # show the person a page to filter mates by rooms/events, and those whose link has been clicked 
    else:
        action = request.form.get("action")
        if action == "filter":
            room_id = request.form.get("room_id")
            status = request.form.get("status")
        
            if status == "all" and room_id == "all":
                mates = db.execute(''' SELECT
                                            users.id AS user_id,
                                            users.username AS user_name,
                                            users.profile_link AS profile_link,
                                            rooms.name AS room,
                                            mates.status AS status
                                        FROM users 
                                        JOIN mates ON users.id = mates.user_id2
                                        JOIN rooms ON mates.room_id = rooms.id
                                        WHERE mates.user_id1=? ;''', id)
                return render_template("mates.html", info=info, mates=mates)
            
            elif status == "all" and room_id != "all":
                mates = db.execute(''' SELECT
                                            users.id AS user_id,
                                            users.username AS user_name,
                                            users.profile_link AS profile_link,
                                            rooms.name AS room,
                                            mates.status AS status
                                        FROM users 
                                        JOIN mates ON users.id = mates.user_id2
                                        JOIN rooms ON mates.room_id = rooms.id
                                        WHERE mates.user_id1=? AND rooms.id=?;''', id, room_id)
                return render_template("mates.html", info=info, mates=mates)
            
            elif status != "all" and room_id == "all":
                mates = db.execute(''' SELECT
                                            users.id AS user_id,
                                            users.username AS user_name,
                                            users.profile_link AS profile_link,
                                            rooms.name AS room,
                                            mates.status AS status
                                        FROM users 
                                        JOIN mates ON users.id = mates.user_id2
                                        JOIN rooms ON mates.room_id = rooms.id
                                        WHERE mates.user_id1=? AND mates.status=?;''', id, status)
                return render_template("mates.html", info=info, mates=mates)
            
            elif status != "all" and room_id != "all":
                mates = db.execute(''' SELECT
                                            users.id AS user_id,
                                            users.username AS user_name,
                                            users.profile_link AS profile_link,
                                            rooms.name AS room,
                                            mates.status AS status
                                        FROM users 
                                        JOIN mates ON users.id = mates.user_id2
                                        JOIN rooms ON mates.room_id = rooms.id
                                        WHERE mates.user_id1=? AND mates.status=? AND rooms.id=?;''', id, status, room_id)
                return render_template("mates.html", info=info, mates=mates)

        elif action == "set_status":
            # get the connection id, set the status to the opposite of what it was before
            user_id2 = request.form.get("mate_id")
            status = 1 - int(request.form.get("status"))
            db.execute('''UPDATE mates
                    SET status=? WHERE user_id1=? AND user_id2=?;''', status, id, user_id2)
            flash("Connection status changed")
            return redirect("/mates")

    

####
######## REGISTER, LOGIN, LOGOUT
####

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("register.html")

    else:
        # Check if the username and password is valid
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        profile_link = request.form.get("profile_link")

        if not is_valid_linkedin_url(profile_link): return apology("Please enter a valid linkedin Profile url", 403)

        if not check(username, password): return apology("Enter username and password to Register")

        # Check if the password and confirmation are both correct
        if password != confirmation: return apology("Password and confirmation password do not match")

        # Check if the username exists in the database
        details = db.execute("SELECT * FROM users WHERE username=?;", username)
        if not details:
            # Enter the user's details into the database if the username doesn't exist
            db.execute("INSERT INTO users (username, hash, profile_link) VALUES (?, ?, ?);",
                       username, generate_password_hash(password), profile_link)
            rows = db.execute("SELECT * FROM users WHERE username=?;", username)

            # Log the user in
            session["user_id"] = rows[0]["id"]
            flash("You have been registered")
            return redirect("/")

        # if the username and password exist
        elif check_password_hash(details[0]["hash"], password) == True:
            return apology("You already have an account with MapleMatch, Login with your username and password")

        # If only the username exists
        else:
            return apology("Please choose a different username, this username has been taken")



# LOG IN
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not check(username, password): return apology("Must Provide username and Password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # Log user in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("You have been logged in")
        return redirect("/")



# LOG OUT
@app.route("/logout", methods=["GET", "POST"])
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    flash("You have logged out")
    return redirect("/")
