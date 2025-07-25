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
                # Transition duration changed from 0.8s to 0.5s
                final_clips.append(CompositeVideoClip([clips[i+1].set_start(0.5).crossfadein(0.5), clips[i].set_end(0.5)]).set_duration(1.5))


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