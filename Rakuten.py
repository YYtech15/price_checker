from ast import keyword
# 取得したデータ操作とcsv出力のため : pandas
import pandas as pd
import numpy as np
# APIを叩く用 ： request
import requests,json,datetime,os,re
from time import sleep

# リクエストするURL()
REQUEST_URL = 'https://app.rakuten.co.jp/'\
'services/api/IchibaItem/Search/20170706'
WANT_ITEMS = [
    'itemCaption',      # JAN
    'itemPrice',        # 価格
    'itemUrl'           # 商品url
    # 'postageFlag'  送料フラグ 0->全て,1->送料込み
]

MAX_PAGE = 5
HITS_PER_PAGE = 30

# 日時指定
start_time = datetime.datetime.today()
this_date = format(start_time,'%Y%m%d')
path_output_dir = f'./output/{this_date}'

# リクエストを送る際のパラメータをdict型で書く
req_params = {
    'applicationId':'1072507588405161320',    # 楽天の開発者向けページで取得したアプリID
    'format':'json',        # 
    'formatVersion':'2',    # 
    'keyword':'',           # 検索したい文字列を指定
    'hits':HITS_PER_PAGE,   # 
    'sort':'+itemPrice',    # 
    'page':0,               # 取得するページ　->　ループを回すことで複数ページの商品情報取得可
    'minPrice':100          # 
}

def main():

    #実行日日付フォルダ作成
    if not os.path.isdir(path_output_dir):
        os.mkdir(path_output_dir)

    #商品記載テキストファイルからキーワード配列作成
    with open('.\list_item_name.txt','r',encoding='utf-8') as f:
        # 改行ごとに読み取る
        item_info = list(map(str,f.read().split('\n')))

    create_output_data(item_info)

    print(f"{'-'*10}")

# 出力データを作る関数
def create_output_data(arg_item_info):

    #キーワードループ
    for keyword in arg_item_info:

        #初期設定
        count = 1
        keyword = keyword.replace('\u3000',' ')
        req_params['keyword'] = keyword
        path_file = f'{path_output_dir}/{keyword}.csv'
        df = pd.DataFrame(columns=WANT_ITEMS)


        print(f"{'-'*10}\nNowSearchWord --> {keyword}")

        #ページループ
        while True:

            req_params['page'] = count
            response = requests.get(REQUEST_URL,req_params)
            response_code = response.status_code
            result = response.json()

            if response_code != 200:
                print(f"ErrorCode --> {response_code}\nError --> {result['error']}\nPage --> {count}")
            else:

                #返ってきた商品数の数が0の場合はループ終了
                if result['hits'] == 0:
                    break

                tmp_df = pd.DataFrame(result['Items'])[WANT_ITEMS]
                df = pd.concat([df,tmp_df],ignore_index=True)

            if count == MAX_PAGE:
                break

            count += 1

            #リクエスト制限回避
            sleep(1)

        df.to_csv(path_file,index=False,encoding="utf_8_sig",sep=",")
        print(f"Finished!!")

if __name__ == '__main__':
    main()