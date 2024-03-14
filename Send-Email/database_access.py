import boto3

class Database_Access():
    # DynamoDB 세팅
    def __init__(self, TABLE_NAME):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(TABLE_NAME)
    
    # 홈팀 데이터 가져오는 함수
    def get_home_data(self):
        data = self.table.scan()
        return [item['Home'] for item in data['Items']]
    
    # 경기 시간 데이터
    def get_time_data(self):
        data = self.table.scan()
        return set([item['Time'] for item in data['Items']])
    
    # 팀 이름으로 홈 배당
    def get_home_odds(self, team):
        data = self.table.scan()
        games = data['Items']
        for game in games:
            if game['Home'] == team:
                return float(game['HomeOdds'])
    
    # 팀 이름으로 원정 배당
    def get_away_odds(self, team):
        data = self.table.scan()
        games = data['Items']
        for game in games:
            if game['Home'] == team:
                return float(game['AwayOdds'])
                
    def delete_game(self, time, home):
        try:
            self.table.delete_item(Key={"Time" : time, "Home" : home})
        except:
            print("fail")
            raise