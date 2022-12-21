# 主要ライブラリ
from flask import Flask, render_template, request, redirect, make_response

# 外部ライブラリ
import bcrypt
import pymysql
from dbutils.pooled_db import PooledDB

# 組み込みライブラリ
import random
import string
import datetime
import json
import threading
from time import sleep

# 自作モジュール
from Yahoo import Yahoo

app = Flask(__name__)

with open("config.json", "r") as f:
    config = json.load(f)
database_config = config["database"]
database_config["autocommit"] = True
database_config["cursorclass"] = pymysql.cursors.DictCursor

database = PooledDB(pymysql, 4, **database_config)

yahoo = Yahoo(config["Yahoo_App_ID"])


# cors許可
@app.after_request
def after_request(response):
    if config["Access-Control-Allow-Origin"]:
        response.headers["Access-Control-Allow-Origin"] = config["Access-Control-Allow-Origin"]
    return response


# Example request body
# {
#    "item_code": <janCode:str>
# }
#
# Example response body
#{"status": True}


@app.route("/add", methods=["POST"])
def add_item():
    user_id = check_header(request.headers)
    if not user_id:
        return {"status": False, "msg": "need login"}
    try:
        post_data = request.get_json()
        sql = "INSERT INTO registerd_items(user_id,item_code) VALUES({},'{}')".format(
            user_id, post_data["item_code"])
        with database.connection().cursor() as cur:
            cur.execute(sql)
            sql = "INSERT IGNORE INTO item_information(item_code) VALUES('{}')".format(
                post_data["item_code"])
            cur.execute(sql)
        return {"status": True}
    except Exception as e:
        print(e)
        return {"status": False, "msg": "missing information"}


# Example request body
# {
#    "item_code": <janCode:str>
# }
#
# Example response body
#{"status": True}

@ app.route("/remove", methods=["POST"])
def remove_item():
    user_id = check_header(request.headers)
    if not user_id:
        return {"status": False, "msg": "need login"}
    post_data = request.get_json()
    sql = "DELETE FROM registerd_items where item_code={} and user_id={}".format(
        post_data["item_code"], user_id)
    with database.connection().cursor() as cur:
        cur.execute(sql)
    return {"status": True}


# Example response body
# {
#  "status" : <process_status:bool>,
#  "items": [
#    {
#      "image": <image_url:str>,
#      "janCode": <jan_code:str>,
#      "name": <product_name:str>,
#      "price": <product_price:int>,
#      "seller": <seller_name:str>,
#      "shipping": <shipping_plan:str>,
#      "url": <item_page_url:str>
#    }
#  ]
# }
@app.route("/info", methods=["GET"])
def get_items():
    user_id = check_header(request.headers)
    if not user_id:
        return {"status": False, "msg": "need login"}
    sql = """SELECT registerd_items.item_code,item_information.name,item_information.price,item_information.url,item_information.image,item_information.seller,item_information.shipping
            FROM registerd_items
            LEFT JOIN item_information ON registerd_items.item_code = item_information.item_code
            WHERE registerd_items.user_id = {}""".format(user_id)
    with database.connection().cursor() as cur:
        cur.execute(sql)
        data = cur.fetchall()
    return {"status": True, "items": data}


# Request query paramater
# q : keyword
#
# Example response body
# {
#  "status" : <process_status:bool>,
#  "items": [
#    {
#      "image": <image_url:str>,
#      "janCode": <jan_code:str>,
#      "name": <product_name:str>,
#      "price": <product_price:int>,
#      "seller": <seller_name:str>,
#      "shipping": <shipping_plan:str>,
#      "url": <item_page_url:str>
#    }
#  ]
# }

@app.route("/search", methods=["GET"])
def search_items():
    user_id = check_header(request.headers)
    if not user_id:
        return {"status": False, "msg": "need login"}
    keyword = request.args.get('q')
    if keyword:
        Y_data = yahoo.search(keyword)
        return {"status": True, "items": Y_data}
    else:
        return {"status": False, "msg": "missing prameter"}


# Example request body
# {
#    "address": <email_address:str>,
#    "pass": <password:str>
# }
#
# Example response body
#{"status": True}


@ app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not (data["address"] and data["pass"]):
        return {"status": False, "msg": "missing data"}
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(data["pass"].encode(), salt).decode()
    sql = "INSERT INTO user(address,pass) values('{}','{}')".format(
        data["address"], hash)
    with database.connection().cursor() as cur:
        cur.execute(sql)
    return {"status": True}


# Example request body
# {
#    "address": <email_address:str>,
#    "pass": <password:str>
# }
#
# Example response body
# {"status": True, "token": <token:str>}

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

# Example response body
# {"status": True}


@ app.route("/check")
def check_login():
    user_id = check_token(request.headers)
    if user_id:
        return {"status": True}
    return {"status": False}


@ app.route("/robots.txt")
def robot():
    return "User-agent: * \nDisallow: /"


def check_header(header: dict):
    try:
        token = header["Authorization"].split(" ").pop()
        return check_token(token)
    except Exception as e:
        print(e)
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


class Crawler():
    def __init__(self,Interval:int):
        self.Interval = Interval

    def __del__(self):
        self.end_flag = True
        self.thread.join()

    def start(self):
        self.end_flag = False
        self.previous_time = datetime.datetime.today()-datetime.timedelta(minutes=60)
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def stop(self):
        self.end_flag = True
        self.thread.join()

    def loop(self):
        while not self.end_flag:
            if (self.previous_time < datetime.datetime.today()):
                self.update()
                self.previous_time = datetime.datetime.today()+datetime.timedelta(minutes=self.Interval)
            for i in range(30):
                sleep(2)
                if self.end_flag:
                    break

    def update(self):
        cur = database.connection().cursor()
        cur.execute("SELECT item_code FROM item_information")
        data = cur.fetchall()
        for d in data:
            res = yahoo.get(d["item_code"])
            sql = """UPDATE item_information SET 
            name = '{name}',price={price},url='{url}',image='{image}',seller='{seller}',shipping='{shipping}'
            where item_code={item_code}""".format(**res[d["item_code"]], **d)
            cur.execute(sql)


crawler = Crawler(60)
if __name__ == "__main__":
    crawler.start()
    app.run(port=9002, debug=True)
