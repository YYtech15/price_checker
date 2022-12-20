from ast import keyword
# 取得したデータ操作とcsv出力のため : pandas
import pandas as pd
# APIを叩く用 ： request
import requests,json,datetime,os,re
from time import sleep

appId = '1072507588405161320'

# リクエストするURL()
REQUEST_URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'

WANT_ITEMS = [
    'itemName',         # 商品名
    'itemPrice',        # 価格
    'itemUrl',          # 商品url
    'shopName'          # 店名
    'itemCaption',      # JANデータだけの取り出し必要
    'postageFlag'       # 送料フラグ 0->全て,1->送料込み
]

MAX_PAGE = 5
HITS_PER_PAGE = 30
# リクエストを送る際のパラメータをdict型で書く
req_params = {
    'applicationId':appId,    # 楽天の開発者向けページで取得したアプリID
    'format':'json',        # 
    'formatVersion':'2',    # 
    'keyword':'',           # 検索したい文字列を指定
    'hits':HITS_PER_PAGE,   # 
    'sort':'+itemPrice',    # 
    'page':0,               # 取得するページ　->　ループを回すことで複数ページの商品情報取得可
    'minPrice':100          # 
}


# 検索データ取得
def get_keyword():

    #商品記載テキストファイルからキーワード配列作成
    with open('.\list_item_name.txt','r',encoding='utf-8') as f:
        # 改行ごとに読み取る
        item_info = list(map(str,f.read().split('\n')))

    search_Rakuten(item_info)

# 楽天のデータ検索
def search_Rakuten(arg_item_info):

    #キーワードループ
    for keyword in arg_item_info:

        #初期設定
        keyword = keyword.replace('\u3000',' ')
        req_params['keyword'] = keyword
        df = pd.DataFrame(columns=WANT_ITEMS)

        # APIを実行してreq_paramsのデータを取得
        res = requests.get(REQUEST_URL,req_params)
        response_code = res.status_code             # ステータスコード取得
        data = res.json()                           # jsonにデコードする
        result = list()

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
            result.append(item)

        if response_code != 200:
            # エラー出力
            print(f"ErrorCode --> {response_code}\nError --> {result['error']}")
        else:
            #返ってきた商品数の数が0の場合は終了
            if result['hits'] == 0:
                return

        tmp_df = pd.DataFrame(result['Items'])[WANT_ITEMS]
        df = pd.concat([df,tmp_df],ignore_index=True)

        #リクエスト制限回避
        sleep(1)
        return result

if __name__ == '__main__':
    janCodes = list()
    while True:
        code = input("{}番目のJANコードを入力してください: ".format(len(janCodes) + 1))
        if code == "exit":
            break
        else:
            janCodes.append(code)

    response = get_Rakuten(*janCodes)
    with open("sample.json", "w") as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

    print(response)