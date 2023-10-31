# This Python script is provided under the MIT License. Please refer to the LICENSE file
# or visit https://opensource.org/licenses/MIT for the full text of the license.

# Author: Adrian Szatmari
# Date: October 2023


from helpers import *


def main():
    # Get the directory containing the main script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the name of your video file
    video_filename = "SiliconValleyBigHeadFiredFromHooli.mp4"  # Replace with the actual filename

    # Construct the full path to the video file
    video_path = os.path.join(script_dir, video_filename)
    video_filename_burned = "SiliconValleyBigHeadFiredFromHooli_burned.mp4"
    video_path_burned = os.path.join(script_dir, video_filename_burned)

    burn_frame_info(video_path, video_path_burned)

    # The burning is done with opencv, which does not support audio, so we have to add back with ffmpeg
    audio_path = os.path.join(script_dir, "audio.m4a")
    extract_audio(video_path, audio_path)

    video_filename_burned_audio = "SiliconValleyBigHeadFiredFromHooli_burned_and_audio.mp4"
    video_path_burned_audio = os.path.join(script_dir, video_filename_burned_audio)
    merge_video_and_audio(video_path_burned, audio_path, video_path_burned_audio)

    # Testing
    vid_stats = get_video_stats(video_path_burned_audio, options='ffmpeg')
    frame_start = extract_frame(video_path_burned_audio, 0, "ffmpeg")
    frame_nb, seconds = get_frame_info_ocr(frame_start)
    assert frame_nb == 0
    assert seconds == 0.0

    # Frame numbering starts from 0, but vid_stats has the total number
    frame_end = extract_frame(video_path_burned_audio, vid_stats['frames'] - 1, "ffmpeg")
    frame_nb, seconds = get_frame_info_ocr(frame_end)
    assert frame_nb == vid_stats['frames'] - 1
    # The last frame also have duration, looks like this
    # |---|---|---
    # And not like this
    # |---|---|---|
    assert abs(seconds - (vid_stats['duration_seconds'] - vid_stats['time_between_frames'])) < 0.001


if __name__ == "__main__":
    main()
