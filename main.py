from random import randint

import librosa
from moviepy.editor import VideoFileClip, concatenate, AudioFileClip
from moviepy.video.fx import speedx
import psutil  # Add this line to import the psutil module


def apply_speed_ramp(video, audio, timestamps):
    slow_percentage = 0.4  # percentage of duration
    fast_percentage = 0.2  # percentage of duration
    slow_factor = 0.5
    middle_factor = 1
    fast_factor = 2
    video = VideoFileClip(video)
    audio = AudioFileClip(audio)
    clips = []
    audio_section_start = 0.0
    audio_section_end = 0.0
    slow_video_start = 0.0
    middle_video_start = 0.0
    fast_video_start = 0.0
    fast_video_end = 0.0
    i = 0
    for audio_timestamp in timestamps:
        audio_difference = audio_section_end - audio_section_start
        audio_section_start = audio_section_end
        audio_section_end = audio_timestamp
        slow_video_start = fast_video_end
        middle_video_start = slow_video_start + audio_difference * slow_percentage * slow_factor
        fast_video_start = middle_video_start + audio_difference * (
                    1 - slow_percentage - fast_percentage) * middle_factor
        if fast_video_start > video.duration:
            break
        fast_video_end = fast_video_start + audio_difference * fast_percentage * fast_factor
        if middle_video_start > video.duration:
            break
        slow_clip = video.subclip(slow_video_start, middle_video_start).speedx(factor=slow_factor)
        clips.append(slow_clip)
        if fast_video_start > video.duration:
            break
        middle_clip = video.subclip(middle_video_start, fast_video_start).speedx(factor=middle_factor)
        clips.append(middle_clip)
        if fast_video_end > video.duration:
            break
        fast_clip = video.subclip(fast_video_start, fast_video_end).speedx(factor=fast_factor)
        clips.append(fast_clip)
        i = i + 1
        print("speed ramp calculation: " + str(round(100 * i / len(audio_timestamps), ndigits=1)) + "%")

    final_clip = concatenate(clips)
    final_clip = final_clip.set_audio(audio.subclip(0, audio_section_end))  # Set the audio from the audio file
    final_clip.write_videofile("output_files/output" + str(randint(1, 10000)) + ".mp4",
                               codec="libx264",
                               audio_codec="aac",
                               threads=psutil.cpu_count(logical=True),
                               progress_bar=False,
                               logger=None,
                               ffmpeg_params=["-nostats", "-loglevel", "0"],
                               cleanup=lambda _: terminate_process(final_clip.reader.process))


def terminate_process(process):
    process.terminate()
    psutil.Process(process.pid).terminate()


def detect_beat(audio_file):
    y, sr = librosa.load(audio_file)

    # Extract beat events and tempo
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)

    # Convert beat frames to time (in seconds)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return beat_times


video_path = "input_files/input_video.mp4"  # Path to the input video file
# Load audio file
audio_path = 'input_files/input_audio.mp3'
audio_timestamps = detect_beat(audio_path)
apply_speed_ramp(video_path, audio_path, audio_timestamps)
