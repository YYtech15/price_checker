# CSVファイルのデータをpythonを利用してMySQLに流し込む

# CSVファイルを読み書きするため、標準ライブラリcsvを使用する。
import csv
# MySQLの操作
import mysql.connector

# 自分のローカルのMysqlへの接続
connect = mysql.connector.connect(
    user='root',
    password='',
    host='localhost',
    database='itempricedb',
    charset='utf8')
cursor = connect.cursor()

with open('./output/20221220/iPad.csv', 'r') as infile:
    count = 0
    for line in infile:
        # 読み込んだ行の項目を順にカンマ区切りで対応する変数へ文字列としてmapする。
        name, price, url = map(str, line.split(','))
        if count > 0:
            # MySQLDBへの格納出力(insert)。上記で読み込んで保持している変数の値をformatで突っ込むので、valuesの{}側をエスケープ\とシングルクオーテーション'で囲んでおく。
            cursor.execute('INSERT INTO item_price_list (name, price, url) values(\'{}\',\'{}\',\'{}\');'.format(name, price, url))

            # コンソール出力
            print(u"{}つ目の処理を行っています".format(count))
        count = count + 1
    # 項目名列は処理対象の行としてカウントしない
    count = count - 1
    print(u'{} 件を処理しました。'.format(count))

# DB操作の終了。
# insert処置後のcommitも。
cursor.close()
connect.commit()
connect.close()