import datetime
import json
import pymysql
import re
import requests
from lxml import html

DOMAIN = "https://www.transfermarkt.co.uk/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
LASTYEAR = int(datetime.datetime.today().strftime('%Y')) - 1
LEAGUE = {}
LEAGUE["England"] = {"id":"ENG", "league":"premier-league", "level":"GB1", "startYear":"1992"}
LEAGUE["Spain"]   = {"id":"SPA", "league":"laliga", "level":"ES1", "startYear":"1928"}
LEAGUE["Germany"]   = {"id":"GER", "league":"1-bundesliga", "level":"L1", "startYear":"1963"}

def getEternalTable(cursor, data):
    url  = DOMAIN + data["league"] + "/ewigeTabelle/wettbewerb/"
    url += data["level"] + "/saison_id_von/"
    url += data["startYear"] + "/saison_id_bis/" + str(LASTYEAR) + "/tabllenart/alle/plus/1"
    print(url)

    response = requests.get(url, headers = HEADERS)
    content = html.fromstring(response.text)
    table = content.xpath('//table[@class="items"]/tbody/tr')
    for row in table:
        td = row.xpath('td')
        id = str(row.xpath('td/a/@id')[0])
        name = td[2].text_content()
        level = data["level"]
        tempLeague = td[3].text_content().replace(".Liga", "")
        league = tempLeague if re.match(r"(\d+)", tempLeague) else "99"
        years = td[4].text_content().replace(".", "")
        first = td[5].text_content().replace(".", "")
        match = td[6].text_content().replace(".", "")
        win = td[7].text_content().replace(".", "")
        draw = td[8].text_content().replace(".", "")
        loss = td[9].text_content().replace(".", "")
        point = td[13].text_content().replace(".", "")

        # 先檢查球會資料
        cursor.execute('select id from club where id = %s', id)
        if(cursor.rowcount == 0):
            # 查無資料則新增一筆
            sql = 'insert into club (id, name, nation) values(%s, %s, %s)'
            param = (id, name, data["id"])
            cursor.execute(sql, param)
            print(id + " : " + name + " : " + data["id"])

        # 再更新歷史記錄
        cursor.execute('select id from eternal_table where id = %s', id)
        if(cursor.rowcount == 0):
            # 查無資料則新增一筆
            sql = 'insert into eternal_table values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            param = (id, level, league, years, first, match, win, draw, loss, point)
        else:
            # 更新履歷資料
            sql = 'update eternal_table set level = %s, league = %s, years = %s, first = %s, `match` = %s, win = %s, draw = %s, loss = %s, point = %s where id = %s'
            param = (level, league, years, first, match, win, draw, loss, point, id)
        cursor.execute(sql, param)
        print(id + " : " + name + " : " + level + " : " + league + " : " + years + " : " + first + " : " + match + " : " + win + " : " + draw + " : " + loss + " : " + point)

"""
Main
"""
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': '',
    'charset':'utf8mb4',
    'db':'transfermarkt',
    'autocommit': True,
    'cursorclass':pymysql.cursors.DictCursor
}
conn = pymysql.connect(**config)
cursor = conn.cursor()

for country in LEAGUE:
    getEternalTable(cursor, LEAGUE[country])