import os
import base64
import cv2
import json 
from flask import current_app
from os.path import isfile, join, dirname

from moviepy.editor import VideoFileClip
from src.core.agents.main_client import client
from src.db.main_model import *
from src.util_helpers.pdf_utils import process_pdf


def process_text_file(text_path):
    with open(text_path, 'r') as file:
        text = file.read()
    return text

def process_video(video_path, seconds_per_frame=2):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)
    
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()

    # Extract audio if available
    audio_path = None
    try:
        clip = VideoFileClip(video_path)
        if clip.audio:
            audio_path = f"{base_video_path}.mp3"
            clip.audio.write_audiofile(audio_path, bitrate="32k")
            clip.audio.close()
        clip.close()
    except Exception as e:
        print(f"Failed to extract audio: {e}")

    return base64Frames, audio_path

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def transcribe_audio(audio_path,model="gpt-4o"):
    transcription_text = ""
    if audio_path:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio_path, "rb"),
        )
        transcription_text = transcription.text
    return transcription_text

def save_text_to_file(text, directory, filename):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    return file_path

def save_processed_file_to_db(file_path, public_id, case_id=None):
    filename = os.path.basename(file_path)
    file_post = FilePost(fileName=filename, user_id=public_id, case_id=case_id)  # Ensure case_id is used here
    db.session.add(file_post)
    db.session.commit()


###File handler####
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def file_handler(file_path, file_type, public_id, file_name, case_id):
    base_dir = current_app.config['STATIC_FOLDER']
    upload_dir = os.path.join(base_dir, 'uploads', public_id)
    summary_dir = os.path.join(base_dir, 'uploads', 'summary', public_id)

    ensure_directory_exists(upload_dir)
    ensure_directory_exists(summary_dir)

    print(f"Checking if upload directory {upload_dir} exists...")
    file_type = file_type.lower()
    text = ""  # Initialize text to ensure it's available for all file types

    print(f"Processing file: {file_path} of type: {file_type}")
    if file_type in ['.mp4', '.avi', '.webm', '.mov']:
        print("Processing video file...")
        frames, audio_path = process_video(file_path)
        video_summary = generate_video_summary(frames)
        text = video_summary  # Assume generate_video_summary returns text
        print(f"Video summary generated. Length of text: {len(text)} characters")

        if audio_path:
            print("Transcribing audio...")
            aud_text = transcribe_audio(audio_path)
            text += '\n\n' + aud_text  # Append transcription text to the video summary
            transcription_file_path = save_text_to_file(aud_text, summary_dir, os.path.splitext(file_name)[0] + "_audio_summary.txt")
            save_processed_file_to_db(transcription_file_path, public_id, case_id)
            print(f"Audio transcription saved to {transcription_file_path}")

        summary_file_path = save_text_to_file(text, summary_dir, os.path.splitext(file_name)[0] + "_video_summary.txt")
        save_processed_file_to_db(summary_file_path, public_id, case_id)
        print(f"Video summary saved to {summary_file_path}")

    elif file_type in ['.mp3', '.wav']:
        print("Processing audio file...")
        text = transcribe_audio(file_path)
        transcription_file_path = save_text_to_file(text, summary_dir, os.path.splitext(file_name)[0] + "_audio_summary.txt")
        save_processed_file_to_db(transcription_file_path, public_id, case_id)
        print(f"Audio transcription saved to {transcription_file_path}")

    elif file_type in ['.jpg', '.png']:
        print("Processing image file...")
        base64_image = encode_image(file_path)
        text = generate_image_summary(base64_image)
        image_summary_file_path = save_text_to_file(text, summary_dir, file_name + "_image_summary.txt")
        save_processed_file_to_db(image_summary_file_path, public_id, case_id)
        print(f"Image summary saved to {image_summary_file_path}")

    elif file_type in ['.txt']:
        print(f"Processing text file of type: {file_type}")
        text = process_text_file(file_path)
        processed_file_path = save_text_to_file(text, summary_dir, file_name + "_txt_summary.txt")
        save_processed_file_to_db(processed_file_path, public_id, case_id)
        print(f"Text file processed and saved to {processed_file_path}")

    elif file_type in ['.pdf']:
        text = process_pdf(public_id, file_name)
        return text

    return text
  
#####Openai calls###
    





def generate_video_summary(base64Frames, model="gpt-4o"):

    # Prepare the frames as messages for the OpenAI API
    frame_messages = [{"type": "image_url", "image_url": f'data:image/jpg;base64,{frame}'} for frame in base64Frames]

    response = client.chat.completions.create(
            model=model,
            messages=[
            {"role": "system", "content": "You are generating a video summary. Please provide a summary of the video. Respond in Markdown."},
            {"role": "user", "content": [
                "These are the frames from the video.",
                *map(lambda x: {"type": "image_url", 
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
                ],
            }
            ],
            temperature=0,
        )
    
    # print(f"Response : {response}\n")
    # answer = answer_dict['choices'][0]['message']['content']
    answer_json_string=(response.model_dump_json(indent=2))
    answer_dict = json.loads(answer_json_string)
    answer = answer_dict['choices'][0]['message']['content']
    print(f"Response message: {answer}\n")

    return answer

def generate_image_summary(base64Image, model="gpt-4o"):
    # Prepare the frame as a message for the OpenAI API
    image_message = {"type": "image_url", "image_url": f'data:image/jpg;base64,{base64Image}'}

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are generating a summary for the provided image. Please provide a summary of the image content. Respond in Markdown."},
            {"role": "user", "content": image_message}
        ],
        temperature=0,
    )

    # Extracting the response and printing for debugging
    answer_json_string = response.model_dump_json(indent=2)
    answer_dict = json.loads(answer_json_string)
    answer = answer_dict['choices'][0]['message']['content']
    print(f"Response message: {answer}\n")

    return answer
