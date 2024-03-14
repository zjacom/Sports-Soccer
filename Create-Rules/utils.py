import json
import boto3
import random
import datetime
import time


def create_cloudwatch_event(time_str, rule_name, target_arn):
    # CloudWatch Events 클라이언트 생성
    cloudwatch_events = boto3.client('events', region_name='ap-northeast-2')

    # 문자열을 날짜 및 시간 객체로 변환
    scheduled_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M') - datetime.timedelta(minutes=545)

    # CloudWatch Events 규칙 생성 (정확한 시간으로 설정)
    response = cloudwatch_events.put_rule(
        Name=rule_name,
        ScheduleExpression=f'cron({scheduled_time.minute} {scheduled_time.hour} {scheduled_time.day} {scheduled_time.month} ? {scheduled_time.year})',
        State='ENABLED'
    )
    
    # id_num 랜덤 배정
    id_num = str(random.randint(1, 1000))

    # CloudWatch Events 규칙과 대상 연결
    cloudwatch_events.put_targets(
        Rule=rule_name,
        Targets=[
            {
                'Id': id_num,
                'Arn': target_arn
            }
        ]
    )

def update_lambda_trigger(rule_name, target_arn, events_client):
    # Lambda 및 CloudWatch Events 클라이언트 생성
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
    
    # CloudWatch Events 규칙의 ARN 가져오기
    response = events_client.describe_rule(Name=rule_name)
    rule_arn = response['Arn']
    
    # 대상 람다 함수에 대한 권한 설정
    lambda_client.add_permission(
        FunctionName=target_arn,
        StatementId=f'{rule_name}-Permission',
        Action='lambda:InvokeFunction',
        Principal='events.amazonaws.com',
        SourceArn=rule_arn
    )
    
# cron 표현식으로 변환
def str_to_cron(input_datetime_str):
    input_datetime = datetime.datetime.strptime(input_datetime_str, '%Y-%m-%d %H:%M') - datetime.timedelta(minutes=545)
    
    cron_expression = f'{input_datetime.minute} {input_datetime.hour} {input_datetime.day} {input_datetime.month} ? {input_datetime.year}'
    
    return cron_expression

def clean_cron_expression(cron_expression):
    return cron_expression.replace('cron', '').replace('(', '').replace(')', '')