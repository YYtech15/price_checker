# 取得したデータ操作 : pandas
import pandas as pd
# APIを叩く用 ： request
import requests,json
from time import sleep

class Rakuten:
    def __init__(self, appId:str) -> None:
        self.appId = appId

        # リクエストするURL()
        self.REQUEST_URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'

        # 取得するデータ項目
        self.WANT_ITEMS = [
            'itemName',         # 商品名
            'itemPrice',        # 価格
            'itemUrl',          # 商品url
            'shopName'          # 店名
            'itemCaption',      # JANデータだけの取り出し必要
            'postageFlag'       # 送料フラグ 0->全て,1->送料込み
        ]

        self.MAX_PAGE = 5
        self.HITS_PER_PAGE = 30

        # getでリクエストを送る際のパラメータをdict型で書く
        self.req_params_get = {
            'applicationId': appId,  # 楽天の開発者向けページで取得したアプリID
            'format':'json',        # JSONを指定
            'formatVersion':'2',    # formatVersion=2 を設定すると、レスポンスフォーマット（JSON）が改善される。
            'keyword':'',           # 検索したい文字列を指定
            'hits': self.HITS_PER_PAGE,  # 各ページに表示する結果の数
            'sort':'+itemPrice',    # 昇順の商品価格でソート
            'page':0,               # 取得するページ -> ループを回すことで複数ページの商品情報取得可
        }

        # searchでリクエストを送る際のパラメータをdict型で書く
        self.req_params_search = {
            'applicationId':appId,
            'format':'json',
            'formatVersion':'2',
            'keyword':'',
            'hits': self.HITS_PER_PAGE,
            'sort':'-reviewAverage',    # 高評価順にソート
            'page':0,
        }

        '''
            In case of formatVersion=2 :
            Our API response will be returned in Array format as the followings.
            You can use notation items[0].itemName
            To access itemName parameter.
        '''

    # 検索データ取得
    def get(self, *Jan_code: str):
        result = dict()

        for j in Jan_code:
            if len(j) != 8 and len(j) != 13:
                result[j] = {"status": False}
                continue
            res = requests.get(self.REQUEST_URL, self.req_params_get)
            data = res.json()

        #商品記載テキストファイルからキーワード配列作成
        with open('.\list_item_name.txt','r',encoding='utf-8') as f:
            # 改行ごとに読み取る
            item_info = list(map(str,f.read().split('\n')))

        self.search(item_info)

    # 楽天のデータ検索
    # keywordは最大128文字の１バイト文字
    def search(self, keyword: str):

        # 検索ワード
        keyword = keyword.replace('\u3000',' ')
        self.req_params_search['keyword'] = keyword
        df = pd.DataFrame(columns = self.WANT_ITEMS)

        # APIを実行してreq_paramsのデータを取得
        res = requests.get(self.REQUEST_URL, self.req_params_search)
        response_code = res.status_code             # ステータスコード取得
        data = res.json()                           # jsonにデコードする
        result = dict()                             # 整形した結果を格納する辞書変数を宣言

        if response_code != 200:
            # エラー出力
            print(f"ErrorCode --> {response_code}\nError --> {data['error']}")
        else:
            #返ってきた商品数の数が0の場合はデータなし
            for d in data['hits']:
                item = {
                    "status": True,
                    'itemName' : d['itemName'],
                    'itemPrice' : d['itemPrice'],
                    'itemUrl' : d['itemUrl'],
                    'shopName' : d['shopName'],
                    'itemCaption' : d['itemCaption'],
                    'postageFlag' : d['postageFlag']
                }
                result.append(item)
            #リクエスト制限回避
            sleep(1)
            return result

        tmp_df = pd.DataFrame(result['Items'])[self.WANT_ITEMS]
        df = pd.concat([df,tmp_df],ignore_index=True)

        return result

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
    response = rakuten.get(*janCodes)

    with open("sample.json", "w") as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

    print(response)