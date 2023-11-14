![logo](https://github.com/allen9535/budget-management-project/assets/69235039/121dcbf5-9079-4316-9e4c-9557aee9f1c7)

# 📈 예산 관리 어플리케이션

**사용자의 예산 관리**를 도와줍니다. 사용자로부터 한 달간 사용할 카테고리별 예산과 매일의 소비 내역을 입력받아 작동합니다. 예산을 어떻게 짜야 할 지 막막하다면, 당 서비스에서는 타 사용자들의 데이터를 통해 적절한 카테고리별 예산을 추천해드립니다. 오늘 얼마를 사용하는 게 적절한지 알고싶다면, 당 서비스는 매일 오전 8시마다 카테고리별 적절한 소비 금액 추천을 이메일로 보내드립니다. 오늘 얼마나 사용했는지를 예산과 비교해 확인하고싶다면, 당 서비스는 매일 오후 8시마다 예산 대비 얼마나 소비했는지에 대한 데이터를 이메일로 보내드립니다.
데이터를 통해 통계를 만들고 사용자의 건전한 소비 습관 형성을 돕습니다.

## 목차

-   [개요](#개요)
-   [사용기술](#사용기술)
-   [디렉터리 구조](#디렉터리-구조)
-   [API 문서](#API-문서)
-   [ERD](#ERD)
-   [프로젝트 진행 및 이슈 관리](#프로젝트-진행-및-이슈-관리)
-   [구현 과정](#구현-과정)
-   [회고](#회고)

<br/>

## 개요

단순히 예산과 소비 내역을 입력받아 계산하는 서비스는 이미 많이 있습니다. 당 서비스는 여기서 그치는 것이 아니라, 데이터를 통해 사용자의 예산 관리를 돕고, 최종적으로는 건전한 소비 습관 형성에 기여할 수 있는 서비스입니다.

우선 예산 작성 시 카테고리별 금액 추천 시스템입니다. 혹시 당 서비스를 처음 이용하는 분이거나 절약을 계획하는 분이라면 해당 시스템을 이용해보세요. 전체 예산액만 입력해주시면, 다른 이용자들의 데이터를 분석하여 카테고리별 적절한 예산액을 제시해 드립니다.

지출에 대한 컨설팅도 제공합니다. 설정한 예산에 맞춰 매일 아침 8시 당일 지출 가능 금액을 이메일로 보내드립니다. 혹시 과소비가 있으셨나요? 예산과 지출 기록을 확인했을 때 남은 기간동안 사용할 수 있는 금액이 없어지셨나요? 당 서비스는 엄격한 교관이 아닙니다. 지속적인 소비 습관 생성을 위해 매일 사용해야 할 최소한의 금액을 제시해 드릴겁니다. 매일 소비는 하는데 얼마나 사용했는지 일일이 확인하는 게 귀찮으신가요? 매일 저녁 8시 당일 기 지출 금액을 이메일로 보내드립니다. 오늘 사용할 수 있었을 금액 대비 몇 퍼센트를 사용하셨는지를 통해 위험도를 체크해보세요.

통계 기능도 제공합니다. 오늘 날짜가 몇 일 인가요? 10일? 지난 달 10일까지의 소비 데이터를 비교해 총액과 카테고리별 소비율이 얼마나 변화했는지 알려드립니다. 요일은요? 지난 지출 데이터 속 해당 요일에 소비한 기록을 통해 소비율의 변화를 알려드립니다. 당연하게도 다른 사용자 대비 소비율도 알려드릴 겁니다.

앞서 말씀드렸듯 단순한 가계부 서비스에 그치고 싶지 않습니다. 여러분의 건전한 소비 습관이 정착될 때까지 충분한 도움을 제공할 수 있는 서비스가 되겠습니다.

<br/>

## 사용기술

![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white) &nbsp;
![Django](https://img.shields.io/badge/Django-092E20.svg?style=for-the-badge&logo=Django&logoColor=white) &nbsp;
![JWT](https://img.shields.io/badge/JWT-000000.svg?style=for-the-badge&logo=JSON-Web-Tokens&logoColor=white) &nbsp;
![Swagger](https://img.shields.io/badge/Swagger-85EA2D.svg?style=for-the-badge&logo=Swagger&logoColor=white) &nbsp;
![Celery](https://img.shields.io/badge/Celery-37814A.svg?style=for-the-badge&logo=Celery&logoColor=white) <br/>

![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=for-the-badge&logo=Docker&logoColor=white) <br/>

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1.svg?style=for-the-badge&logo=PostgreSQL&logoColor=white)

<br/>

## 디렉터리 구조

<details>
    <summary>디렉터리 구조</summary>

    📦Budget-Management-Project
    ┣ 📂.github
    ┃ ┗ 📂workflows
    ┃ ┃ ┗ 📜django_ci.yml
    ┣ 📂accounts
    ┃ ┣ 📜admin.py
    ┃ ┣ 📜apps.py
    ┃ ┣ 📜models.py
    ┃ ┣ 📜serializers.py
    ┃ ┣ 📜tests.py
    ┃ ┣ 📜urls.py
    ┃ ┣ 📜views.py
    ┃ ┗ 📜__init__.py
    ┣ 📂budgets
    ┃ ┣ 📜admin.py
    ┃ ┣ 📜apps.py
    ┃ ┣ 📜models.py
    ┃ ┣ 📜serializers.py
    ┃ ┣ 📜tests.py
    ┃ ┣ 📜urls.py
    ┃ ┣ 📜views.py
    ┃ ┗ 📜__init__.py
    ┣ 📂categories
    ┃ ┣ 📜admin.py
    ┃ ┣ 📜apps.py
    ┃ ┣ 📜models.py
    ┃ ┣ 📜serializers.py
    ┃ ┣ 📜tests.py
    ┃ ┣ 📜urls.py
    ┃ ┣ 📜views.py
    ┃ ┗ 📜__init__.py
    ┣ 📂config
    ┃ ┣ 📜asgi.py
    ┃ ┣ 📜celery.py
    ┃ ┣ 📜settings.py
    ┃ ┣ 📜urls.py
    ┃ ┣ 📜wsgi.py
    ┃ ┗ 📜__init__.py
    ┣ 📂spends
    ┃ ┣ 📜admin.py
    ┃ ┣ 📜apps.py
    ┃ ┣ 📜models.py
    ┃ ┣ 📜serializers.py
    ┃ ┣ 📜tasks.py
    ┃ ┣ 📜tests.py
    ┃ ┣ 📜urls.py
    ┃ ┣ 📜views.py
    ┃ ┗ 📜__init__.py
    ┣ 📜.env
    ┣ 📜.gitignore
    ┣ 📜category_list.csv
    ┣ 📜db_dump_data.json
    ┣ 📜dummy_budgets.py
    ┣ 📜dummy_categories.py
    ┣ 📜dummy_spends.py
    ┣ 📜dummy_users.py
    ┣ 📜manage.py
    ┣ 📜README.md
    ┗ 📜requirements.txt

기본 Django 프로젝트의 디렉터리 구조를 거의 그대로 사용하였습니다. Celery 설정 파일은 설정과 관련 있는 파일이라 함께 관리하기 위해 config 폴더에, Celery 작업과 관련된 기능들은 tasks.py 파일에 만든 다음 해당 기능과 관련있는 폴더에 위치시켰습니다. 더미 데이터를 만들기 위한 파일들과 DB 덤프 파일은 개발 작업 시 편리하게 사용하기 위해 루트 프로젝트 폴더에 위치시켰습니다.

</details>

<br/>

## API 문서

Swagger: `http://127.0.0.1:{port}`

<br/>

## ERD

![ERD](https://github.com/wanted-A/GIS-Restaurant/assets/69235039/39055c39-4d9d-471e-82e3-8101f755156c)

<br/>

## 프로젝트 진행 및 이슈 관리

GitHub 이슈 / GitHub 일정 관리

![GitHub이슈](https://github.com/wanted-A/GIS-Restaurant/assets/69235039/2ca80ca4-e11a-4dd8-aba7-941461b8159e)

![GitHub이슈상세](https://github.com/wanted-A/GIS-Restaurant/assets/69235039/ffff7d54-c1e0-4e8a-8c82-eb0c04e5f5f9)

![GitHub일정관리](https://github.com/wanted-A/GIS-Restaurant/assets/69235039/7d3c9e55-3365-4cdf-8e32-00cf6d6f1a72)

<br/>

## 구현 과정

<details>
<summary>사용자 기능</summary>

-   [관련 이슈 #3](https://github.com/allen9535/budget-management-project/issues/3)

1.  회원가입

    -   계정명, 이메일, 휴대전화 번호, 비밀번호, 비밀번호 체크의 다섯 항목을 입력해야 합니다.
    -   계정명과 비밀번호는 사용자 인증에 사용됩니다.
    -   이메일은 이메일 인증과 향후 서비스 제공 시 사용됩니다.
    -   비밀번호와 비밀번호 체크 항목의 경우 사용자가 정확한 값을 입력했는지 확인하기 위해 설정했습니다.
    -   휴대전화 번호는 정규표현식을 사용해 한국의 휴대전화 번호 형식만을 저장합니다.

2.  로그인

    -   계정명과 비밀번호를 입력하면 **JSON Web Token**을 발급합니다.
    -   Access Token은 보안을 위해 유효 기간을 30분으로 짧게 설정했습니다.
    -   Refresh Token 또한 보안을 위해 요청한 측에 반환하지 않고 사용자 명의로 서버의 Redis에 저장합니다.

3.  로그아웃

    -   Access Token을 받아 블랙리스트에 등록합니다.
    -   블랙리스트에 등록된 토큰은 다시 사용할 수 없습니다.

    </details>

<details>
<summary>카테고리 기능</summary>

-   [관련 이슈 #4](https://github.com/allen9535/budget-management-project/issues/4)

1. 카테고리 생성

    - 프로젝트 루트 폴더에 위치한 dummy_categories.py 파일을 실행시켜 카테고리를 등록합니다.
    - 이 때 마찬가지로 프로젝트 루트 폴더에 위치한 category_list.csv 파일을 읽어서 카테고리를 등록합니다.
    - 이와 같은 구조를 갖춘 것은 향후 카테고리 관련 수정이나 확장이 필요한 경우 csv 파일만 수정하면 되는 것이 편리할 것이라 판단했기 때문입니다.

2. 카테고리 목록

    - GET 요청을 받으면 현재 DB에 저장되어 있는 카테고리 목록을 제공합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

</details>

<details>
<summary>예산 기능</summary>

-   [관련 이슈 #4](https://github.com/allen9535/budget-management-project/issues/4)
-   [관련 이슈 #16](https://github.com/allen9535/budget-management-project/issues/16)

1. 예산 생성

    - POST 요청과 함께 데이터를 받으면 해당하는 예산 데이터를 생성합니다.
    - 카테고리, 금액, 시작일, 종료일은 필수값입니다.
    - 필수값이 없거나 잘못된 데이터가 들어오면 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

2. 예산 목록

    - GET 요청을 받으면 현재 로그인한 사용자의 예산 데이터 목록을 제공합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

3. 예산 상세보기

    - GET 요청과 함께 예산 데이터의 ID를 받으면 해당하는 상세한 데이터를 제공합니다.
    - 잘못된 값이나 타인의 예산 데이터 ID를 입력할 경우 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

4. 예산 수정

    - PUT 요청과 함께 예산 데이터 ID, 수정할 데이터를 받으면 해당하는 예산 데이터를 수정합니다.
    - 잘못된 값이나 타인의 예산 데이터 ID를 입력할 경우 상태 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

5. 예산 삭제
    - DELETE 요청과 함께 예산 데이터 ID를 받으면 해당하는 예산 데이터를 삭제합니다.
    - 잘못된 값이나 타인의 예산 데이터 ID를 입력할 경우 상태 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

</details>

<details>
<summary>지출 기능</summary>

-   [관련 이슈 #5](https://github.com/allen9535/budget-management-project/issues/5)
-   [관련 이슈 #12](https://github.com/allen9535/budget-management-project/issues/12)
-   [관련 이슈 #13](https://github.com/allen9535/budget-management-project/issues/13)
-   [관련 이슈 #22](https://github.com/allen9535/budget-management-project/issues/22)

1. 지출 생성

    - POST 요청과 함께 데이터를 받으면 해당하는 지출 데이터를 생성합니다.
    - 카테고리, 금액, 지출일은 필수값입니다.
    - 필수값이 없거나 잘못된 데이터가 들어오면 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

2. 지출 목록

    - GET 요청과 함께 쿼리 파라미터를 받으면 해당하는 지출 목록을 제공합니다.
    - 검색 시작일, 종료일은 필수입니다.
    - 필수값이 없거나 잘못된 데이터가 들어오면 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

3. 지출 상세보기

    - GET 요청과 함께 지출 데이터 ID를 받으면 해당하는 상세한 데이터를 제공합니다.
    - 잘못된 값이나 타인의 지출 데이터 ID를 입력할 경우 상태 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

4. 지출 수정

    - PUT 요청과 함께 지출 데이터 ID, 수정할 데이터를 받으면 해당하는 지출 데이터를 수정합니다.
    - 잘못된 값이나 타인의 예산 데이터 ID를 입력할 경우 상태 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

5. 지출 삭제

    - DELETE 요청과 함께 지출 데이터 ID를 받으면 해당하는 지출 데이터를 삭제합니다.
    - 잘못된 값이나 타인의 지출 데이터 ID를 입력할 경우 상태 상태코드와 함께 에러 메시지를 출력합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

6. 지출 내역에서 합계 제외 기능

    - 지출 목록 API를 호출할 때 제외할 지출 데이터 ID를 제공하면, 지출 목록에는 그대로 표시되지만 총 지출액 항목과 카테고리별 지출액 항목에서는 제외됩니다.
    - 제외할 지출 데이터는 여러 값을 줄 수 있습니다.

7. 오늘 지출 추천

    - 사용자의 가장 최신 예산안의 기간 범위를 산출하고, 해당 범위 내의 지출 금액을 뺀 다음, 예산안 기간 범위의 남은 기간(당일 포함)으로 나누어 **일별 지출 가능 금액**을 제공합니다.
    - 총액에 대한 지출 추천과 카테고리별 **지출 추천**을 제공합니다.
    - 총액과 카테고리별 지출 가능 금액이 일정 금액 이하여도 최소한의 금액을 제시합니다. 이는 서비스의 목적이 금액 계산이 아니라 건전한 소비 습관 정착이기 때문입니다.
    - Celery를 통해 **매일 오전 8시에 자동으로 사용자의 이메일로 전송**될 수 있도록 설정했습니다.
    - 현재 코드에는 테스트용으로 개발자 이메일에 한 개의 이메일만 전송되도록 설정했습니다.

8. 오늘 지출 안내

    - 사용자가 오늘 지출한 총액을 제공합니다.
    - 사용자의 가장 최신 예산안의 기간 범위를 산출하여 카테고리별 해당 기간의 예산 총액을 제공합니다.
    - 또 이를 날짜별로 나누어 오늘의 **적정 지출 금액**과 실제 지출한 금액을 제공합니다.
    - 적정 금액에 대한 실지출 금액의 비를 퍼센테이지로 만들어 **위험도**를 제공합니다.
    - Celery를 통해 **매일 오후 8시에 자동으로 사용자의 이메일로 전송**될 수 있도록 설정했습니다.
    - 현재 코드에서는 테스트용으로 개발자 이메일에 한 개의 이메일만 전송되도록 설정했습니다.

9. 지출 통계
    - 오늘을 기준으로 이번달의 1일부터 말일까지의 데이터를 기반으로 합니다.
    - 현재 로그인한 사용자의 당월과 전월의 지출 총계를 각각 구하고, 당월 지출 총계에서 전월 지출 총계를 나눈 다음 퍼센테이지를 만들어 **전월 대비 전체 소비율의 변화**를 제공합니다.
    - 오늘의 요일과 지출액을 구하고 지난 모든 같은 요일의 지출액과의 대비를 통해 **지난 요일 지출 금액 대비 소비율**을 제공합니다.
    - 현재 로그인한 사용자를 제외한 나머지 모든 사용자 데이터에서, 평균 예산액을 일별로 나누어 일일 평균 예산액을 구하고, 이를 오늘 지출한 금액의 평균값과 대비를 통해 전체 사용자의 일일 평균 소비율을 구합니다. 또 현재 로그인한 사용자의 일일 평균 예산액과 오늘 지출한 금액의 평균값의 대비를 통해 로그인 사용자의 일일 평균 소비율을 구합니다. 이 둘의 대비를 통해 **타 사용자 대비 소비율**을 제공합니다.

</details>

<details>
<summary>더미 데이터 생성</summary>

-   [관련 이슈 #10](https://github.com/allen9535/budget-management-project/issues/10)

1. 더미 데이터 생성을 위한 파일 생성

    - 프로젝트 루트 폴더에 파일을 생성하고 해당 파일을 실행하여 더미 데이터를 생성했습니다.
    - Faker 라이브러리를 활용하여 무작위 계정명, 이메일, 날짜를 생성하여 더미 데이터를 만들었습니다.

2. 더미 데이터의 유용성에 대한 고민
    - 간단한 CRUD에 대한 개발이 끝나고 통계 부분으로 넘어가자, 제가 생성한 더미 데이터에 대한 문제점이 발견되었습니다.
    - 예산과 지출 데이터가 지나치게 무작위였습니다. 이 서비스는 연속성을 전제로 두고 있는데, 제가 생성한 더미 데이터는 너무 데이터가 산발적이었습니다.
    - 이후 통계 관련 기능을 추가하면서 더미 데이터를 수정하여 테스트 했습니다.

</details>

<details>
<summary>예산 추천</summary>

-   [관련이슈 #11](https://github.com/allen9535/budget-management-project/issues/11)

1. 의도

    - 카테고리별 예산 설정에 어려움을 겪는 사용자를 위해 총 예산액을 입력하면 카테고리별 예산 금액을 제공하는 기능을 만들고자 했습니다.
    - 이 때 생성되는 예산 금액은 기존 사용자들의 데이터의 평균 값의 퍼센테이지로 설정하고자 했습니다.

2. 구현

    - 카테고리별 예산의 평균을 만들고, 이것이 전체 예산 평균에서 차지하는 비율을 계산합니다. 여기에 현재 로그인한 사용자가 입력한 예산 총액을 곱해 카테고리별 추천 예산액을 제공합니다.
    - 사용자 편의성을 위해 예산 총액을 곱하기 직전 소숫점 둘째 자리까지 반올림하고, 곱한 다음에는 정수로 형변환 한 값을 제공합니다.
    - 인증된 사용자에게만 권한을 부여합니다.

</details>

<br/>

## 회고

[관련 이슈](https://github.com/allen9535/budget-management-project/issues/18)

<details>
<summary>TDD에 대한 고민</summary>

-   매번 Postman을 통해 일일이 조건을 다르게 부여하고 검증하는 일련의 과정들이 번거롭다고 생각하게 되었습니다.
-   Django와 Django REST Framework에는 TDD를 위한 기능들이 갖추어져 있었기에 이를 활용하여 효율적인 테스트를 시도해보고자 TDD를 도입하게 되었습니다.
-   처음에는 사용할 데이터를 매 코드마다 일일이 새로 만드는 것이 몹시 번거로웠습니다. 하지만 Django의 TDD에 대해 공부하면서 코드를 조금씩 고쳐보았더니 작성하는 코드 수도 줄고, 테스트 실행 시간도 많이 단축되었습니다.(라인수: 561라인 -> 442라인 / 실행 시간: 33.461초 -> 16.622초)
-   또 제가 생각한 오류가 발생할 수 있는 케이스들을 다양하게 테스트 할 수 있어 관련 부분들을 빠르게 수정할 수 있었습니다.

</details>

<details>
<summary>CI에 대한 고민</summary>

-   TDD를 도입하면서 GitHub Actions를 활용해 테스트 자동화를 시도할 수 있다는 것을 알게 되었습니다.
-   이에 yml 파일을 생성해 Push나 PR이 발생할 때 GitHub Actions에서 제가 작성한 테스트 코드를 활용한 테스트를 진행할 수 있도록 만들었습니다.
-   CI 적용 초기에는 많은 문제가 발생했습니다. Redis를 활용하는 코드가 있는데 Workflow에는 관련 내용이 없다거나, 데이터 없이 테스트를 진행하게 만드는 등의 문제였습니다. 하지만 자동적으로 테스트가 진행되고 에러 메시지를 쉽게 확인할 수 있어 빠르게 관련 문제들을 해결할 수 있었습니다.

</details>

<details>
<summary>DB 데이터 인코딩</summary>

-   로컬에서 SQLite3를 사용해 개발하고 테스트 할 때의 문제입니다.
-   DB에서 데이터를 덤프한 다음, 이 데이터를 다시 DB에 적용하기 위해 `python manage.py loaddata` 명령어를 실행시켰습니다. 그랬더니 이런 에러가 발생했습니다. `“UnicodeDecodeError: 'utf8' codec can't decode byte 0xff in position 0: invalid start byte”`
-   원인은 DB데이터를 JSON 형식의 파일로 덤프하면서 인코딩 형식을 지정하지 않았던 것으로 보입니다.
-   덤프한 DB 데이터의 인코딩 형식을 변경하는 것으로 해결했습니다. 제가 검색한 것을 바탕으로 실험해 본 바로는, 애초에 DB 데이터를 덤프할 때 명령어에 인코딩 형식을 UTF-8로 지정해주는 것이 편할 것 같습니다. 명령어는 다음과 같습니다. `python -Xutf8 manage.py dumpdata > db.json`

</details>

<details>
<summary>테스트 코드 개선</summary>

-   테스트 코드를 작성하고 실행시키는데 다음과 같은 에러가 발생했습니다. `AttributeError: 'list' object has no attribute 'items'`
-   원인은 테스트 코드에서 사용하려던 데이터 형식이었습니다. client 객체의 메서드를 사용할 때에는 딕셔너리 형태의 데이터를 아규먼트로 제공해야 하는데, 리스트 형태의 데이터를 제공했기 때문인 것으로 보입니다.
-   데이터 형식을 JSON이라고 명시하는 것으로 해결했습니다. client 객체를 사용할 때 옵션으로 `content_type='json'` 옵션을 제공해도 되고, settings.py의 REST_FRAMEWORK 옵션에 `'TEST_REQUEST_DEFAULT_FORMAT': 'json'` 값을 입력해도 됩니다.

</details>

<br/>

## 작성자

-   [전정헌](https://github.com/allen9535)
