# ⚽ 축구 경기 결과 예측 서비스
<p>
  <img src="https://img.shields.io/badge/Amazon AWS-232F3E?style=flat&logo=Amazon AWS&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=Docker&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=Python&logoColor=white">
</p>

## Description
- 축구 경기 결과 예측에 사용할 지표를 알아보던 중 “해외 배당”을 알게 됐습니다.
- 이 프로젝트는 초기 배당과 경기 시작 5분 전 배당의 차이를 활용하여 경기의 승패를 예측합니다.
- 만약 배당의 차이가 조건에 부합하면 해당 경기의 정보를 이메일로 보내줍니다.

## Architecture
<img width="897" alt="스크린샷 2024-03-14 오후 10 54 51" src="https://github.com/zjacom/Sports-Soccer/assets/112957047/ca20283d-b836-4996-904d-07e77df6a56f">

## How it works?
- EventBridge Scheduler의 일정에 맞게 Init-Soccer-Games가 실행되며 새로운 경기 정보를 DynamoDB에 추가한다.
    - EventBridge Scheduler의 일정은 매일 오전 6시와 오후 6시로 설정하면 적당하다.
- DynamoDB에 새로운 데이터가 들어오면 DynamoStreamToSQS가 실행되며 SQS에 메시지를 보낸다.
- EventBridge Rule에 있는 Run_Step_Functions_When_Message_In_SQS가 실행되고 Step_Functions가 실행된다.
    - Run_Step_Functions_When_Message_In_SQS은 아래와 같다.
```
{
  "source": ["aws.sqs"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": ["sqs.amazonaws.com"],
    "eventName": ["SendMessage"]
  }
}
```
- Step_Functions는 아래와 같은 구조로 만들어졌으며, SQS에 메시지가 없을 때까지 반복된다.
```
{
  "Comment": "Invoke Lambda Function Until StatusCode is 200",
  "StartAt": "Check_Queue_Has_Message",
  "States": {
    "Check_Queue_Has_Message": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-2:487590574852:function:Check_Queue_Has_Message",
      "ResultPath": "$.lambdaResult",
      "Next": "CheckStatusCode"
    },
    "CheckStatusCode": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.lambdaResult.statusCode",
          "NumericEquals": 200,
          "Next": "Create_Rule_If_Queue_Has_Message"
        }
      ],
      "Default": "EndState"
    },
    "Create_Rule_If_Queue_Has_Message": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:ap-northeast-2:487590574852:function:Create-Rules-prod-demo:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ],
      "Next": "WaitBeforeNextInvocation"
    },
    "WaitBeforeNextInvocation": {
      "Type": "Wait",
      "Seconds": 30,
      "Next": "Check_Queue_Has_Message"
    },
    "EndState": {
      "Type": "Pass",
      "Result": "Lambda function returned a non-200 status code. Ending the state machine.",
      "End": true
    }
  }
}
```
- EventBridge Rule에 새로 생성된 규칙이 경기 시작 5분 전에 Send-Email을 실행한다.
- Send-Email은 배당의 차이가 조건에 부합하는 경기 정보를 이메일로 보내주고, 조회한 데이터를 DynamoDB에서 삭제한다.

## TODO
- 데이터를 수집하는 코드가 현재 삭제된 거 같다. -> 수집 코드를 다시 만들어 데이터 수집을 지속적으로 해볼 예정입니다.
- 이메일로 알람이 오면 실제 경기 결과와 비교하여 정확도를 측정하는 기능을 추가하여 대시보드를 만들 예정입니다.
- 쌓이는 데이터를 주기적으로 분석하여 threshold를 수정하여 정확도를 높일 예정입니다.
