from utils import update_lambda_trigger, clean_cron_expression, create_cloudwatch_event, str_to_cron
import json
import boto3
import datetime
import time

def handler(event=None, context=None):
    # SQS 대기열 URL 설정
    sqs_queue_url = 'https://sqs.ap-northeast-2.amazonaws.com/487590574852/Soccer_Queue'
    target_arn = 'arn:aws:lambda:ap-northeast-2:487590574852:function:Send-Email-prod-demo'
    
    # SQS 클라이언트 생성
    sqs_client = boto3.client('sqs', region_name='ap-northeast-2')
    
    events_client = boto3.client('events', region_name='ap-northeast-2')

    # 여기서는 모든 규칙을 가져옵니다.
    response = events_client.list_rules()
    
    # 규칙 목록을 저장할 리스트를 생성합니다.
    cron_expressions = []
    
    # 규칙 목록을 반복하면서 Cron 표현식을 추출합니다.
    for rule in response['Rules']:
        if 'ScheduleExpression' in rule:
            cron_expression = rule['ScheduleExpression']
            cron_expressions.append(cron_expression)

    # 모든 원소에 함수를 적용하여 새로운 배열 생성
    cleaned_expressions = [clean_cron_expression(expression) for expression in cron_expressions]
    
    # SQS 대기열로부터 메시지 가져오기
    response = sqs_client.receive_message(
        QueueUrl = sqs_queue_url,
        MaxNumberOfMessages = 1,
        VisibilityTimeout = 30,
        WaitTimeSeconds = 20
    )
    
    if 'Messages' in response:
        for message in response['Messages']:
            time = json.loads(message['Body'])
            
            if str_to_cron(time) not in cleaned_expressions:
                current_time = datetime.datetime.now()
                rule_name = f"my_rule_{current_time.strftime('%Y%m%d%H%M%S')}"
                create_cloudwatch_event(time, rule_name, target_arn)
                update_lambda_trigger(rule_name, target_arn, events_client)
        
            # SQS 대기열에서 메시지 삭제
            receipt_handle = message['ReceiptHandle']
            
            sqs_client.delete_message(
                QueueUrl = sqs_queue_url,
                ReceiptHandle = receipt_handle
            )
    else:
        print("No messages in the queue.")

    return {
        'statusCode': 200,
        'body': 'Message handling completed.'
    }

