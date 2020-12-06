import re

_help_text={
    "main":
    """사용자의 역할에 따라 다른 메뉴가 보입니다.
    관리자: Task 전체 오버뷰 / Task 생성 / Task 관리 / 사용자 관리
    제출자: 제출 / Task 목록
    전체: 계정 관리 / 로그 아웃
    """,
    "myaccount":
    """계정 기본 정보를 수정합니다.
    비밀번호는 공란으로 두면 기존 비밀번호를 유지합니다.
    간단한 form validation이 작동합니다. validation에 실패해도 폼이 지워지지 않은 채 안내 메세지가 표시됩니다.
    관리자 외에는 여기서 계정을 삭제할 수 있습니다.(명세에 따라 관리자 계정은 삭제되지 않습니다)
    """,
    "signin":
    """패스워드 인증을 통해 회원 및 관리자가 시스템에 로그인 합니다.
    """,
    "signup":
    """새로운 회원이 가입할 수 있습니다.
    간단한 form validation이 작동합니다.  validation에 실패해도 폼이 지워지지 않은 채 안내 메세지가 표시됩니다.
    """,
    "tskcreate":
    """관리자가 새 task를 작성합니다.
    간단한 form validation이 작동합니다.
    New Field를 클릭해 Task의 새 columns을 추가할 수 있습니다.
    추가된 columns을 클릭하면 다시 삭제할 수 있습니다.
    """,
    "tskmgmt_per_task":
    """task의 속성을 수정하거나, 새 원본 데이터 타입을 작성합니다.
    activated를 변경하여 데이터 수집을 재개하거나 종료할 수 있습니다.
    activated가 체크되지 않은 경우 제출자에게 보이지 않습니다.
    아래 Pending Submitters에서, 이 task에 참여 대기 중인 제출자를 클릭하여, 승인하거나 거절할 수 있습니다.
    생성 중인 원본 데이터 타입의 fields를 클릭해 삭제할 수 있습니다.
    원본 데이터 타입은 SELECT절을 입력받아, 원본 데이터 타입의 columns과 테스크 데이터 테이블의 columns 간의 매핑 및 간단한 연산을 제공합니다.
    """,
    "tskmgmt":
    """Tasks를 관리합니다.
    WHERE절을 작성해 task를 검색할 수 있습니다.
    task를 클릭해서 해당 task를 수정합니다.
    """,
    "usrmgmt_per_user":
    """여기서 관리자가 각 제출자 별 참여 태스크 현황 혹은
    각 평가자 별 평가 파싱 데이터 시퀸스 파일의 현황을 확인합니다.
    SQL문을 통해 DB에 직접 데이터를 넣어도 반영됩니다.
    """,
    "usrmgmt":
    """WHERE 절을 입력하여 역할,나이대,성별,참여중인 태스크, ID를 기준으로 회원을 검색합니다.
    검색 결과를 다운받을 수 있습니다.
    사용자를 클릭하여 자세히 볼 수 있습니다.
    task_name: 해당 제출자가 관련된 task입니다.
    status: 제출자와 해당 task간의 상태입니다. a:approved, 참여 가능 / p:pending, 허가 대기 / r:rejected, 참여 거부됨
    """,
    "tskstat":
    """Tasks의 자세한 정보를 봅니다.
    WHERE절을 작성해 task를 검색할 수 있습니다.
    task를 클릭해서 해당 task를 자세히 봅니다.
    """,
    "tskstat_per_task":
    """해당 Task의 튜플을 보고, 검색을 하거나 csv파일로 다운받을 수 있습니다.
    SQL문으로 DB에 직접 데이터를 넣어도 작동합니다.
    이 task에 참여중인 제출자 목록이 표시됩니다.
    파싱 데이터 시퀸스 파일의 수와 태스크 데이터 테이블의 tuple의 개수가 표시됩니다.
    Task의 원본 데이터 타입 각각으로 들어온 제출물, 평가자의 평가를 기다리는 제출물, 평가를 통과한 제출물이 표시됩니다.
    """,
    "tsklist":
    """테스크의 목록입니다. 제출자는 여기서 테스크를 선택합니다.
    """,
    "tskdetail":
    """제출자가 권한을 요청하는 페이지입니다.
    """
}

def get_help_text(template):
    r=re.search("\/([^\/]+?)\.html$",template)
    if((r is not None) and (r.group(1) in _help_text)):
        return _help_text[r.group(1)]