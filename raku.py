# APIを叩く用 ： request
import requests,json
from time import sleep

class Rakuten:
    def __init__(self, appId:str, Want_Items:list, req_params_get:dict, req_params_search:dict) -> None:
        self.appId = appId

        # リクエストするURL()
        self.REQUEST_URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'

        # 取得するデータ項目
        self.Want_Items = Want_Items
        self.MAX_PAGE = 5

        # getでリクエストを送る際のパラメータ
        self.req_params_get = req_params_get
        # searchでリクエストを送る際のパラメータ
        self.req_params_search = req_params_search

    # 検索データ取得
    def get(self, *Jan_code: str):
        result = dict()

        for j in Jan_code:
            if len(j) != 8 and len(j) != 13:
                result[j] = {"status": False}
                continue
            res = requests.get(self.REQUEST_URL, self.req_params_get)
            data = res.json()
            minPrice = data["hits"][0]["itemPrice"]
            minPrice_index = 0
            for d in data["hits"]:
                if d["itemPrice"] < minPrice:
                    minPrice = d["itemPrice"]
                    minPrice_index = d["index"] - 1

            d = data["hits"][minPrice_index]

            result[j] = {
                "status": True,
                "name": d["itemName"],
                "price": d["itemPrice"],
                "url": d["url"],
                "seller": d["shopName"],
                "shipping": d["postageFlag"]
            }

        return result

    # 楽天のデータ検索
    # keywordは最大128文字の１バイト文字
    def search(self, keyword: str):
        # 検索ワード
        cnt = 1
        self.req_params_search['keyword'] = keyword

        #ページループ
        while True:
            self.req_params_search['page'] = cnt
            # APIを実行してreq_paramsのデータを取得
            res = requests.get(self.REQUEST_URL, self.req_params_search)
            response_code = res.status_code             # ステータスコード取得
            data = res.json()                           # jsonにデコードする
            result = list()

            if response_code != 200:
                # エラー出力
                print(f"ErrorCode --> {response_code}\nError --> {data['error']}")
            else:
                #返ってきた商品数の数が0の場合はループ終了
                if res['hits'] == 0:
                    break

                if self.extract_JanCode(d["itemCaption"])=="":
                    continue
                item = {
                    'name' : data['itemName'],
                    'price' : data['itemPrice'],
                    "janCode": self.extract_JanCode(data["itemCaption"]),
                    'url' : data['itemUrl'],
                    'seller' : data['shopName'],
                    'shipping' : data['postageFlag']
                }
                result.append(item)

            if cnt == self.MAX_PAGE:
                break
            cnt += 1
            #リクエスト制限回避
            sleep(1)

        return result

    def extract_JanCode(itemCaption :str):
        return itemCaption


if __name__ == '__main__':
    janCodes = list()
    while True:
        code = input("{}番目のJANコードを入力してください: ".format(len(janCodes) + 1))
        if code == "exit":
            break
        else:
            janCodes.append(code)

    with open("config_rakuten.json", "r") as f:
        config = json.load(f)
    rakuten = Rakuten(config["Rakuten_App_ID"],config["Want_Items"],config["req_params_get"],config["req_params_search"])
    response = rakuten.get(*janCodes)

    with open("sample.json", "w") as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

    print(response)