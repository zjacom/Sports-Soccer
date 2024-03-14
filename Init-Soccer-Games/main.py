import json
from decimal import Decimal
from database_access import Database_Access
from chrome_driver import Chrome_Driver

# 크롤링 후 문자열로 되어있는 배당을 float으로 변경하는 함수
def odds_change_to_float(s):
        return float(s.replace("[", "").replace("]", "").replace(" ", ""))

def handler(event=None, context=None):
    url = 'https://www.livescore.co.kr/#/sports/score_board/soccer_score.php'
    db_access = Database_Access('Soccer_Odds_Observer', region_name='ap-northeast-2')
    soup = Chrome_Driver.create_soup(url)

    # 크롤링할 축구 리그
    leagues = ["UEFA EL", "UEFA ECL", "ENG PR", "GER D1", "ITA D1", "SPA D1", "UEFA CL", "UEFA YL", "FRA D1", "ENG LCH", "AUS D1", "UEFA EURO", "TUR D1", "HOL D1"]

    # 축구 경기 요소만 필터링
    soccer_games = soup.find("table", {"border" : "1"}).find("tbody").find_all("tr")

    for ele in soccer_games:
        # 경기 날짜를 date에 저장
        if ele.find("strong", {"class" : "th_cal"}) != None:
            date = ele.find("strong", {"class" : "th_cal"}).get_text()
        # 배당이 없는 경기나 leagues에 포함되지 않은 리그는 패스
        elif ele.find("span", {"id" : "odds"}) == None or ele.find("td", {"class" : 'game'}).get_text() not in leagues:
            ele.next_sibling
        # DB에 필요한 데이터 저장
        else:
            start_time = ele.find("td", {"class" : "stime"}).get_text()
            hometeam_info = ele.find("td", {"class" : "hometeam"}).find_all("span")
            awayteam_info = ele.find("td", {"class" : "visitor"}).find_all("span")

            hometeam_name = hometeam_info[0].get_text()
            hometeam_odds, awayteam_odds = odds_change_to_float(hometeam_info[1].get_text()), odds_change_to_float(awayteam_info[0].get_text())
            # 이미 있는 DB에 저장된 경기라면 패스
            if hometeam_name in db_access.get_home_data():
                ele.next_sibling
            else:
                new_data = {'Time' : (date + start_time).rstrip(), 'Home': hometeam_name, 'HomeOdds' : hometeam_odds, 'AwayOdds' : awayteam_odds}
                ddb_data = json.loads(json.dumps(new_data), parse_float=Decimal)
                db_access.put_data(ddb_data)
                # # 배당이 1.99 이상 2.4 이하인 경기만 DB에 저장
                # if (1.99 <= hometeam_odds <= 2.4) or (1.99 <= awayteam_odds <= 2.4):
                #     new_data = {'Time' : (date + start_time).rstrip(), 'Home': hometeam_name, 'HomeOdds' : hometeam_odds, 'AwayOdds' : awayteam_odds}
                #     ddb_data = json.loads(json.dumps(new_data), parse_float=Decimal)
                #     db_access.put_data(ddb_data)
                #     print(ddb_data)
                # else:
                #     ele.next_sibling
    
    return {
        'statusCode': 200,
        'body': json.dumps('Soccer Data update has been completed')
    }