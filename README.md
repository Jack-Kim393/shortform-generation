# Short-form Video Generator

이 프로젝트는 사용자가 업로드한 이미지와 MP3 파일을 사용하여 짧은 형식의 비디오를 자동으로 생성하는 Streamlit 기반의 애플리케이션입니다. 이미지 비율을 유지하면서 비디오 프레임에 맞추고, 부드러운 전환 효과와 배경 음악을 추가하여 전문적인 느낌의 비디오를 쉽게 만들 수 있습니다.

## 주요 기능

*   **이미지 및 MP3 파일 업로드:** 드래그 앤 드롭 방식으로 여러 이미지 파일과 하나의 MP3 파일을 쉽게 업로드할 수 있습니다.
*   **자동 비디오 생성:** 업로드된 이미지와 MP3를 기반으로 비디오를 자동으로 조합합니다.
*   **이미지 처리 정책:**
    *   이미지의 원본 비율을 유지합니다.
    *   비디오 프레임(1080x1920)에 이미지가 잘리지 않고 완전히 들어가도록 크기를 조정합니다.
    *   이미지 크기 조정 후 남는 공간은 검은색 배경으로 채워집니다.
    *   썸네일 생성 시에도 동일한 이미지 처리 정책이 적용됩니다.
*   **부드러운 전환 효과:** 이미지 클립 간에 0.5초의 부드러운 교차 페이드(crossfade) 전환 효과가 적용됩니다.
*   **오디오 통합:** 업로드된 MP3 파일의 특정 구간(40초~55초)이 비디오의 배경 음악으로 사용됩니다.
*   **비디오 다운로드:** 생성된 비디오를 웹 인터페이스에서 직접 다운로드할 수 있습니다.

## 시작하기

### 전제 조건

*   Python 3.8 이상
*   Git

### 설치

1.  **저장소 클론:**
    ```bash
    git clone https://github.com/Jack-Kim393/shortform-generation-image.git
    cd shortform-generation-image
    ```

2.  **가상 환경 생성 및 활성화:**
    ```bash
    python -m venv venv
    # macOS / Linux
    source venv/bin/activate
    # Windows
    .\venv\Scripts\activate
    ```

3.  **필요한 라이브러리 설치:**
    ```bash
    pip install -r requirements.txt
    ```

## 사용 방법

애플리케이션을 실행하는 방법은 운영 체제에 따라 다릅니다.

### macOS / Linux

프로젝트 루트 디렉토리에서 `start.command` 파일을 더블클릭하거나 터미널에서 다음 명령어를 실행합니다:

```bash
./start.command
```

### Windows

프로젝트 루트 디렉토리에서 `start.bat` 파일을 더블클릭합니다.

### 웹 인터페이스 사용

1.  앱이 실행되면 웹 브라우저에 Streamlit 애플리케이션이 열립니다.
2.  **"Upload Images"** 섹션에 비디오에 사용할 이미지 파일(PNG, JPG, JPEG)을 드래그 앤 드롭하거나 찾아보기 버튼을 클릭하여 업로드합니다. (최소 2개 이상의 이미지가 필요합니다.)
3.  **"Upload MP3 File"** 섹션에 배경 음악으로 사용할 MP3 파일을 드래그 앤 드롭하거나 찾아보기 버튼을 클릭하여 업로드합니다. (MP3 파일은 최소 55초 이상이어야 합니다.)
4.  **"Generate Video"** 버튼을 클릭하여 비디오 생성을 시작합니다.
5.  비디오 생성이 완료되면 미리보기와 함께 **"Download Video"** 버튼이 나타납니다. 이 버튼을 클릭하여 생성된 MP4 파일을 다운로드할 수 있습니다.

## 출력 파일

생성된 비디오 파일은 프로젝트 루트 디렉토리 내의 `output/` 폴더에 `shortform_video.mp4`로 저장됩니다.
생성된 썸네일 이미지는 `thumbnail/` 폴더에 `thumbnail.png`로 저장됩니다.

## 폴더 구조 (앱 실행 후)

```
shortform-generation-image/
├── .git/
├── .gitignore
├── app.py
├── requirements.txt
├── shortform-generation-image.code-workspace (선택 사항)
├── start.bat
├── start.command
├── output/
│   └── shortform_video.mp4
├── thumbnail/
│   └── thumbnail.png
└── venv/
    └── ... (가상 환경 파일)
```

## 독립 실행 파일 (Standalone Executables)

개발 환경 설정 없이 애플리케이션을 실행하고 싶다면, 미리 빌드된 독립 실행 파일을 사용할 수 있습니다.

### macOS (Apple Silicon / Intel)

1.  `dist/` 폴더로 이동합니다.
2.  `ShortformVideoGenerator.app` 파일을 더블클릭하여 애플리케이션을 실행합니다.

### Windows

Windows용 독립 실행 파일은 Windows 운영 체제에서 직접 빌드해야 합니다. 다음 단계를 따르세요:

1.  **Windows 환경에서 프로젝트 설정:**
    *   위의 "설치" 섹션에 따라 Python, 가상 환경, `requirements.txt` 설치를 완료합니다.
    *   `venv\Scripts\activate`를 사용하여 가상 환경을 활성화합니다.
    *   `pip install pyinstaller` 명령으로 `PyInstaller`를 설치합니다.

2.  **실행 파일 빌드:**
    프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다:
    ```bash
    .\venv\Scripts\pyinstaller --noconfirm --onefile --windowed --name "ShortformVideoGenerator" app.py
    ```
    *   빌드가 완료되면 `dist/` 폴더 안에 `ShortformVideoGenerator.exe` 파일이 생성됩니다.

3.  **애플리케이션 실행:**
    *   `dist/` 폴더로 이동합니다.
    *   `ShortformVideoGenerator.exe` 파일을 더블클릭하여 애플리케이션을 실행합니다.

**참고:** 독립 실행 파일은 크기가 클 수 있으며, 빌드 환경에 따라 특정 라이브러리(예: `moviepy`의 `ffmpeg`)가 제대로 포함되지 않을 경우 오류가 발생할 수 있습니다.
