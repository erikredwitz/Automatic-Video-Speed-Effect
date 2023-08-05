from random import randint
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import moviepy.video.fx
from moviepy.video.fx.accel_decel import accel_decel
from moviepy.video.io.VideoFileClip import VideoFileClip

root = Tk()

# Hide the main window
root.withdraw()

# Open the file chooser dialog
video_path = askopenfilename(title="input video")
clip = VideoFileClip(video_path)
effect_clip = accel_decel(clip, new_duration=clip.duration, abruptness=-0.5, soonness=1)
effect_clip.write_videofile("output_files/output" + str(randint(1, 10000000)) + ".mp4",
                               codec="libx264",
                               audio_codec="aac")
