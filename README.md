숏폼 영상 자동 생성기 (Short-form Video Generator)
이 프로젝트는 사용자가 업로드한 여러 이미지와 오디오 파일을 조합하여 짧은 형식의 동영상을 자동으로 생성하는 Streamlit 기반의 웹 애플리케이션입니다. 드래그 앤 드롭으로 이미지 순서를 직관적으로 편집하고, 영상 길이와 전환 효과 등 다양한 옵션을 직접 설정하여 개성 있는 동영상을 손쉽게 만들 수 있습니다.

주요 기능 ✨
다중 파일 업로드: 여러 이미지 파일(PNG, JPG, JPEG)과 하나의 오디오 파일(MP3, M4A)을 동시에 업로드할 수 있습니다.

드래그 앤 드롭 순서 편집: 업로드된 이미지의 순서를 마우스로 끌어다 놓는 방식으로 자유롭게 변경할 수 있습니다.

이미지 시퀀스 반복 (Looping): 설정한 영상 길이를 채우기 위해, 각 이미지의 표시 시간은 고정된 채 이미지 순서가 자동으로 반복됩니다. 지루하지 않고 역동적인 결과물을 만들 수 있습니다.

사용자 정의 설정:

최종 영상의 전체 길이를 슬라이더로 조절합니다.

이미지 간 전환(페이드) 효과의 지속 시간을 설정할 수 있습니다.

배경 음악으로 사용할 오디오 파일의 시작 지점을 직접 지정할 수 있습니다.

자동 영상 및 썸네일 생성: 설정된 값에 따라 FFmpeg가 영상과 썸네일을 자동으로 생성하고 인코딩합니다.

이미지 처리 정책:

이미지의 원본 비율을 유지하며, 1080x1920 세로 영상 규격에 맞게 조정됩니다.

남는 공간은 검은색 배경으로 채워져(Padding) 이미지가 잘리지 않습니다.

결과 확인 및 다운로드: 생성된 영상과 썸네일을 웹에서 바로 확인하고 다운로드할 수 있습니다.

기술 사양 (Technical Specifications)
항목	사양
출력 해상도	1080 x 1920 (세로 숏폼)
영상 길이	5초 ~ 60초 (사용자 설정 가능)
프레임 레이트	24 fps
비디오 코덱	H.264 (libx264)
오디오 코덱	AAC

Sheets로 내보내기
시작하기
전제 조건 (Prerequisites)
Python 3.8 이상

Git

FFmpeg: 로컬 개발 환경에서 실행할 때 필요합니다. 시스템에 설치되어 있고, 어느 경로에서든 접근 가능해야 합니다.

FFmpeg 공식 사이트에서 운영체제에 맞게 설치할 수 있습니다.

설치 (Installation)
저장소 클론:

Bash

git clone https://github.com/Jack-Kim393/shortform-generation-image.git
cd shortform-generation-image
가상 환경 생성 및 활성화:

Bash

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
필요한 라이브러리 설치:

Bash

pip install -r requirements.txt
사용 방법
애플리케이션 실행:
터미널에서 아래 명령어를 입력합니다.

Bash

streamlit run app.py
웹 인터페이스 사용:

앱이 실행되면 웹 브라우저가 자동으로 열립니다.

파일 업로드: 이미지(2개 이상)와 오디오 파일을 업로드합니다.

이미지 순서 편집: 드래그 앤 드롭으로 영상에 사용할 이미지 순서를 결정합니다. (첫 번째 이미지가 썸네일)

영상 설정: 영상 길이, 전환 효과, 음악 시작 위치를 조절합니다. 영상 길이를 늘리면 이미지 순서가 자동으로 반복됩니다.

(선택) "설정된 음악 구간 미리듣기" 버튼으로 오디오를 확인할 수 있습니다.

영상 생성하기: 버튼을 누르면 영상 생성이 시작됩니다.

결과 확인 및 다운로드: 생성이 완료되면 결과물을 확인하고 썸네일과 영상을 각각 다운로드합니다.

주요 의존성 (Key Dependencies)
라이브러리 / 도구	역할 (Role)
Streamlit	사용자 친화적인 웹 애플리케이션 인터페이스를 구축합니다.
FFmpeg (외부 도구)	이미지 스케일링, 전환 효과, 오디오/비디오 결합 등 모든 핵심 영상 처리 작업을 수행합니다.
streamlit-sortables	UI에서 드래그 앤 드롭으로 리스트 순서를 변경하는 기능을 제공합니다.

Sheets로 내보내기
독립 실행 파일 (.exe, .app) 만들기
이 섹션은 다른 사람에게 쉽게 배포할 수 있도록, FFmpeg를 포함한 하나의 실행 파일을 만드는 방법을 안내합니다. 이 방법으로 만든 파일은 최종 사용자가 FFmpeg를 별도로 설치할 필요가 없습니다.

1. 공통 준비
먼저 프로젝트 폴더 구조를 아래와 같이 준비합니다.

shortform-generation/
├── libs/
│   └── streamlit_sortables-0.3.1-py3-none-any.whl
├── app.py
└── requirements.txt
app.py와 requirements.txt는 최종 버전으로 준비합니다.

libs 폴더를 만들고, 이전에 다운로드한 streamlit_sortables...whl 파일을 그 안에 넣습니다.

2. Windows용 .exe 만들기
Windows PC에서 진행해야 합니다.

FFmpeg 준비: gyan.dev에서 essentials 버전 .zip 파일을 받아 압축을 풀고, bin 폴더 안의 ffmpeg.exe 파일을 프로젝트 루트 폴더(app.py가 있는 곳)에 복사합니다.

빌드 실행: 터미널에서 아래 명령어들을 순서대로 실행합니다.

Bash

# 가상 환경 생성 및 활성화, 라이브러리 설치
python -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# PyInstaller로 빌드 실행
pyinstaller --noconfirm --onefile --windowed --name "ShortformVideoGenerator" --add-data "venv\Lib\site-packages\streamlit\frontend;streamlit\frontend" --add-binary "ffmpeg.exe;." app.py
결과: dist 폴더 안에 ShortformVideoGenerator.exe 파일이 생성됩니다.

3. macOS용 .app 만들기
Mac에서 진행해야 합니다.

FFmpeg 준비: ffmpeg.org 등에서 macOS용 Static build를 다운로드하여, 압축 푼 폴더 안의 ffmpeg 파일(확장자 없음)을 프로젝트 루트 폴더에 복사합니다.

빌드 실행: Mac의 터미널에서 아래 명령어들을 순서대로 실행합니다.

Bash

# 가상 환경 생성 및 활성화, 라이브러리 설치
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# PyInstaller로 빌드 실행 (macOS에서는 경로 구분자가 ':' 입니다)
pyinstaller --noconfirm --onefile --windowed --name "ShortformVideoGenerator" --add-data "venv/lib/python*/site-packages/streamlit/frontend:streamlit/frontend" --add-binary "ffmpeg:." app.py
결과: dist 폴더 안에 ShortformVideoGenerator.app 파일이 생성됩니다.