import requests
import json


appId = ""

def set_appId(appId:str):
    appId = appId


def get_yahoo(*JAN_codes: str):
    results = dict()
    for j in JAN_codes:
        if len(j) != 8 and len(j) != 13:
            results[j] = {"status": False}
            continue
        url = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch?appid={}&jan_code={}".format(
            appId, j)
        r = requests.get(url)
        data = r.json()

        min_price = data["hits"][0]["price"]
        min_price_index = 0
        for d in data["hits"]:
            if d["price"] < min_price:
                min_price = d["price"]
                min_price_index = d["index"]-1

        d = data["hits"][min_price_index]

        results[j] = {
            "status": True,
            "name": d["name"],
            "price": d["price"],
            "url": d["url"],
            "image": d["image"]["medium"],
            "seller": d["seller"]["name"],
            "shipping": d["shipping"]["name"]
        }
    return results


def search_yahoo(query: str):
    url = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch?appid={}&query={}".format(
        appId, query)
    r = requests.get(url)
    data = r.json()
    results = list()
    for d in data["hits"]:
        if d["janCode"]=="":
            continue
        item = {
            "status": True,
            "name": d["name"],
            "price": d["price"],
            "janCode":d["janCode"],
            "url": d["url"],
            "image": d["image"]["medium"],
            "seller": d["seller"]["name"],
            "shipping": d["shipping"]["name"]
        }
        results.append(item)
    return results


if __name__ == "__main__":
    jan_codes = list()
    while True:
        code = input("{}番目のJANコードを入力してください: ".format(len(jan_codes)+1))
        if code == "exit":
            break
        else:
            jan_codes.append(code)
    res = get_yahoo(*jan_codes)
    with open("example.json", "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=4)

    print(res)
