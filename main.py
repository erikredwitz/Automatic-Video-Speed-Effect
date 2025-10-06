from random import randint

import librosa
# moviepy-1.0.3 necessary for this - not later version
from moviepy.editor import VideoFileClip, concatenate, AudioFileClip
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import json


def apply_speed_ramp(video, audio, timestamps):
    # Open the JSON file
    with open('config.json', 'r') as file:
        # Load the JSON data
        data = json.load(file)
    # Set the variables from the JSON data
    speed_duration = data["speed_duration"]
    slow_factor = data["slow_factor"]
    fast_factor = data["fast_factor"]
    audio_offset = data["audio_offset"]
    video_offset = data["video_offset"]
    video = VideoFileClip(video)
    audio = AudioFileClip(audio)
    clips = []
    print("video: " + str(video.fps) + " fps, audio: " + str(audio.fps) + " fps")
    audio_section_start = 0.0
    audio_section_end = 0.0
    slow_video_start = 0.0
    fast_video_start = 0.0
    fast_video_end = 0.0
    is_video_end_reached = False
    i = 0
    for audio_timestamp in timestamps:
        audio_section_end = audio_timestamp
        audio_section_length = audio_section_end - audio_section_start
        if fast_video_end != 0:
            slow_video_start = fast_video_end + video_offset
        else:
            slow_video_start = 0
        fast_video_start = slow_video_start + audio_section_length - speed_duration
        if fast_video_start > video.duration:
            fast_video_start = video.duration
            is_video_end_reached = True
        slow_clip = video.subclip(slow_video_start, fast_video_start).speedx(factor=slow_factor)
        clips.append(slow_clip)
        if is_video_end_reached:
            break
        fast_video_end = slow_video_start + audio_section_length
        if fast_video_end > video.duration:
            fast_video_end = video.duration
            is_video_end_reached = True
        fast_clip = video.subclip(fast_video_start, fast_video_end).speedx(factor=fast_factor)
        clips.append(fast_clip)
        if is_video_end_reached:
            break
        i = i + 1
        if i % 10 == 0:
            print("audio: " + str(round(100 * i / len(audio_timestamps), ndigits=1)) + "%, video: " + str(
                round(100 * fast_video_end / video.duration, ndigits=1)) + " %")
        audio_section_start = audio_section_end

    final_clip = concatenate(clips)
    if audio_offset != 0:
        final_clip = final_clip.subclip(t_start=audio_offset)
    else:
        final_clip = final_clip.set_audio(audio)  # Set the audio from the audio file
    final_clip.write_videofile("output_files/output" + str(randint(1, 10000000)) + ".mp4",
                               codec="libx264",
                               audio_codec="aac")


def detect_beat(audio_file):
    y, sr = librosa.load(audio_file)

    # Extract beat events and tempo
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
    # Convert beat frames to time (in seconds)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return beat_times


# Create the Tkinter root window
root = Tk()

# Hide the main window
root.withdraw()

# Open the file chooser dialog
video_path = askopenfilename(title="input video")
# Load audio file
audio_path = askopenfilename(title="input audio")
audio_timestamps = detect_beat(audio_path)
apply_speed_ramp(video_path, audio_path, audio_timestamps)
