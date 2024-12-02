from flask import redirect, render_template, session
from functools import wraps
import json
import re
import uuid


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def check(username, password):
    if not username or not password:
        return False
    return True

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def write_json(data, file_path):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)  # indent=4 makes the JSON file more readable


def is_valid_linkedin_url(url):
    if not url: return False
    pattern = r"^(https?:\/\/)?(www\.)?linkedin\.com\/(in|pub|company|school)\/[a-zA-Z0-9-_%]+(\/)?$"
    return re.match(pattern, url) is not None


def generate_key(keys):
    keys_set = set(map(lambda x: x["key"], keys)) 
    while True:
        unique_id = uuid.uuid4()
        unique_number = unique_id.int % 1000000
        key = str(unique_number).zfill(6)
        if key not in keys_set:
            return key

        


