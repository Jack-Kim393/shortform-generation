import os
import streamlit as st
from pathlib import Path
import tempfile
import uuid
import subprocess
from streamlit_sortables import sort_items
import io
import math
import sys

# ★★★ 각 이미지의 목표 표시 시간 (초)
TARGET_IMAGE_DURATION = 2.0

# FFmpeg 실행 파일 경로를 찾는 함수
def get_ffmpeg_path():
    """실행 파일로 패키징되었는지, 어떤 운영체제인지에 따라 올바른 FFmpeg 경로를 반환합니다."""
    is_windows = (sys.platform == "win32")
    ffmpeg_filename = "ffmpeg.exe" if is_windows else "ffmpeg"
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        return os.path.join(application_path, ffmmap_filename)
    else:
        return "ffmpeg"

# --- 1. 경로 및 기본 설정 ---
st.set_page_config(page_title="Short-form Video Generator", layout="wide")
st.title("🏞️ 숏폼 영상 자동 생성기")

try:
    script_dir = Path(__file__).parent
except NameError:
    script_dir = Path.cwd()
output_dir = script_dir / "output"
output_dir.mkdir(exist_ok=True)

# --- 2. 핵심 기능 함수 (영상 생성 로직) ---
def generate_video(image_paths, audio_configs, output_path, video_duration, transition_duration, image_display_duration, progress_bar):
    num_images = len(image_paths)
    num_audios = len(audio_configs)
    ffmpeg_path = get_ffmpeg_path()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        silent_video_path = temp_dir_path / "silent_video.mp4"
        final_audio_path = temp_dir_path / "final_audio.aac"

        try:
            # --- 1. 무음 비디오 생성 ---
            progress_bar.progress(10, text="숏폼 비디오 생성을 시작합니다...")
            cmd_inputs_video = []
            clip_duration = image_display_duration + transition_duration
            for img_path in image_paths:
                cmd_inputs_video.extend(['-loop', '1', '-framerate', '24', '-t', str(clip_duration), '-i', str(img_path)])

            filter_complex_video = ""
            clip_streams_video = []
            for i in range(num_images):
                fade_out_start = image_display_duration
                filter_complex_video += (
                    f"[{i}:v]format=yuv420p,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,"
                    f"setsar=1,"
                    f"fade=t=in:st=0:d={transition_duration},"
                    f"fade=t=out:st={fade_out_start}:d={transition_duration},"
                    f"setpts=PTS-STARTPTS[v{i}];"
                )
                clip_streams_video.append(f"[v{i}]")
            
            filter_complex_video += f"{''.join(clip_streams_video)}concat=n={num_images}:v=1:a=0[video_out]"

            cmd_video = [
                ffmpeg_path, '-y', *cmd_inputs_video,
                '-filter_complex', filter_complex_video,
                '-map', '[video_out]', '-t', str(video_duration), '-vcodec', 'libx264',
                '-preset', 'veryfast', '-pix_fmt', 'yuv420p', str(silent_video_path)
            ]
            subprocess.run(cmd_video, check=True, capture_output=True, text=True, encoding='utf-8')
            
            # --- 2. 오디오 클립 생성 및 병합 ---
            progress_bar.progress(40, text="오디오 클립을 자르고 병합합니다...")
            cmd_inputs_audio = []
            filter_complex_audio = ""
            audio_streams = []

            for i, config in enumerate(audio_configs):
                cmd_inputs_audio.extend(['-i', str(config['path'])])
                filter_complex_audio += f"[{i}:a]atrim=start={config['start']}:duration={config['duration']},asetpts=PTS-STARTPTS[a{i}];"
                audio_streams.append(f"[a{i}]")

            filter_complex_audio += f"{''.join(audio_streams)}concat=n={num_audios}:v=0:a=1[audio_out]"
            
            cmd_audio = [
                ffmpeg_path, '-y', *cmd_inputs_audio,
                '-filter_complex', filter_complex_audio,
                '-map', '[audio_out]', '-acodec', 'aac', '-ar', '44100', '-b:a', '192k',
                str(final_audio_path)
            ]
            subprocess.run(cmd_audio, check=True, capture_output=True, text=True, encoding='utf-8')

            # --- 3. 최종 영상 결합 ---
            progress_bar.progress(80, text="오디오 처리 완료. 최종 영상을 결합합니다...")
            cmd_combine = [
                ffmpeg_path, '-y', '-i', str(silent_video_path), '-i', str(final_audio_path),
                '-c:v', 'copy', '-c:a', 'copy', '-map', '0:v:0', '-map', '1:a:0', 
                '-t', str(video_duration), # 최종 영상 길이 제한
                str(output_path)
            ]
            subprocess.run(cmd_combine, check=True, capture_output=True, text=True, encoding='utf-8')
            
            progress_bar.progress(100, text="영상 생성 완료!")
            return True
        except subprocess.CalledProcessError as e:
            st.error("영상 생성 중 FFmpeg 오류가 발생했습니다.")
            st.code(f"FFmpeg Error:\n{e.stderr.decode('utf-8') if hasattr(e.stderr, 'decode') else e.stderr}")
            return False

# --- 3. Streamlit UI 구성 ---
if 'uploaded_images' not in st.session_state: st.session_state.uploaded_images = []
if 'audio_configs' not in st.session_state: st.session_state.audio_configs = {}
if 'video_path' not in st.session_state: st.session_state.video_path = None
if 'thumbnail_path' not in st.session_state: st.session_state.thumbnail_path = None
if 'run_id' not in st.session_state: st.session_state.run_id = str(uuid.uuid4())

with st.expander("사용법 보기 👀"):
    st.write("""
    1.  **파일 업로드**: 2개 이상의 이미지와 1개 이상의 오디오 파일을 업로드합니다.
    2.  **순서 및 구간 편집**:
        - **이미지**: 드래그 앤 드롭으로 순서를 바꿀 수 있습니다. 첫 번째 이미지가 썸네일로 사용됩니다.
        - **오디오**: 드래그 앤 드롭으로 순서를 바꾸고, 각 음원의 `시작(초)`과 `사용할 길이(초)`를 설정합니다.
    3.  **영상 설정**: 영상 길이, 전환 효과를 조절합니다.
    4.  **영상 생성하기**: 버튼을 누르면 설정된 내용으로 영상이 만들어집니다.
    """)

st.header("1. 파일 업로드")
cols_upload = st.columns(2)
with cols_upload[0]:
    uploaded_images = st.file_uploader("이미지를 2개 이상 업로드하세요.", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
with cols_upload[1]:
    uploaded_audios = st.file_uploader("배경 음악을 1개 이상 업로드하세요.", type=["mp3", "m4a"], accept_multiple_files=True)

# 이미지 파일 관리
if uploaded_images:
    current_files = {f.name: f for f in st.session_state.uploaded_images}
    for f in uploaded_images: current_files[f.name] = f
    st.session_state.uploaded_images = list(current_files.values())

# 오디오 파일 및 설정 관리
if uploaded_audios:
    new_audio_configs = st.session_state.audio_configs.copy()
    for f in uploaded_audios:
        if f.name not in new_audio_configs:
            new_audio_configs[f.name] = {'file': f, 'start': 15, 'duration': 5.0}
    st.session_state.audio_configs = new_audio_configs

st.header("2. 영상 설정")
cols_settings = st.columns(2)
with cols_settings[0]: video_duration_sec = st.slider("전체 영상 길이 (초)", 5, 180, 15)
with cols_settings[1]: transition_duration_sec = st.slider("화면 전환 효과 시간 (초)", 0.1, 3.0, 0.5, 0.1)

# 업로드된 이미지 순서 편집 UI
if st.session_state.uploaded_images:
    st.subheader("🖼️ 업로드된 이미지 (드래그로 순서 변경)")
    items_to_sort = [file.name for file in st.session_state.uploaded_images]
    file_lookup = {file.name: file for file in st.session_state.uploaded_images}
    
    reordered_filenames = sort_items(items_to_sort, direction='horizontal')
    
    if reordered_filenames:
        st.session_state.uploaded_images = [file_lookup[name] for name in reordered_filenames]

    cols_per_row = 10
    for i, file in enumerate(st.session_state.uploaded_images):
        if i % cols_per_row == 0: cols = st.columns(cols_per_row)
        with cols[i % cols_per_row]:
            st.image(file, use_container_width=True, caption=f"{i+1}. {file.name[:10]}...")
            if i == 0: st.info("썸네일", icon="🖼️")

    # 이미지 타임라인 표시
    st.subheader("📊 이미지 타임라인")
    timeline_cols = st.columns(4)
    current_time = 0.0
    image_duration_no_transition = TARGET_IMAGE_DURATION
    for i, file in enumerate(st.session_state.uploaded_images):
        start_time = current_time
        end_time = start_time + image_duration_no_transition
        with timeline_cols[i % 4]:
            st.metric(label=f"{i+1}. {file.name[:15]}...", value=f"{start_time:.1f}s - {end_time:.1f}s")
        current_time = end_time - transition_duration_sec # 다음 이미지는 전환 시간만큼 겹침

# 업로드된 오디오 순서 및 구간 편집 UI
if st.session_state.audio_configs:
    st.subheader("🎵 업로드된 오디오 (드래그 및 구간 설정)")
    
    audio_filenames_to_sort = list(st.session_state.audio_configs.keys())
    reordered_audio_filenames = sort_items(audio_filenames_to_sort, direction='vertical')
    
    if reordered_audio_filenames:
        st.session_state.audio_configs = {name: st.session_state.audio_configs[name] for name in reordered_audio_filenames}

    for i, (name, config) in enumerate(st.session_state.audio_configs.items()):
        cols = st.columns([4, 2, 2])
        with cols[0]:
            st.markdown(f"**{i+1}순위**: {name}")
        with cols[1]:
            config['start'] = st.number_input("시작(초)", min_value=0, value=config['start'], key=f"start_{name}")
        with cols[2]:
            config['duration'] = st.number_input("사용할 길이(초)", min_value=0.1, value=config['duration'], step=0.1, key=f"duration_{name}")

if st.session_state.audio_configs:
    if st.button("🎧 설정된 음악 구간 미리듣기"):
        with st.spinner("미리듣기 오디오 생성 중..."):
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir_path = Path(temp_dir)
                    
                    audio_configs_for_preview = []
                    for name, config in st.session_state.audio_configs.items():
                        temp_audio_path = temp_dir_path / name
                        temp_audio_path.write_bytes(config['file'].getbuffer())
                        audio_configs_for_preview.append({
                            'path': str(temp_audio_path),
                            'start': config['start'],
                            'duration': config['duration']
                        })

                    ffmpeg_path = get_ffmpeg_path()
                    cmd_inputs_audio = []
                    filter_complex_audio = ""
                    audio_streams = []

                    for i, config in enumerate(audio_configs_for_preview):
                        cmd_inputs_audio.extend(['-i', config['path']])
                        filter_complex_audio += f"[{i}:a]atrim=start={config['start']}:duration={config['duration']},asetpts=PTS-STARTPTS[a{i}];"
                        audio_streams.append(f"[a{i}]")

                    filter_complex_audio += f"{''.join(audio_streams)}concat=n={len(audio_streams)}:v=0:a=1[audio_out]"
                    
                    cmd = [
                        ffmpeg_path, '-y', *cmd_inputs_audio,
                        '-filter_complex', filter_complex_audio,
                        '-map', '[audio_out]', '-f', 'mp3', '-'
                    ]
                    result = subprocess.run(cmd, check=True, capture_output=True)
                    st.audio(result.stdout, format='audio/mp3')

            except subprocess.CalledProcessError as e:
                st.error("미리듣기 생성에 실패했습니다.")
                st.code(e.stderr.decode('utf-8') if hasattr(e.stderr, 'decode') else e.stderr)

st.header("3. 영상 생성")
if st.button("🚀 영상 생성하기!"):
    image_order = st.session_state.uploaded_images
    audio_configs = st.session_state.audio_configs

    if not audio_configs: st.warning("오디오 파일을 1개 이상 업로드해주세요.")
    elif len(image_order) < 2: st.warning("이미지를 2개 이상 업로드하고 순서를 정해주세요.")
    else:
        progress_bar = st.progress(0, text="준비 중...")
        time_per_slot = TARGET_IMAGE_DURATION + transition_duration_sec
        num_total_slots = math.ceil(video_duration_sec / time_per_slot) + 1 if time_per_slot > 0 else len(image_order)
        looped_file_order = [image_order[i % len(image_order)] for i in range(num_total_slots)]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            image_paths = []
            for file in looped_file_order:
                unique_name = f"{uuid.uuid4().hex}_{file.name}"
                img_path = temp_dir_path / unique_name
                img_path.write_bytes(file.getbuffer())
                image_paths.append(img_path)

            audio_configs_for_generation = []
            for name, config in audio_configs.items():
                temp_audio_path = temp_dir_path / name
                temp_audio_path.write_bytes(config['file'].getbuffer())
                audio_configs_for_generation.append({
                    'path': str(temp_audio_path),
                    'start': config['start'],
                    'duration': config['duration']
                })

            run_id = str(uuid.uuid4())
            st.session_state.run_id = run_id
            video_output_path = output_dir / f"video_{run_id}.mp4"
            thumb_output_path = output_dir / f"thumb_{run_id}.png"
            
            success = generate_video(
                image_paths, audio_configs_for_generation, str(video_output_path),
                video_duration_sec, transition_duration_sec,
                TARGET_IMAGE_DURATION, progress_bar
            )

            if success:
                st.success("영상 생성 완료!")
                st.session_state.video_path = str(video_output_path)
                
                first_image_path = temp_dir_path / f"{uuid.uuid4().hex}_{image_order[0].name}"
                first_image_path.write_bytes(image_order[0].getbuffer())
                try:
                    ffmpeg_path = get_ffmpeg_path()
                    subprocess.run([
                        ffmpeg_path, '-y', '-i', str(first_image_path),
                        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black',
                        '-vframes', '1', str(thumb_output_path)
                    ], check=True, capture_output=True, text=True, encoding='utf-8')
                    st.session_state.thumbnail_path = str(thumb_output_path)
                except subprocess.CalledProcessError:
                    st.session_state.thumbnail_path = None
            else:
                st.session_state.video_path = None
                st.session_state.thumbnail_path = None

if st.session_state.video_path:
    st.header("4. 결과 확인 및 다운로드")
    video_file_path = Path(st.session_state.video_path)
    thumb_file_path = Path(st.session_state.thumbnail_path) if st.session_state.thumbnail_path else None
    if video_file_path.exists():
        if thumb_file_path and thumb_file_path.exists():
            st.image(str(thumb_file_path), caption="생성된 썸네일")
            with open(thumb_file_path, "rb") as f:
                st.download_button("썸네일 이미지 다운로드 🖼️", data=f.read(), file_name=f"thumbnail_{st.session_state.run_id}.png", mime="image/png")
        st.markdown("---")
        st.video(str(video_file_path))
        with open(video_file_path, "rb") as f:
            st.download_button("영상 다운로드 🎬", data=f.read(), file_name=f"video_{st.session_state.run_id}.mp4", mime="video/mp4")
    else:
        st.error("생성된 파일을 찾을 수 없습니다.")
        st.session_state.video_path = None
        st.session_state.thumbnail_path = None

st.sidebar.info("© 2025. Jack-Kim393. All Rights Reserved.")
st.sidebar.markdown("---")
st.sidebar.markdown("### FFmpeg 정보")
try:
    ffmpeg_path = get_ffmpeg_path()
    result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, check=True, encoding='utf-8')
    st.sidebar.code(result.stdout.splitlines()[0])
except (subprocess.CalledProcessError, FileNotFoundError):
    st.sidebar.error("FFmpeg를 찾을 수 없거나 실행할 수 없습니다. 시스템에 설치하고 PATH에 추가해주세요.")