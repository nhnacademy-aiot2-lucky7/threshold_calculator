# 1. Python 3.10을 기본 이미지로 사용 (경량 버전)
FROM python:3.10-slim

# 2. prophet 및 numpy 관련 빌드 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. 컨테이너 내부 작업 디렉토리 지정
WORKDIR /app

# 4. requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 5. 나머지 소스코드 복사
COPY . .

# 6. 실행 명령어 (main.py를 실행)
ENV PYTHONPATH=/app
CMD ["python", "main.py"]
