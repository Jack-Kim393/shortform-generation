# 숏폼 영상 자동 생성기 (Short-form Video Generator)

이 프로젝트는 사용자가 업로드한 여러 이미지와 오디오 파일을 조합하여 짧은 형식의 동영상을 자동으로 생성하는 **Streamlit** 기반의 웹 애플리케이션입니다. 드래그 앤 드롭으로 이미지 순서를 직관적으로 편집하고, 영상 길이와 전환 효과 등 다양한 옵션을 직접 설정하여 개성 있는 동영상을 손쉽게 만들 수 있습니다.

## macOS 호환성 업데이트 및 주요 개선사항 (2025-07-28)

Windows에서 정상 작동하던 프로젝트를 macOS 환경에서도 완벽하게 실행하고 빌드할 수 있도록 수정했습니다. 이 과정에서 발생한 다수의 환경 설정 문제와 FFmpeg의 크로스플랫폼 호환성 오류를 해결하고, 영상 생성 로직을 전면 개선하여 안정성을 확보했습니다.

**주요 변경 및 수정 사항:**

*   **macOS 환경설정 문제 해결**
    *   `requirements.txt`에 하드코딩되어 있던 Windows 절대 경로를 모든 OS에서 작동하는 상대 경로(`./libs/...`)로 수정하여 프로젝트 이식성을 확보했습니다.
    *   Homebrew를 이용한 FFmpeg 설치 및 터미널 PATH 설정 문제를 해결하여 Mac에서도 FFmpeg 명령어를 정상적으로 사용할 수 있도록 했습니다.
    *   로컬 의존성 파일인 `streamlit_sortables` (.whl)이 누락된 경우를 대비해 수동 설치 과정을 명확히 했습니다.
*   **FFmpeg 크로스플랫폼 호환성 오류 수정**
    *   macOS 환경의 최신 FFmpeg에서 발생하던 고질적인 constant frame rate 및 SAR mismatch 오류를 해결했습니다.
    *   단순 필터 추가 방식이 아닌, FFmpeg 명령어 구조 자체를 변경하여 근본적인 원인을 해결했습니다.
*   **영상 생성 로직 리팩토링**
    *   기존의 불안정한 필터(`tpad`) 로직을 폐기했습니다.
    *   각 이미지 입력단에서 `-t` 옵션으로 클립 길이를 명확히 지정하고, `fade` 효과를 적용한 뒤 `concat` 필터로 이어 붙이는 방식으로 로직을 전면 재작성하여, 어떤 환경에서도 일관된 결과물을 보장하도록 안정성을 대폭 향상시켰습니다.

## 주요 기능 ✨

* **다중 파일 업로드**: 여러 이미지 파일(**PNG, JPG, JPEG**)과 여러 오디오 파일(**MP3, M4A**)을 동시에 업로드할 수 있습니다.
* **드래그 앤 드롭 순서 편집**: 업로드된 이미지와 오디오의 순서를 마우스로 끌어다 놓는 방식으로 자유롭게 변경할 수 있습니다.
* **오디오 구간 설정**: 각 오디오 파일별로 사용할 시작 시간과 길이를 직접 지정하여 원하는 부분만 잘라 쓸 수 있습니다.
* **이미지 시퀀스 반복 (Looping)**: 설정한 영상 길이를 채우기 위해, 각 이미지의 표시 시간은 고정된 채 이미지 순서가 자동으로 반복됩니다.
* **사용자 정의 설정**:
    * 최종 영상의 전체 길이를 슬라이더로 조절합니다.
    * 이미지 간 전환(페이드) 효과의 지속 시간을 설정할 수 있습니다.
* **자동 영상 및 썸네일 생성**: 설정된 값에 따라 **FFmpeg**가 오디오 클립들을 병합하고, 이미지와 합쳐 영상과 썸네일을 자동으로 생성합니다.
* **이미지 처리 정책**:
    * 이미지의 원본 비율을 유지하며, 1080x1920 세로 영상 규격에 맞게 조정됩니다.
    * 남는 공간은 검은색 배경으로 채워져(Padding) 이미지가 잘리지 않습니다.
* **결과 확인 및 다운로드**: 생성된 영상과 썸네일을 웹에서 바로 확인하고 다운로드할 수 있습니다.

## 기술 사양 (Technical Specifications)

| 항목              | 사양                          |
| :---------------- | :---------------------------- |
| **출력 해상도** | 1080 x 1920 (세로 숏폼)       |
| **영상 길이** | 5초 ~ 180초 (사용자 설정 가능) |
| **프레임 레이트** | 24 fps                        |
| **비디오 코덱** | H.264 (libx264)               |
| **오디오 코덱** | AAC                           |

## 시작하기

### 전제 조건 (Prerequisites)

* Python 3.8 이상
* Git
* **FFmpeg**: 로컬 개발 환경에서 실행할 때 필요합니다. 시스템에 설치되어 있고, 어느 경로에서든 접근 가능해야 합니다.
    * [FFmpeg 공식 사이트](https://ffmpeg.org/download.html)에서 운영체제에 맞게 설치할 수 있습니다.

### 설치 (Installation)

1.  **저장소 클론:**
    ```bash
    git clone https://github.com/Jack-Kim393/shortform-generation-image.git
    cd shortform-generation-image
    ```

2.  **가상 환경 생성 및 활성화:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **필요한 라이브러리 설치:**
    ```bash
    pip install -r requirements.txt
    ```
    > **macOS/Linux 사용자 참고:** `requirements.txt`에 포함된 `streamlit_sortables` 라이브러리가 로컬 `.whl` 파일로 지정되어 있습니다. 만약 `pip install -r requirements.txt` 실행 시 이 부분에서 오류가 발생하면, 아래 명령어를 통해 수동으로 먼저 설치한 후 다시 시도해 주세요.
    > ```bash
    > pip install libs/streamlit_sortables-0.3.1-py3-none-any.whl
    > pip install -r requirements.txt
    > ```

## 사용 방법

1.  **애플리케이션 실행:**
    터미널에서 아래 명령어를 입력합니다.
    ```bash
    streamlit run app.py
    ```

2.  **웹 인터페이스 사용:**
    * 앱이 실행되면 웹 브라우저가 자동으로 열립니다.
    * **파일 업로드**: 이미지(2개 이상)와 오디오 파일(1개 이상)을 업로드합니다.
    * **순서 및 구간 편집**:
        * **이미지**: 드래그 앤 드롭으로 영상에 사용할 이미지 순서를 결정합니다. (첫 번째 이미지가 썸네일)
        * **오디오**: 드래그 앤 드롭으로 순서를 정하고, 각 오디오의 '시작(초)'와 '사용할 길이(초)'를 설정합니다.
    * **영상 설정**: 영상 길이, 전환 효과를 조절합니다.
    * **(선택)** "설정된 음악 구간 미리듣기" 버튼으로 최종 오디오를 확인할 수 있습니다.
    * **영상 생성하기**: 버튼을 누르면 영상 생성이 시작됩니다.
    * **결과 확인 및 다운로드**: 생성이 완료되면 결과물을 확인하고 썸네일과 영상을 각각 다운로드합니다.

## 주요 의존성 (Key Dependencies)

| 라이브러리 / 도구       | 역할 (Role)                                                        |
| :---------------------- | :----------------------------------------------------------------- |
| **Streamlit** | 사용자 친화적인 웹 애플리케이션 인터페이스를 구축합니다.           |
| **FFmpeg** (외부 도구)  | 이미지 스케일링, 전환 효과, 오디오/비디오 결합 등 모든 핵심 영상 처리 작업을 수행합니다. |
| **streamlit-sortables** | UI에서 드래그 앤 드롭으로 리스트 순서를 변경하는 기능을 제공합니다. |

---

## 독립 실행 파일 (.exe, .app) 만들기

이 섹션은 다른 사람에게 쉽게 배포할 수 있도록, **FFmpeg를 포함한** 하나의 실행 파일을 만드는 방법을 안내합니다. 이 방법으로 만든 파일은 최종 사용자가 FFmpeg를 별도로 설치할 필요가 없습니다.

### 1. 공통 준비

먼저 프로젝트 폴더 구조을 아래와 같이 준비합니다.

* **`shortform-generation/`** (프로젝트 루트 폴더)
    * **`libs/`**
        * `streamlit_sortables-0.3.1-py3-none-any.whl`
    * `app.py`
    * `requirements.txt`

* `app.py`와 `requirements.txt`는 이전에 안내된 최종 버전으로 준비합니다.
* `libs` 폴더를 만들고, 이전에 다운로드한 `streamlit_sortables...whl` 파일을 그 안에 넣습니다.

### 2. Windows용 `.exe` 만들기

**Windows PC에서 진행해야 합니다.**

1.  **FFmpeg 준비**: [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)에서 `essentials` 버전 `.zip` 파일을 받아 압축을 풀고, `bin` 폴더 안의 **`ffmpeg.exe`** 파일을 프로젝트 루트 폴더(`app.py`가 있는 곳)에 복사합니다.

2.  **빌드 실행**: 터미널에서 아래 명령어들을 순서대로 실행합니다.
    ```bash
    # 가상 환경 생성 및 활성화, 라이브러리 설치
    python -m venv venv
    .\venv\Scripts\activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller

    # PyInstaller로 빌드 실행
    pyinstaller --noconfirm --onefile --windowed --name "ShortformVideoGenerator" --add-data "venv\Lib\site-packages\streamlit\frontend;streamlit\frontend" --add-binary "ffmpeg.exe;." app.py
    ```

3.  **결과**: `dist` 폴더 안에 `ShortformVideoGenerator.exe` 파일이 생성됩니다.

### 3. macOS용 `.app` 만들기

**Mac에서 진행해야 합니다.**

1.  **FFmpeg 준비**: [ffmpeg.org](https://ffmpeg.org/download.html) 등에서 macOS용 `Static build`를 다운로드하여, 압축 푼 폴더 안의 **`ffmpeg`** 파일(확장자 없음)을 프로젝트 루트 폴더에 복사합니다.

2.  **빌드 실행**: Mac의 터미널에서 아래 명령어들을 순서대로 실행합니다.
    ```bash
    # 가상 환경 생성 및 활성화, 라이브러리 설치
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller

    # PyInstaller로 빌드 실행 (macOS에서는 경로 구분자가 ':' 입니다)
    pyinstaller --noconfirm --onefile --windowed --name "ShortformVideoGenerator" --add-data "venv/lib/python*/site-packages/streamlit/frontend:streamlit/frontend" --add-binary "ffmpeg:." app.py
    ```

3.  **결과**: `dist` 폴더 안에 `ShortformVideoGenerator.app` 파일이 생성됩니다.