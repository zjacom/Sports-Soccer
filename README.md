# 🍚 축구 경기 결과 예측 서비스
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
<img width="897" alt="스크린샷 2024-03-14 오후 10 54 51" src="https://github.com/zjacom/Sports-Soccer/assets/112957047/d1ae08b5-28c0-4c35-aef0-cc91c3f5132c">

## How it works?
- EventBridge Scheduler의 일정에 맞게 Init-Soccer-Games가 실행되며 새로운 경기 정보를 DynamoDB에 추가한다.
    - EventBridge Scheduler의 일정은 매일 오전 6시와 오후 6시로 설정하면 적당하다.
- DynamoDB에 새로운 데이터가 들어오면 DynamoStreamToSQS가 실행되며 SQS에 메시지를 보낸다.
- EventBridge Rule에 있는 Run_Step_Functions_When_Message_In_SQS가 실행되고 Step_Functions가 실행된다.
    - Run_Step_Functions_When_Message_In_SQS은 아래와 같다.
<img width="395" alt="스크린샷 2024-03-14 오후 5 43 19" src="https://github.com/zjacom/Sports-Soccer/assets/112957047/67f0cdf3-31f7-406f-9ac7-b642f29f21f8">
- Step_Functions는 아래와 같은 구조로 만들어졌으며, SQS에 메시지가 없을 때까지 반복된다.
    - 아래 그림을 참고해 Check_Queue_Has_Message에는 Checking_Queue_Message 함수를 연결하고, 다른 하나는 Create-Rules 함수를 연결한다.
<img width="583" alt="스크린샷 2024-03-14 오후 10 57 15" src="https://github.com/zjacom/Sports-Soccer/assets/112957047/11bf48cc-97ae-441e-a22f-7bb7ef443abb">
- EventBridge Rule에 새로 생성된 규칙이 경기 시작 5분 전에 Send-Email을 실행한다.
- Send-Email은 배당의 차이가 조건에 부합하는 경기 정보를 이메일로 보내주고, 조회한 데이터를 DynamoDB에서 삭제한다.

# TODO
- 데이터를 수집하는 코드가 현재 삭제된 거 같다. -> 수집 코드를 다시 만들어 데이터 수집을 지속적으로 해볼 예정입니다.
- 이메일로 알람이 오면 실제 경기 결과와 비교하여 정확도를 측정하는 기능을 추가하여 대시보드를 만들 예정입니다.
- 쌓이는 데이터를 주기적으로 분석하여 threshold를 수정하여 정확도를 높일 예정입니다.