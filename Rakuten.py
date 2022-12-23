# APIを叩く用 ： request
import requests
import json
import re
from time import sleep
from checkdigit import check_code


class Rakuten:
    def __init__(self, appId: str) -> None:
        self.appId = appId

        # リクエストするURL()
        self.REQUEST_URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'

        # 取得するデータ項目
        self.Want_Items = ["itemName", "itemPrice", "itemUrl",
                           "url",  "shopName", "itemCaption", "postageFlag"]
        self.MAX_PAGE = 1

        # getでリクエストを送る際のパラメータ
        self.req_params = {
            "applicationId": "1072507588405161320",
            "format": "json",
            "formatVersion": "2",
            "keyword": "",
            "hits": 30,
            "sort": "-reviewAverage",
            "page": 0,
            "NGKeyword": "中古"
        }

    # 検索データ取得
    def get(self, *Jan_code: str):
        result = dict()
        for j in Jan_code:
            # 正しいJANコードか判定
            if len(j) != 8 and len(j) != 13:
                result[j] = {"status": False}
                continue
            self.req_params['keyword'] = j
            self.req_params['page'] = 1

            # APIを実行してreq_paramsのデータを取得
            res = requests.get(self.REQUEST_URL, self.req_params)
            response_code = res.status_code             # ステータスコード取得
            data = res.json()                           # jsonにデコードする

            if response_code == 429:
                result[j] = {
                    "status": False
                }
            elif response_code != 200:
                # エラー出力
                print(
                    f"ErrorCode --> {response_code}\nError --> {data['error']}")
                break
            minPrice = data["Items"][0]['itemPrice']
            index = 0
            for k in range(data["hits"]):
                if data["Items"][k]['itemPrice'] < minPrice:
                    minPrice = data["Items"][k]['itemPrice']
                    index = k
            shippingFlag = "送料別"
            if data["Items"][index]['postageFlag']:
                shippingFlag = "送料無料"
            result[j] = {
                "status": True,
                'name': data["Items"][index]['itemName'],
                'price': data["Items"][index]['itemPrice'],
                'url': data["Items"][index]['itemUrl'],
                'image': data["Items"][index]['mediumImageUrls'][0],
                'seller': data["Items"][index]['shopName'],
                'shipping': shippingFlag
            }
            if len(Jan_code) > 1:
                sleep(1)
        return result

    # 楽天のデータ検索
    # keywordは最大128文字の１バイト文字

    def search(self, keyword: str):
        result = list()
        # 検索ワード
        self.req_params['keyword'] = keyword
        cnt = 1

        # ページループ
        while True:
            self.req_params['page'] = cnt
            # APIを実行してreq_paramsのデータを取得
            res = requests.get(self.REQUEST_URL, self.req_params)
            response_code = res.status_code             # ステータスコード取得
            data = res.json()                           # jsonにデコードする

            if response_code != 200:
                # エラー出力
                print(
                    f"ErrorCode --> {response_code}\nError --> {data['error']}")
                break
            index = 0
            # 返ってきた商品数の数が0の場合はループ終了
            for k in range(data["hits"]):
                janCode = extract_JanCode(data["Items"][k]["itemCaption"])
                if not janCode:
                    continue
                item = {
                    'name': data["Items"][k]['itemName'],
                    'price': data["Items"][k]['itemPrice'],
                    'janCode': janCode,
                    'url': data["Items"][k]['itemUrl'],
                    'image': data["Items"][k]['mediumImageUrls'][0],
                    'seller': data["Items"][k]['shopName'],
                    'shipping': data["Items"][k]['postageFlag']
                }
                result.append(item)

            if cnt == self.MAX_PAGE:
                break
            cnt += 1
            # リクエスト制限回避
            sleep(1)

        return result


# 説明文の中に含まれるJANコードの抜き出し
number = re.compile(r"\d{8,13}")


def extract_JanCode(itemCaption: str):
    r = number.search(itemCaption)
    if not r:
        return False
    else:
        n = r.group()
        if check_code(n):
            return n
        else:
            return False


if __name__ == '__main__':
    # janCodes = list()
    # while True:
    #     code = input("{}番目のJANコードを入力してください: ".format(len(janCodes) + 1))
    #     if code == "exit":
    #         break
    #     else:
    #         janCodes.append(code)
    # with open("config_rakuten.json", "r") as f:
    #     config = json.load(f)
    # rakuten = Rakuten(config["Rakuten_App_ID"])
    # res = rakuten.search(*janCodes)

    janCodes = input("入力してください:")

    with open("config.json", "r") as f:
        config = json.load(f)
    rakuten = Rakuten(config["Rakuten_App_ID"])
    res = rakuten.search(janCodes)

    with open("example.json", "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=4)

    print(res)
