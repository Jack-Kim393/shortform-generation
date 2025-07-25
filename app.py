import os
import streamlit as st
from moviepy.editor import *
from PIL import Image
import numpy as np
from pathlib import Path
import tempfile
import shutil

# Define paths
base_dir = "/Users/kakaoent/Desktop/my-mac-project/shortform-generation-image"
output_dir = os.path.join(base_dir, "output")
thumbnail_dir = os.path.join(base_dir, "thumbnail")

# Create directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(thumbnail_dir, exist_ok=True)

def resize_and_pad(img_path, output_size=(1080, 1920)):
    """
    Resizes an image to fit within the output size while maintaining aspect ratio,
    padding the remaining space with a black background. This is a "fit" or "contain" operation.
    It calculates the scale required for both dimensions and uses the smaller scale
    to ensure the whole image fits without cropping.
    """
    target_w, target_h = output_size

    try:
        img = Image.open(img_path).convert("RGB")
    except Exception as e:
        print(f"Error opening image {img_path}: {e}")
        return np.zeros((target_h, target_w, 3), dtype=np.uint8)

    img_w, img_h = img.size
    if img_w == 0 or img_h == 0:
        return np.zeros((target_h, target_w, 3), dtype=np.uint8)

    # Calculate scaling factors for width and height
    scale_w = target_w / img_w
    scale_h = target_h / img_h

    # Choose the smaller scaling factor to ensure the image fits without cropping
    scale = min(scale_w, scale_h)

    # Calculate the new dimensions
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    # Resize the image using the calculated dimensions
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Create a new image with a black background
    background = Image.new("RGB", output_size, (0, 0, 0))

    # Calculate position to paste the resized image onto the center of the background
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2

    # Paste the resized image
    background.paste(img_resized, (paste_x, paste_y))

    return np.array(background)

st.title("Short-form Video Generator")

# File Uploaders
uploaded_images = st.file_uploader(
    "Upload Images (PNG, JPG, JPEG) - At least 2 images required", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)
uploaded_mp3 = st.file_uploader(
    "Upload MP3 File - At least 55 seconds long", 
    type=["mp3"]
)

# Video Settings
st.subheader("Video Settings")

video_duration_sec = st.slider(
    "Total Video Duration (seconds)",
    min_value=10,
    max_value=20,
    value=15,
    step=1
)

transition_duration_ms = st.selectbox(
    "Select Transition Duration (Ease in and out)",
    options=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    index=4, # Default to 500ms
    format_func=lambda x: f"{x}ms"
)
transition_duration_sec = transition_duration_ms / 1000.0

mp3_start_time = st.number_input(
    "MP3 Extraction Start Time (seconds)",
    min_value=0,
    value=40,
    step=1
)

# MP3 Preview Button
if uploaded_mp3 and st.button("Preview MP3 Segment"):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_mp3_path = os.path.join(temp_dir, uploaded_mp3.name)
        with open(temp_mp3_path, "wb") as f:
            f.write(uploaded_mp3.getbuffer())

        try:
            audio_clip = AudioFileClip(temp_mp3_path)
            if mp3_start_time + video_duration_sec > audio_clip.duration:
                st.warning(f"MP3 segment ({video_duration_sec}s from {mp3_start_time}s) exceeds audio duration ({audio_clip.duration:.2f}s). Playing available portion.")
                preview_end_time = audio_clip.duration
            else:
                preview_end_time = mp3_start_time + video_duration_sec

            preview_clip = audio_clip.subclip(mp3_start_time, preview_end_time)
            
            temp_preview_path = os.path.join(temp_dir, "preview_audio.mp3")
            preview_clip.write_audiofile(temp_preview_path, verbose=False, logger=None)
            
            st.audio(temp_preview_path, format='audio/mp3')

        except Exception as e:
            st.error(f"Error during MP3 preview: {e}")

def generate_video_process(uploaded_images, uploaded_mp3, transition_duration_sec, mp3_start_time, video_duration_sec):
    # --- Validation Checks ---
    if not uploaded_images:
        st.error("Error: Please upload at least 2 images.")
        return
    elif len(uploaded_images) < 2:
        st.error("Error: At least 2 images are required.")
        return
    elif not uploaded_mp3:
        st.error("Error: Please upload an MP3 file.")
        return
    else:
        # Create a temporary directory for uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []
            for uploaded_file in uploaded_images:
                # Save uploaded image to a temporary file
                temp_image_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                image_paths.append(temp_image_path)
            
            # Save uploaded MP3 to a temporary file
            temp_mp3_path = os.path.join(temp_dir, uploaded_mp3.name)
            with open(temp_mp3_path, "wb") as f:
                f.write(uploaded_mp3.getbuffer())

            try:
                audio_clip = AudioFileClip(temp_mp3_path)
                
                # Validate MP3 duration and start time
                if audio_clip.duration < video_duration_sec:
                    st.error(f"Error: The MP3 file must be at least {video_duration_sec} seconds long to match video duration.")
                    return # Stop execution
                
                if mp3_start_time + video_duration_sec > audio_clip.duration:
                    st.error(f"Error: MP3 segment ({video_duration_sec}s from {mp3_start_time}s) exceeds audio duration ({audio_clip.duration:.2f}s). Please adjust start time.")
                    return # Stop execution

                st.success("Validation passed! Starting video generation...")

                # --- Thumbnail Generation ---
                thumbnail_path = os.path.join(thumbnail_dir, "thumbnail.png")
                first_img_path = image_paths[0]
                
                try:
                    # Use the same padding logic for the thumbnail
                    thumb_np_array = resize_and_pad(first_img_path, output_size=(1080, 1920))
                    thumbnail_img = Image.fromarray(thumb_np_array)
                    thumbnail_img.save(thumbnail_path)
                    st.image(thumbnail_path, caption="Generated Thumbnail")
                except Exception as e:
                    st.error(f"Error generating thumbnail: {e}")


                # --- Video Composition ---
                clips = []
                
                # Repeat images if less than 10
                while len(image_paths) < 10:
                    image_paths.extend(image_paths)
                image_paths = image_paths[:10]

                # Calculate individual image clip duration based on total video duration
                image_clip_duration = video_duration_sec / len(image_paths)

                for img_path in image_paths:
                    processed_img = resize_and_pad(img_path)
                    clips.append(ImageClip(processed_img).set_duration(image_clip_duration))

                # --- Transitions ---
                final_clips = [clips[0]]
                for i in range(len(clips) - 1):
                    # Use selected transition duration
                    final_clips.append(CompositeVideoClip([
                        clips[i+1].set_start(transition_duration_sec).crossfadein(transition_duration_sec),
                        clips[i].set_end(transition_duration_sec)
                    ]).set_duration(image_clip_duration))


                video = concatenate_videoclips(final_clips, method="compose")
                
                # --- Audio ---
                final_audio = audio_clip.subclip(mp3_start_time, mp3_start_time + video_duration_sec)
                video = video.set_audio(final_audio)

                # --- Export Video ---
                output_filename = "shortform_video.mp4"
                output_path = os.path.join(output_dir, output_filename)
                video.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, fps=24)

                st.success(f"Video generated successfully! Saved to: {output_path}")
                st.video(output_path)

                # --- Download Button ---
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="Download Video",
                        data=file,
                        file_name=output_filename,
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"An error occurred during video generation: {e}")

        # Temporary directory and its contents are automatically cleaned up here


if st.button("Generate Video"):
    generate_video_process(uploaded_images, uploaded_mp3, transition_duration_sec, mp3_start_time, video_duration_sec)
