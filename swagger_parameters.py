from drf_yasg import openapi


PATH_BUDGET_NO = openapi.Parameter(
    'budget_no',
    openapi.IN_PATH,
    type=openapi.TYPE_INTEGER,
    description='예산 데이터 ID',
    required=True
)

HEADER_TOKEN = openapi.Parameter(
    'access_token',
    openapi.IN_HEADER,
    type=openapi.TYPE_STRING,
    description='인증에 사용되는 액세스 토큰',
    required=True
)

QUERY_START_AT = openapi.Parameter(
    'start_at',
    openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='검색 시작일',
    required=True
)

QUERY_END_AT = openapi.Parameter(
    'end_at',
    openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='검색 종료일',
    required=True
)

QUERY_MIN_AMOUNT = openapi.Parameter(
    'min_amount',
    openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description='검색 최솟값',
)

QUERY_MAX_AMOUNT = openapi.Parameter(
    'max_amount',
    openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description='검색 최댓값',
)

QUERY_CATEGORY = openapi.Parameter(
    'category',
    openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='카테고리명',
)

QUERY_EXCLUDE = openapi.Parameter(
    'exclude',
    openapi.IN_QUERY,
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_INTEGER,
    ),
    description='제외할 지출 ID',
)

PATH_SPEND_NO = openapi.Parameter(
    'spend_no',
    openapi.IN_PATH,
    type=openapi.TYPE_INTEGER,
    description='지출 데이터 ID',
    required=True
)

BODY_CATEGORY = openapi.Parameter(
    'category',
    openapi.IN_BODY,
    type=openapi.TYPE_STRING,
    description='카테고리명',
    required=True
)
