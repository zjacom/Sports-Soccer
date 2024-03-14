import pytz
import boto3
import json
import datetime
from dateutil import parser
from decimal import Decimal
from database_access import Database_Access
from chrome_driver import Chrome_Driver

kst = pytz.timezone('Asia/Seoul')

# 크롤링 후 문자열로 되어있는 배당을 float으로 변경하는 함수
def odds_change_to_float(s):
    return float(s.replace("[", "").replace("]", "").replace(" ", ""))

def check_odd_difference(before_odd, current_odd, threshold):
    return before_odd - current_odd >= threshold

def handler(event=None, context=None):
    db_access = Database_Access('Soccer_Odds_Observer')
    url = 'https://www.livescore.co.kr/#/sports/score_board/soccer_score.php'
    soup = Chrome_Driver.create_soup(url)

    # 크롤링할 축구 리그
    leagues = ["UEFA EL", "UEFA ECL", "ENG PR", "GER D1", "ITA D1", "SPA D1", "UEFA CL", "UEFA YL", "FRA D1", "ENG LCH", "AUS D1", "UEFA EURO", "TUR D1", "HOL D1"]

    # 축구 경기 요소만 필터링
    soccer_games = soup.find("table", {"border" : "1"}).find("tbody").find_all("tr")

    for ele in soccer_games:
        # 경기 날짜 변수 date에 저장
        if ele.find("strong", {"class" : "th_cal"}) != None:
            date = ele.find("strong", {"class" : "th_cal"}).get_text()
        # 배당이 없는 경기나 target_games에 포함되지 않은 리그는 패스
        elif ele.find("span",{"id" : "odds"}) == None or ele.find("td", {"class" : 'game'}).get_text() not in leagues:
            ele.next_sibling
        # 필요한 정보 추출 후 DB에 저장
        else:
            start_time = ele.find("td",{"class" : "stime"}).get_text()
            hometeam_info = ele.find("td",{"class" : "hometeam"}).find_all("span")
            awayteam_info = ele.find("td",{"class" : "visitor"}).find_all("span")

            current_time = (datetime.datetime.now(kst) + datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M')
            hometeam_name, awayteam_name = hometeam_info[0].get_text(), awayteam_info[1].get_text()
            hometeam_odds, awayteam_odds = odds_change_to_float(hometeam_info[1].get_text()), odds_change_to_float(awayteam_info[0].get_text())

            # 배당 차이 기준이 되는 변수!
            threshold = 0.24
            if (hometeam_name in db_access.get_home_data()) and (current_time in db_access.get_time_data()):
                before_home_odd, before_away_odd = db_access.get_home_odds(hometeam_name), db_access.get_away_odds(hometeam_name)
                game_time = (date + start_time).rstrip()
                
                if check_odd_difference(before_home_odd, hometeam_odds, threshold):
                    changed_team = hometeam_name
                    changed_odd = hometeam_odds
                    changed_before_odd = before_home_odd
                elif check_odd_difference(before_away_odd, awayteam_odds, threshold):
                    changed_team = awayteam_name
                    changed_odd = awayteam_odds
                    changed_before_odd = before_away_odd

                # 만약 기준에 적합하는 팀이 있다면 이메일 발송
                if 'changed_team' in locals():
                    subject = "배당 하락 감지 알림 서비스! " + (date + start_time).rstrip()
                    message_body = f"{hometeam_name} vs {awayteam_name}\n{changed_team} 배당 하락!\n{changed_before_odd} -> {changed_odd}"
                    client = boto3.client("ses")
                    message = {"Subject": {"Data": subject}, "Body": {"Html": {"Data": message_body}}}

                db_access.delete_game(game_time, hometeam_name)
                ele.next_sibling

            else:
                ele.next_sibling

    return {
        'statusCode': 200,
        'body': json.dumps('Send e-mail and delete data have been completed!')
    }
