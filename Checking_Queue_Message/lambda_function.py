import boto3
import time

def lambda_handler(event, context):
    time.sleep(30)
    # SQS 큐 URL 설정
    sqs_queue_url = 'https://sqs.ap-northeast-2.amazonaws.com/487590574852/Soccer_Queue'

    # SQS 클라이언트 생성
    sqs_client = boto3.client('sqs', region_name='ap-northeast-2')

    # SQS 큐의 메시지 수 확인
    response = sqs_client.get_queue_attributes(
        QueueUrl=sqs_queue_url,
        AttributeNames=['ApproximateNumberOfMessages']
    )

    # 메시지 수 확인
    num_messages = int(response['Attributes']['ApproximateNumberOfMessages'])
    
    if num_messages > 0:
        return {
            'statusCode': 200,
            'body': 'There is Message.'
        }
    else:
        return {
            'statusCode': 404,
            'body': 'There is no Message.'
        }

