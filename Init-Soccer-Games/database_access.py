import boto3

class Database_Access():
    # DynamoDB 세팅
    def __init__(self, TABLE_NAME, region_name='ap-northeast-2'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(TABLE_NAME)
    
    # 홈팀 데이터 가져오는 함수
    def get_home_data(self):
        data = self.table.scan()
        return [item['Home'] for item in data['Items']]
    
    # DynamoDB에 데이터 삽입하는 함수
    def put_data(self, input_data):
        self.table.put_item(
            Item =  input_data
        )