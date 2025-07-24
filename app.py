import os
import streamlit as st
from moviepy.editor import *
from PIL import Image
import numpy as np
from pathlib import Path

# Define paths
base_dir = "/Users/kakaoent/Desktop/my-mac-project/shortform-generation-image"
img_dir = os.path.join(base_dir, "img")
mp3_dir = os.path.join(base_dir, "mp3")
output_dir = os.path.join(base_dir, "output")
thumbnail_dir = os.path.join(base_dir, "thumbnail")

# Create directories if they don't exist
os.makedirs(img_dir, exist_ok=True)
os.makedirs(mp3_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(thumbnail_dir, exist_ok=True)

def resize_and_pad(img_path, output_size=(1080, 1920)):
    img = Image.open(img_path)
    img.thumbnail(output_size, Image.Resampling.LANCZOS)
    
    new_img = Image.new("RGB", output_size, (0, 0, 0))
    new_img.paste(img, ((output_size[0] - img.size[0]) // 2, (output_size[1] - img.size[1]) // 2))
    
    return np.array(new_img)

st.title("Short-form Video Generator")

if st.button("Generate Video"):
    # --- Validation Checks ---
    img_files = sorted([f for f in os.listdir(img_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
    mp3_files = [f for f in os.listdir(mp3_dir) if f.endswith('.mp3')]

    if not img_files:
        st.error("Error: The 'img' folder is empty. Please add images.")
    elif len(img_files) < 2:
        st.error("Error: At least 2 images are required in the 'img' folder.")
    elif not mp3_files:
        st.error("Error: The 'mp3' folder is empty. Please add an MP3 file.")
    else:
        mp3_path = os.path.join(mp3_dir, mp3_files[0])
        audio_clip = AudioFileClip(mp3_path)
        if audio_clip.duration < 55:
            st.error("Error: The MP3 file must be at least 55 seconds long.")
        else:
            st.success("Validation passed! Starting video generation...")

            # --- Thumbnail Generation ---
            thumbnail_path = os.path.join(thumbnail_dir, "thumbnail.png")
            first_img_path = os.path.join(img_dir, img_files[0])
            thumbnail_img = Image.open(first_img_path)
            thumbnail_img.thumbnail((1080, 1920), Image.Resampling.LANCZOS)
            thumbnail_img.save(thumbnail_path)
            st.image(thumbnail_path, caption="Generated Thumbnail")


            # --- Video Composition ---
            clips = []
            image_paths = [os.path.join(img_dir, img) for img in img_files]
            
            # Repeat images if less than 10
            while len(image_paths) < 10:
                image_paths.extend(image_paths)
            image_paths = image_paths[:10]


            for img_path in image_paths:
                processed_img = resize_and_pad(img_path)
                clips.append(ImageClip(processed_img).set_duration(1.5))

            # --- Transitions ---
            final_clips = [clips[0]]
            for i in range(len(clips) - 1):
                final_clips.append(CompositeVideoClip([clips[i+1].set_start(0.8).crossfadein(0.8), clips[i].set_end(0.8)]).set_duration(1.5))


            video = concatenate_videoclips(final_clips, method="compose")
            
            # --- Audio ---
            final_audio = audio_clip.subclip(40, 55)
            video = video.set_audio(final_audio)

            # --- Export Video ---
            output_filename = "shortform_video.mp4"
            output_path = os.path.join(output_dir, output_filename)
            video.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, fps=24)

            st.success(f"Video generated successfully! Saved to: {output_path}")
            st.video(output_path)