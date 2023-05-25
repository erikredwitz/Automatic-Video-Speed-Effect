import subprocess
import librosa


def detect_bass_sounds(audio_file):
    # Load the audio file
    audio, sr = librosa.load(audio_file)

    # Compute the spectral centroid
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]

    # Apply bass detection
    timestamps = []
    threshold = 0.2  # Adjust the threshold as per your requirements

    for i in range(len(spectral_centroid)):
        if spectral_centroid[i] > threshold:
            timestamps.append(i)

    return timestamps


def apply_speed_ramps(video, audio, output, timestamps):
    segment_duration = int(len(timestamps) / len(video))

    # Iterate through video segments and apply speed ramp effects
    for i, segment_start in enumerate(timestamps):
        start_time = segment_start / len(video)
        duration = segment_duration / len(video)
        speed_ramp_command = f"ffmpeg -y -i {video} -i {audio} -ss {start_time} -t {duration} -vf " \
                             f"\"setpts='if(lt(T,{start_time}+{duration}*(1-0.75)),0.5*PTS,2.0*PTS)'\" -a" \
                             f"f atrim={start_time}:{start_time + duration},asetpts=PTS-STARTPTS -c:v libx264 -c:a " \
                             f"aac -strict experimental -b:a 192k -shortest segment_{i}.mp4"

        subprocess.call(speed_ramp_command, shell=True)

    # Concatenate the segmented videos
    concat_command = f"ffmpeg -y -f concat -safe 0 -i <(for f in segment_*.mp4; do echo \"file '$PWD/$f'\"; done) -c " \
                     f"copy {output}"
    subprocess.call(concat_command, shell=True)

    # Remove the temporary segment files
    cleanup_command = "rm segment_*.mp4"
    subprocess.call(cleanup_command, shell=True)


if __name__ == '__main__':
    # Prompt for input file paths
    input_video = input("Enter the path for the input video: ")
    input_audio = input("Enter the path for the input audio: ")

    # Specify the output file path
    output_video = 'output_video.mp4'

    # Detect bass sounds in the audio file
    bass_timestamps = detect_bass_sounds(input_audio)

    # Apply speed ramps to the video based on bass timestamps
    apply_speed_ramps(input_video, input_audio, output_video, bass_timestamps)

    print("Speed ramps applied. Output video generated.")
