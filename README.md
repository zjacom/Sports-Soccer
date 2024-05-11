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
<img width="802" alt="스크린샷 2024-05-12 오전 2 40 15" src="https://github.com/zjacom/Sports-Soccer/assets/112957047/2f976ae2-0ad3-4134-9e92-c05de312e79b">

## How it works?
1. `EventBridge Scheduler`가 일정에 맞춰 `Init-Soccer-Games` 람다 함수를 실행한다.
2. `Init-Soccer-Games` 람다 함수는 새로운 축구 경기에 대한 정보를 `DynamoDB`에 업데이트한다.
3. `DynamoDB`에 새로운 데이터가 삽입되면 `DynamoStreamToSQS` 람다 함수가 실행된다.
4. `DynamoStreamToSQS` 람다 함수는 `SQS`에 메시지(경기 정보)를 보낸다.
5. `CloudWatch`는 `SQS`에 새로운 메시지가 들어오면 `Run_Step_Functions` 람다 함수를 실행한다.
6. `Run_Step_Functions` 람다 함수는 `Step_Functions`를 실행한다.
7. `Step_Functions`는 `SQS`에 메시지가 있는지 확인하고 `Rule`을 생성한다.
7. 생성된 `Rule`이 트리거되면 `Send-Email` 람다 함수를 실행한다.
9. `Send-Eamil` 람다 함수는 `DynamoDB`에서 경기 정보를 삭제하고, 만약 조건에 부합하는 경기라면 `SES`를 통해 사용자에게 이메일을 발송한다.

## TODO
- 데이터를 수집하는 코드가 현재 삭제된 거 같다. -> 수집 코드를 다시 만들어 데이터 수집을 지속적으로 해볼 예정입니다.
- 이메일로 알람이 오면 실제 경기 결과와 비교하여 정확도를 측정하는 기능을 추가하여 대시보드를 만들 예정입니다.
- 쌓이는 데이터를 주기적으로 분석하여 threshold를 수정하여 정확도를 높일 예정입니다.
