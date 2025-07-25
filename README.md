🏞️ Short-form Video Generator from Image & MP3
이미지와 MP3 파일만으로 전문가 수준의 숏폼 영상을 자동으로 생성하는 Streamlit 기반 웹 애플리케이션입니다.

🌟 주요 기능 (Key Features)
간편한 파일 업로드: 드래그 앤 드롭 방식으로 여러 이미지와 MP3 파일을 손쉽게 업로드합니다.

이미지 처리 정책:

비율 유지 리사이징: 원본 이미지의 비율을 유지하며 1080x1920 세로 영상 프레임에 맞춰 자동으로 크기를 조절합니다.

블랙 배경 패딩: 영상 프레임에서 남는 공간은 검은색 배경으로 채워 깔끔한 통일성을 제공합니다.

콘텐츠 자동 조합:

일관된 영상 길이: 업로드된 이미지를 반복/조합하여 총 10개의 이미지 클립으로 구성된 15초 영상을 생성합니다.

부드러운 전환 효과: 각 이미지 클립 사이에 0.5초 길이의 부드러운 교차 페이드(Crossfade) 효과를 적용합니다.

오디오 자동 편집: 업로드된 MP3 파일의 가장 매력적인 구간인 40초~55초 사이의 15초를 자동으로 잘라내어 배경 음악으로 사용합니다.

결과물 즉시 확인 및 다운로드: 영상 생성 완료 후 웹 화면에서 즉시 미리보고, MP4 파일로 다운로드할 수 있습니다.

💻 기술 사양 (Technical Specifications)
항목	사양
출력 해상도	1080 x 1920 (세로 숏폼)
영상 길이	15초
프레임 레이트	24 fps
비디오 코덱	H.264 (libx264)
오디오 코덱	AAC

Sheets로 내보내기
🚀 시작하기 (Getting Started)
사전 요구 사항
Python 3.8 이상

Git

설치 과정
저장소 클론:

Bash

git clone https://github.com/Jack-Kim393/shortform-generation-image.git
cd shortform-generation-image
가상 환경 생성 및 활성화:

Bash

python -m venv venv
macOS / Linux:

Bash

source venv/bin/activate
Windows:

Bash

.\venv\Scripts\activate
필요한 라이브러리 설치:

Bash

pip install -r requirements.txt
▶️ 사용 방법 (How to Use)
애플리케이션 실행:

macOS / Linux: 터미널에서 ./start.command 실행

Windows: start.bat 파일 더블클릭

웹 인터페이스 사용:

자동으로 열리는 웹 브라우저 화면의 "Upload Images" 영역에 이미지 파일(PNG, JPG)을 업로드합니다. (최소 2개 이상 필요)

"Upload MP3 File" 영역에 배경 음악으로 사용할 MP3 파일을 업로드합니다. (최소 55초 이상 길이 필요)

"Generate Video" 버튼을 클릭합니다.

생성이 완료되면 영상 미리보기와 함께 "Download Video" 버튼이 활성화됩니다.

📁 프로젝트 구조 (Project Structure)
shortform-generation-image/
├── .gitignore
├── app.py                  # Streamlit 애플리케이션 메인 코드
├── requirements.txt        # 필요한 Python 라이브러리 목록
├── start.bat               # Windows 실행 스크립트
├── start.command           # macOS/Linux 실행 스크립트
├── output/                 # 생성된 비디오가 저장되는 폴더
│   └── shortform_video.mp4
├── thumbnail/              # 생성된 썸네일이 저장되는 폴더
│   └── thumbnail.png
└── venv/                   # Python 가상 환경 폴더
🛠️ 주요 의존성 (Key Dependencies)
Streamlit: 웹 애플리케이션 인터페이스 구축

Moviepy: 비디오 클립 생성, 편집 및 렌더링

Pillow (PIL): 이미지 리사이징 및 처리

Numpy: 이미지 데이터를 Moviepy가 인식하는 배열 형태로 변환
