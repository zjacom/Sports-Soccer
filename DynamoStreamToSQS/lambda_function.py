import boto3
import json

def lambda_handler(event, context):
    # SQS 대기열 URL을 지정
    sqs_queue_url = 'https://sqs.ap-northeast-2.amazonaws.com/487590574852/Soccer_Queue'
    stream_arn = 'arn:aws:dynamodb:ap-northeast-2:487590574852:table/Soccer_Odds_Observer/stream/2024-03-08T05:43:13.444'
    dynamodb_client = boto3.client('dynamodb')
    streams_client = boto3.client('dynamodbstreams')

    # AWS SDK를 사용하여 SQS 대기열로 메시지 보내기
    sqs_client = boto3.client('sqs', region_name='ap-northeast-2')

    for record in event['Records']:
        # DynamoDB Stream에서 데이터 추출
        if record['eventName'] == 'INSERT':
            # INSERT 이벤트가 발생한 경우에만 처리
            new_image = record['dynamodb']['NewImage']['Time']['S']
            
            # 메시지 내용 생성 (JSON 형식)
            message_body = json.dumps(new_image)
            
            # SQS에 메시지 전송
            response = sqs_client.send_message(
                QueueUrl = sqs_queue_url,
                MessageBody = message_body
            )
    
    return {
    'statusCode': 200,
    'body': 'Data sent to SQS successfully.'
    }
