import requests
import json
from urllib.parse import quote,unquote



class Yahoo:
    def __init__(self,appId:str) -> None:
        self.appId=appId


    def get(self,*JAN_codes: str):
        results = dict()
        for j in JAN_codes:
            if len(j) != 8 and len(j) != 13:
                results[j] = {"status": False}
                continue
            url = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch?appid={}&sort=%2Bprice&results=1&condition=new&jan_code={}".format(
                self.appId, j)
            r = requests.get(url)
            data = r.json()

            d = data["hits"][0]

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


    def search(self,query: str):
        url = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch?appid={}&query={}".format(
            self.appId, query)
        r = requests.get(url)
        data = r.json()
        results = list()
        for d in data["hits"]:
            if d["janCode"]=="":
                continue
            item = {
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
    print("情報取得したい商品のJANコードを入力してください。終了する場合はexitと入力してください。")
    while True:
        code = input("{}番目のJANコードを入力してください: ".format(len(jan_codes)+1))
        if code == "exit":
            break
        else:
            jan_codes.append(code)

    with open("config.json", "r") as f:
        config = json.load(f)
    yahoo = Yahoo(config["Yahoo_App_ID"])
    res = yahoo.get(*jan_codes)
    
    with open("example.json", "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
    print(res)