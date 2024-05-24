FROM python:3.10.14-slim-bullseye

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DEBUG=false

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt update -y && apt upgrade -y

# 작업 디렉토리 설정
WORKDIR /usr/src/app

# Poetry 설치
RUN pip install poetry==1.8.2

# Poetry 가상 환경 생성 비활성화
RUN poetry config virtualenvs.create false

# `pyproject.toml`과 `poetry.lock` 파일을 컨테이너에 복사
COPY pyproject.toml poetry.lock ./

# Poetry를 사용하여 의존성 설치
RUN poetry install

# 애플리케이션 코드 복사
COPY . .

# 헬스체크 명령 추가
HEALTHCHECK --interval=1m --timeout=30s \
    CMD curl -f http://localhost:8080/health || exit 1

# 애플리케이션 포트 노출
EXPOSE 8080

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
