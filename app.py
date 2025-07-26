import os
import streamlit as st
from pathlib import Path
import tempfile
import uuid
import subprocess

# --- 1. 경로 및 기본 설정 ---
st.set_page_config(page_title="Short-form Video Generator", layout="centered")

# 임시 파일 및 출력 디렉토리 설정
try:
    script_dir = Path(__file__).parent
except NameError:
    script_dir = Path.cwd()

output_dir = script_dir / "output"
output_dir.mkdir(exist_ok=True)


# --- 2. 핵심 기능 함수 ---
def generate_video_with_subprocess(image_paths, mp3_path, output_path, video_duration, transition_duration, mp3_start_time):
    """
    [핵심 수정] 3단계 접근법으로 비디오를 안정적으로 생성하는 함수
    1. 무음 비디오 생성 -> 2. 오디오 트랙 생성 -> 3. 비디오와 오디오 결합
    """
    num_images = len(image_paths)
    if num_images < 2:
        st.error("오류: 이미지는 2개 이상 필요합니다.")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        silent_video_path = temp_dir_path / "silent_video.mp4"
        final_audio_path = temp_dir_path / "final_audio.aac"

        try:
            # --- 1단계: 무음 비디오 생성 ---
            filter_complex_video = ""
            for i, img_path in enumerate(image_paths):
                filter_complex_video += f"[{i}:v]settb=AVTB,fps=24,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:-1:-1:color=black[v{i}];"
            
            clip_duration = (video_duration + (num_images - 1) * transition_duration) / num_images
            prev_stream = "[v0]"
            for i in range(1, num_images):
                offset = i * (clip_duration - transition_duration)
                out_stream_name = "[video_out]" if i == num_images - 1 else f"[vt{i}]"
                filter_complex_video += f"{prev_stream}[v{i}]xfade=transition=fade:duration={transition_duration}:offset={offset}{out_stream_name};"
                prev_stream = out_stream_name

            cmd_video = ['ffmpeg', '-y']
            for img_path in image_paths:
                cmd_video.extend(['-loop', '1', '-i', img_path])
            cmd_video.extend([
                '-filter_complex', filter_complex_video,
                '-map', '[video_out]',
                '-t', str(video_duration),
                '-vcodec', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'veryfast',
                str(silent_video_path)
            ])
            subprocess.run(cmd_video, check=True, capture_output=True, text=True, encoding='utf-8')

            # --- 2단계: 오디오 트랙 생성 ---
            cmd_audio = [
                'ffmpeg', '-y',
                '-i', mp3_path,
                '-ss', str(mp3_start_time),
                '-t', str(video_duration),
                '-acodec', 'aac',
                '-ar', '44100',
                '-b:a', '192k',
                str(final_audio_path)
            ]
            subprocess.run(cmd_audio, check=True, capture_output=True, text=True, encoding='utf-8')

            # --- 3단계: 무음 비디오와 오디오 결합 ---
            cmd_combine = [
                'ffmpeg', '-y',
                '-i', str(silent_video_path),
                '-i', str(final_audio_path),
                '-c:v', 'copy',  # 비디오는 재인코딩 없이 복사
                '-c:a', 'copy',  # 오디오도 재인코딩 없이 복사
                '-map', '0:v:0',
                '-map', '1:a:0',
                str(output_path)
            ]
            subprocess.run(cmd_combine, check=True, capture_output=True, text=True, encoding='utf-8')
            
            return True

        except subprocess.CalledProcessError as e:
            st.error("영상 생성 중 FFmpeg 오류가 발생했습니다.")
            st.code(e.stderr) # 에러 로그를 직접 보여줌
            return False


# --- 3. Streamlit UI 구성 ---
st.title("🏞️ 숏폼 영상 자동 생성기")

if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'thumbnail_path' not in st.session_state:
    st.session_state.thumbnail_path = None
if 'run_id' not in st.session_state:
    st.session_state.run_id = str(uuid.uuid4())

with st.expander("사용법 보기 👀"):
    st.write("이미지(2개 이상)와 MP3 파일을 업로드하고 설정을 맞춘 뒤 '영상 생성하기' 버튼을 누르세요.")

st.header("1. 파일 업로드")
uploaded_images = st.file_uploader(
    "이미지를 2개 이상 업로드하세요.", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)
uploaded_mp3 = st.file_uploader(
    "배경 음악(MP3)을 업로드하세요.", type=["mp3"]
)

st.header("2. 영상 설정")
video_duration_sec = st.slider(
    "전체 영상 길이 (초)", min_value=5, max_value=60, value=15, step=1
)
transition_duration_sec = st.slider(
    "화면 전환 효과 시간 (초)", min_value=0.1, max_value=2.0, value=0.5, step=0.1
)
mp3_start_time = st.number_input(
    "음악 시작 위치 (초)", min_value=0, value=15, step=1
)

if uploaded_mp3:
    if st.button("🎧 설정된 음악 구간 미리듣기"):
        with st.spinner("미리듣기 생성 중..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_in, \
                 tempfile.NamedTemporaryFile(delete=False, suffix="_preview.mp3") as temp_out:
                
                temp_in.write(uploaded_mp3.getbuffer())
                input_path = temp_in.name
                output_path = temp_out.name
            
            try:
                command = [
                    'ffmpeg', '-y',
                    '-i', input_path,
                    '-ss', str(mp3_start_time),
                    '-t', str(video_duration_sec),
                    output_path
                ]
                subprocess.run(command, check=True, capture_output=True)
                st.audio(output_path)
            except subprocess.CalledProcessError as e:
                st.error("미리듣기 생성에 실패했습니다.")
                st.code(e.stderr)
            finally:
                if os.path.exists(input_path): os.remove(input_path)
                if os.path.exists(output_path): os.remove(output_path)

st.header("3. 영상 생성")
if st.button("🚀 영상 생성하기!"):
    if uploaded_images and uploaded_mp3 and len(uploaded_images) >= 2:
        with st.spinner('영상을 생성 중입니다... 잠시만 기다려주세요.'):
            # 파일을 임시 디렉토리에 저장하지 않고 바로 BytesIO로 처리 시도
            with tempfile.TemporaryDirectory() as temp_dir:
                image_paths = []
                for file in uploaded_images:
                    unique_name = f"{uuid.uuid4().hex}_{file.name}"
                    img_path = Path(temp_dir) / unique_name
                    img_path.write_bytes(file.getbuffer())
                    image_paths.append(str(img_path))
                
                mp3_path = Path(temp_dir) / "audio.mp3"
                mp3_path.write_bytes(uploaded_mp3.getbuffer())

                run_id = str(uuid.uuid4())
                st.session_state.run_id = run_id
                video_output_path = output_dir / f"video_{run_id}.mp4"
                thumb_output_path = output_dir / f"thumb_{run_id}.png"

                success = generate_video_with_subprocess(
                    image_paths, str(mp3_path), video_output_path,
                    video_duration_sec, transition_duration_sec, mp3_start_time
                )

                if success:
                    subprocess.run([
                        'ffmpeg', '-y', '-i', str(video_output_path),
                        '-vframes', '1', str(thumb_output_path)
                    ], check=True, capture_output=True, text=True)
                    st.success("영상 생성 완료!")
                    st.session_state.video_path = str(video_output_path)
                    st.session_state.thumbnail_path = str(thumb_output_path)
                else:
                    st.session_state.video_path = None
                    st.session_state.thumbnail_path = None
    else:
        st.warning("이미지(2개 이상)와 MP3 파일을 모두 업로드해주세요.")

if st.session_state.video_path and st.session_state.thumbnail_path:
    st.header("4. 결과 확인 및 다운로드")
    if Path(st.session_state.video_path).exists() and Path(st.session_state.thumbnail_path).exists():
        st.image(st.session_state.thumbnail_path, caption="생성된 썸네일")
        with open(st.session_state.thumbnail_path, "rb") as f:
            st.download_button(
                "썸네일 이미지 다운로드", data=f.read(),
                file_name=f"thumbnail_{st.session_state.run_id}.png", mime="image/png"
            )
        st.markdown("---")
        st.video(st.session_state.video_path)
        with open(st.session_state.video_path, "rb") as f:
            st.download_button(
                "영상 다운로드", data=f.read(),
                file_name=f"video_{st.session_state.run_id}.mp4", mime="video/mp4"
            )
    else:
        st.error("생성된 파일을 찾을 수 없습니다. 다시 생성해주세요.")
        st.session_state.video_path = None
        st.session_state.thumbnail_path = None