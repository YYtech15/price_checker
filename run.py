from flask import Flask, render_template, request, redirect, make_response
import pymysql
from dbutils.pooled_db import PooledDB
import random
import string
import bcrypt
import datetime
import json

app = Flask(__name__)

with open("database.json", "r") as f:
    config = json.load(f)
config["autocommit"] = False
config["cursorclass"] = pymysql.cursors.DictCursor

database = PooledDB(pymysql, 4, **config)


@app.route("/add", methods=["POST"])
def add_item():
    user_id = check_header(request.headers)
    if not user_id:
        return {"status": False, "msg": "need login"}
    post_data = request.get_json()
    try:
        sql = "".format(post_data["item_id"], user_id)
        with database.connection().cursor() as cur:
            cur.execute(sql)
            cur.commit()
        return {"status": True}
    except Exception as e:
        print(e)
        return {"status": False, "msg": "missing information"}


@ app.route("/remove", methods=["POST"])
def remove_item():
    user_id = check_header(request.headers)
    if not user_id:
        return {"status": False, "msg": "need login"}
    post_data = request.get_json()
    sql = "".format(post_data["item_id"], user_id)
    with database.connection().cursor() as cur:
        cur.execute(sql)
    return {"status": True}


@app.route("/info", methods=["GET"])
def get_items():
    user_id = check_header(request.headers)
    if not user_id:
        return {"status": False, "msg": "need login"}
    sql = "".format(user_id)
    with database.connection().cursor() as cur:
        cur.execute(sql)
    return {"status": True}

# Example request body
# {
#    "address": id,
#    "pass": pass
# }
#
# Example response body
#{"status": True}


@ app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not (data["address"] and data["pass"]):
        return {"status": False}
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(data["pass"].encode(), salt).decode()
    sql = "INSERT INTO user(address,pass) values('{}','{}')".format(
        data["address"], hash)
    with database.connection().cursor() as cur:
        cur.execute(sql)
    return {"status": True}


# Example request body
# {
#    "address": id,
#    "pass": pass
# }
#
# Example response body
#{"status": True, "token": token}

@ app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not (data["address"] and data["pass"]):
        return {"status": False, "msg": "missing data"}
    sql = "SELECT id,pass from user where address='{}'".format(data["address"])
    with database.connection().cursor() as cur:
        cur.execute(sql)
        try:
            record = cur.fetchone()
            if not bcrypt.checkpw(data["pass"].encode(), record["pass"].encode()):
                return {"status": False, "msg": "user not found"}
        except:
            return {"status": False, "msg": "user not found"}
        token = random_name(24)
        sql = "INSERT INTO token(user_id,token) values('{}','{}')".format(
            record["id"], token)
        cur.execute(sql)
    return {"status": True, "token": token}


@ app.route("/check")
def check_login():
    user_id = check_token(request.headers)
    if user_id:
        return user_id
    return ""


@ app.route("/robots.txt")
def robot():
    return "User-agent: * \nDisallow: /"


def check_header(header: dict):
    try:
        token = header["Authorization"].split(" ").pop()
        return check_token(token)
    except:
        return False


def check_token(token: str):
    dt = datetime.datetime.today() - datetime.timedelta(days=3)
    with database.connection().cursor() as cur:
        sql = "DELETE FROM token WHERE created_time < '{}';".format(str(dt))
        cur.execute(sql)
        sql = "SELECT user_id from token where token='{}'".format(token)
        cur.execute(sql)
        record = cur.fetchone()
    try:
        return record["user_id"]
    except:
        return False


def cookie_dict(cookie: str):
    items = cookie.split(";")
    result = dict()
    for i in items:
        try:
            k, v = i.split("=")
            result[k.strip()] = v.strip()
        except:
            pass
    return result


def user_search(token: str):
    sql = "SELECT * FROM token where token={}".format(token)
    with database.connection().cursor() as cur:
        cur.execute(sql)
        data = cur.fetchone()
    if data:
        return data["user_id"]
    else:
        return False


def random_name(n: int):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


if __name__ == "__main__":
    app.run(port=9000, debug=True)
