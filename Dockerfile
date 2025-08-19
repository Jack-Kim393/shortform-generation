# 1. 기반 이미지 설정 (Python 3.9 슬림 버전)
FROM python:3.9-slim

# 2. 시스템 패키지 업데이트 및 FFmpeg 설치
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 로컬 라이브러리 및 requirements.txt 복사
COPY libs/ /app/libs/
COPY requirements.txt .

# 5. 파이썬 라이브러리 설치 (로컬 .whl 파일 먼저 설치)
RUN pip install --no-cache-dir /app/libs/streamlit_sortables-0.3.1-py3-none-any.whl
RUN pip install --no-cache-dir -r requirements.txt

# 6. 나머지 애플리케이션 소스 코드 복사
COPY . .

# 7. Streamlit 포트 노출
EXPOSE 8501

# 8. 애플리케이션 실행
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
