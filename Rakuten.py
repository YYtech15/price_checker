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
        self.MAX_PAGE = 1

        # getでリクエストを送る際のパラメータ
        self.req_params = {
            "applicationId": "1072507588405161320",
            "format":"json",
            "formatVersion":"2",
            "keyword":"",
            "hits": 30,
            "sort": "-reviewAverage",
            "page": 0,
            "NGKeyword" : "中古"
        }

    # 検索データ取得
    def get(self, *Jan_code:str):
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
            if response_code != 200:
                # エラー出力
                print(f"ErrorCode --> {response_code}\nError --> {data['error']}")
                break
            minPrice = data["Items"][0]['itemPrice']
            index = 0
            for k in range(data["hits"]):
                if data["Items"][k]['itemPrice'] < minPrice:
                    minPrice = data["Items"][k]['itemPrice']
                    index = k
            result[j] = {
                'name' : data["Items"][index]['itemName'],
                'price' : data["Items"][index]['itemPrice'],
                'url' : data["Items"][index]['itemUrl'],
                'seller' : data["Items"][index]['shopName'],
                'shipping' : data["Items"][index]['postageFlag']
            }
        return result


    # 楽天のデータ検索
    # keywordは最大128文字の１バイト文字
    def search(self, keyword: str):
        result = list()
        # 検索ワード
        self.req_params['keyword'] = keyword
        cnt = 1

        #ページループ
        while True:
            self.req_params['page'] = cnt
            # APIを実行してreq_paramsのデータを取得
            res = requests.get(self.REQUEST_URL, self.req_params)
            response_code = res.status_code             # ステータスコード取得
            data = res.json()                           # jsonにデコードする

            if response_code != 200:
                # エラー出力
                print(f"ErrorCode --> {response_code}\nError --> {data['error']}")
                break
            index = 0
            #返ってきた商品数の数が0の場合はループ終了
            for k in range(data["hits"]):
                if self.extract_JanCode(data["Items"][k]["itemCaption"])=="":
                    continue
                item = {
                    'name' : data["Items"][k]['itemName'],
                    'price' : data["Items"][k]['itemPrice'],
                    'janCode': self.extract_JanCode(data["Items"][k]['itemCaption']),
                    'url' : data["Items"][k]['itemUrl'],
                    'image' : data["Items"][k]['mediumImageUrls'],
                    'seller' : data["Items"][k]['shopName'],
                    'shipping' : data["Items"][k]['postageFlag']
                }
                result.append(item)

            if cnt == self.MAX_PAGE:
                break
            cnt += 1
            #リクエスト制限回避
            sleep(1)

        return result
# 説明文の中に含まれるJANコードの抜き出し
    def extract_JanCode(self, itemCaption :str):
        idx = itemCaption.find('JAN')
        pattern = list()
        if idx != -1:
            pattern = re.split('[:(/\■)【：】]', itemCaption[idx+1:idx+15])
            for i in pattern:
                # JANコードがあれば返り値で返す
                if check_JAN(i):
                    return i
                else:
                    continue
        else:
            return ""

def check_JAN(jan_code: str):
    length = len(jan_code)
    if length == 8:
        jan_code = "00000"+jan_code
        length = len(jan_code)
    if length == 13:
        even = 0
        odd = 0
        for i in range(1, 12, 2):
            even += int(jan_code[i])
        even *= 3
        for i in range(0, 12, 2):
            odd += int(jan_code[i])
        result = (odd+even) % 10
        if str(10-result) == jan_code[12] or str(result) == jan_code[12]:
            return True
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

    with open("config_rakuten.json", "r") as f:
        config = json.load(f)
    rakuten = Rakuten(config["Rakuten_App_ID"])
    res = rakuten.search(janCodes)

    with open("sample.json", "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=4)

    print(res)