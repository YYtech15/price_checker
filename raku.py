# APIを叩く用 ： request
import requests,json,re
from time import sleep

class Rakuten:
    def __init__(self, appId:str) -> None:
        self.appId = appId

        # リクエストするURL()
        self.REQUEST_URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'

        # 取得するデータ項目
        self.Want_Items = ["itemName", "itemPrice", "itemUrl", "url",  "shopName", "itemCaption", "postageFlag"]
        self.MAX_PAGE = 5

        # getでリクエストを送る際のパラメータ
        self.req_params_get = {
            "applicationId": "1072507588405161320",
            "format":"json",
            "formatVersion":"2",
            "keyword":"",
            "hits": 30,
            "sort":"+itemPrice",
            "page": 0
        }
        # searchでリクエストを送る際のパラメータ
        self.req_params_search = {
            "applicationId": "1072507588405161320",
            "format": "json",
            "formatVersion": "2",
            "keyword": "",
            "hits": 30,
            "sort": "-reviewAverage",
            "page": 0
        }

    # 検索データ取得
    def get(self, Jan_code):
        result = dict()
        for j in Jan_code:
            # 正しいJANコードか判定
            if len(j) != 8 and len(j) != 13:
                result[j] = {"status": False}
                continue
            cnt = 1
            self.req_params_get['keyword'] = j

            #ページループ
            while True:
                self.req_params_get['page'] = cnt
                # APIを実行してreq_paramsのデータを取得
                res = requests.get(self.REQUEST_URL, self.req_params_get)
                response_code = res.status_code             # ステータスコード取得
                data = res.json()                           # jsonにデコードする

                if response_code != 200:
                    # エラー出力
                    print(f"ErrorCode --> {response_code}\nError --> {data['error']}")
                    break
                else:
                    #返ってきた商品数の数が0の場合はループ終了
                    if res['hits'] == 0:
                        break

                    if data["itemPrice"] < minPrice:
                        minPrice = data["itemPrice"]

                    result[j] = {
                        'name' : data['itemName'],
                        'price' : data['itemPrice'],
                        'url' : data['itemUrl'],
                        'seller' : data['shopName'],
                        'shipping' : data['postageFlag']
                    }

                if cnt == self.MAX_PAGE:
                    break
                cnt += 1
                #リクエスト制限回避
                sleep(1)
        return result


    # 楽天のデータ検索
    # keywordは最大128文字の１バイト文字
    def search(self, keyword: str):
        # 検索ワード
        keyword = keyword.replace('\u3000',' ')
        self.req_params_search['keyword'] = keyword
        cnt = 1

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
                break
            else:
                #返ってきた商品数の数が0の場合はループ終了
                if res['hits'] == 0:
                    break

                if self.extract_JanCode(data["itemCaption"])=="":
                    continue
                item = {
                    'name' : data['itemName'],
                    'price' : data['itemPrice'],
                    'janCode': self.extract_JanCode(data['itemUrl']),
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

    def extract_JanCode(itemUrl :str):
        a = list()
        a = itemUrl.split('/')
        if a[4].isdigit():
            if len(a[4]) == 8 or len(a[4]) == 13:
                return a[4]
        else:
            return ""


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
    rakuten = Rakuten(config["Rakuten_App_ID"])
    response = rakuten.get(janCodes)

    with open("sample.json", "w") as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

    print(response)