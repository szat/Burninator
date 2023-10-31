# This Python script is provided under the MIT License. Please refer to the LICENSE file
# or visit https://opensource.org/licenses/MIT for the full text of the license.

# Author: Adrian Szatmari
# Date: October 2023


import numpy as np
import os
import cv2
import json
import subprocess


def get_frames_info(video_file, option="all"):
    try:
        if option == 'all':
            ffprobe_command = [
                'ffprobe',
                '-loglevel', 'error',
                '-select_streams', 'v:0',
                '-show_entries',
                'frame=pict_type,pkt_pts_time,pkt_dts_time,pkt_duration_time,pkt_pos_time,key_frame,best_effort_timestamp_time',
                '-of', 'json',
                video_file
            ]
        if option == 'keys':
            ffprobe_command = [
                'ffprobe',
                '-loglevel', 'error',
                '-select_streams', 'v:0',
                '-show_entries',
                'frame=key_frame',
                '-of', 'json',
                video_file
            ]
        # Execute the ffprobe command and capture its output as a byte string
        output = subprocess.check_output(ffprobe_command)

        # Decode the byte string into a JSON object
        frame_info = json.loads(output)

        return frame_info
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e}")
        return None


def convert_numbers_to_letters(input_string):
    # Define a dictionary to map numbers to letters
    number_to_letter = {
        '0': 'A',
        '1': 'B',
        '2': 'C',
        '3': 'D',
        '4': 'G',
        '5': 'H',
        '6': 'K',
        '7': 'M',
        '8': 'P',
        '9': 'Y'
    }

    # Initialize an empty result string
    result = ''

    # Iterate through each character in the input string
    for char in input_string:
        # If the character is in the dictionary, append the corresponding letter
        if char in number_to_letter:
            result += number_to_letter[char]
        else:
            # If the character is not in the dictionary, keep it unchanged
            result += char

    return result


def convert_letters_to_numbers(input_string):
    # Define a dictionary to map letters to numbers
    letter_to_number = {
        'A': '0',
        'B': '1',
        'C': '2',
        'D': '3',
        'G': '4',
        'H': '5',
        'K': '6',
        'M': '7',
        'P': '8',
        'Y': '9'
    }

    # Initialize an empty result string
    result = ''

    # Iterate through each character in the input string
    for char in input_string:
        # If the character is in the dictionary, append the corresponding number
        if char in letter_to_number:
            result += letter_to_number[char]
        else:
            # If the character is not in the dictionary, keep it unchanged
            result += char

    return result


def get_frame_info_ocr(image, target_color=(255, 0, 255), option="letters"):
    # Create a mask that identifies pixels close to the target color
    lower_bound = np.array(target_color) - np.array([15, 15, 15])
    upper_bound = np.array(target_color) + np.array([15, 15, 15])
    mask = cv2.inRange(image, lower_bound, upper_bound)
    tmp = mask > 0.5
    tmp2 = np.ones_like(mask) * 255
    tmp2[tmp] = 0
    kernel = np.ones((3, 3), np.uint8)

    # Dilate the image
    # tmp2 = cv2.dilate(tmp2, kernel, iterations=1)
    # tmp3 = np.ones_like(mask)*255
    # tmp3[tmp2 == 255] = 0
    tmp3 = cv2.erode(tmp2, kernel, iterations=1)

    import pytesseract
    import re
    text = pytesseract.image_to_string(tmp3)

    punctuation_chars = ".,"

    # Extract uppercase characters, newline characters, and punctuation characters
    text = [char for char in text if char.isupper() or char == '\n' or char in punctuation_chars]
    text = ''.join(text)

    info_list = text.splitlines()
    info_list = info_list[:3]

    # Use regular expression to find all capital letters
    if option == "letters":
        capital_letters = re.findall(r'[A-Z\.]+', info_list[0])
        digits = convert_letters_to_numbers(capital_letters[0])
        frame_nb = int(digits)

        capital_letters = re.findall(r'[A-Z\.]+', info_list[1])
        digits = convert_letters_to_numbers(capital_letters[0])
        time_seconds = float(digits)
    else:
        digits = re.findall(r'\d', info_list[0])
        digits = digits[0]
        # matches = matches.replace(" ", "")
        # Convert the remaining string to an integer
        frame_nb = int(digits)

        # pattern = r'\[(.*?)\]'
        # time_seconds = re.findall(pattern, info_list[1])
        time_seconds = re.findall(r'\d+\.\d+', info_list[1])
        time_seconds = time_seconds[0]
        # matches = matches.replace(" ", "")
        # Convert the remaining string to an integer
        time_seconds = float(time_seconds)
    return frame_nb, time_seconds


def extract_frame(video_path, frame_number, option="opencv"):
    # Open the video file
    if option == "opencv":
        import cv2
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return None  # Unable to open the video file

        # Set the frame position to the desired frame_number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame
        ret, frame = cap.read()

        # Release the video capture object
        cap.release()

        if not ret:
            return None  # Unable to read the frame

        return frame
    if option == "ffmpeg":
        import subprocess
        import io
        import cv2
        import numpy as np

        # Replace 'your_video_file.mp4' with the path to your video file
        video_file = video_path

        # Define the FFmpeg command to extract the n-th frame as an image, starts at 0
        ffmpeg_command = f"ffmpeg -i {video_file} -vf 'select=eq(n\\,{frame_number})' -vframes 1 -f image2pipe -"

        # Run the FFmpeg command
        result = subprocess.run(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if FFmpeg command was successful
        if result.returncode == 0:
            # Get the binary image data from the stdout
            frame_data = result.stdout

            # Create an in-memory buffer for the frame data
            frame_buffer = io.BytesIO(frame_data)

            # Read the frame from the buffer using OpenCV
            frame = cv2.imdecode(np.frombuffer(frame_buffer.read(), np.uint8), cv2.IMREAD_COLOR)
        return frame


def burn_frame_info(input_path, output_path):
    # Open the input video file
    input_video = cv2.VideoCapture(input_path)

    # Check if the video file exists
    if not os.path.exists(input_path):
        print(f"Not finding input video file {input_path}")
        return

    if os.path.exists(output_path):
        print(f"Burnt video file {output_path} already exists")
        return

    # Check if the video file was opened successfully
    if not input_video.isOpened():
        print("Error: Could not open input video file")
        return

    # Get the frame rate of the input video
    frame_rate = float(input_video.get(cv2.CAP_PROP_FPS))

    # Get the width and height of the video frames
    frame_width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create a video writer object to save the modified video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec as needed
    output_video = cv2.VideoWriter(output_path, fourcc, frame_rate, (frame_width, frame_height))

    # Initialize frame number and time counters
    frame_number = 0
    start_time = 0

    while True:
        ret, frame = input_video.read()
        if not ret:
            break

        # Calculate the time in seconds since the start of the video
        time_in_seconds = start_time + frame_number / frame_rate

        # Convert the time to a formatted string (h:min:ss)
        time_str1 = f"frame = {convert_numbers_to_letters(str(frame_number))}"
        time_in_seconds = "{:.4f}".format(time_in_seconds)
        time_str2 = f"time = {convert_numbers_to_letters(time_in_seconds)}"
        cv2.putText(frame, time_str1, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(255, 0, 255),
                    thickness=3)
        cv2.putText(frame, time_str2, (10, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(255, 0, 255),
                    thickness=3)

        time_str1 = f"frame = {frame_number}"
        time_str2 = f"time = {time_in_seconds}"

        # Draw the frame number and time on the frame
        cv2.putText(frame, time_str1, (10, 300), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=3)
        cv2.putText(frame, time_str2, (10, 340), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=3)

        # Write the modified frame to the output video
        output_video.write(frame)

        frame_number += 1

    # Release the video capture and writer objects
    input_video.release()
    output_video.release()


def get_video_stats(input_video, options="opencv"):
    # Replace 'your_video_file.mp4' with the path to your video file
    video_file = input_video

    if options == "opencv":
        # Open the video file for reading
        cap = cv2.VideoCapture(video_file)

        # Check if the video file was successfully opened
        if not cap.isOpened():
            print("Error: Could not open video file.")
        else:
            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            duration_seconds = frame_count / fps

            # Calculate time between frames
            if fps > 0:
                time_between_frames = 1 / fps
            else:
                time_between_frames = 0

            # Create a dictionary to store the video information
            video_info = {
                'length': frame_count,
                'frames': frame_count,
                'duration_seconds': duration_seconds,
                'fps': fps,
                'time_between_frames': time_between_frames
            }

            # Print the video information
            print("Video Information OpenCV:")
            for key, value in video_info.items():
                print(f"{key}: {value}")

            # Release the video capture object
            cap.release()
            return video_info
    elif options == "ffmpeg":
        import json
        ffprobe_command = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,duration,nb_frames,codec_name -of json {video_file}"
        result = subprocess.run(ffprobe_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if ffprobe command was successful
        if result.returncode == 0:
            # Parse the JSON output from ffprobe
            json_data = json.loads(result.stdout)

            # Extract video information from the JSON data
            video_info = {
                'length': int(json_data['streams'][0]['nb_frames']),
                'frames': int(json_data['streams'][0]['nb_frames']),
                'duration_seconds': float(json_data['streams'][0]['duration']),
                'fps': eval(json_data['streams'][0]['r_frame_rate']),
                'codec': json_data['streams'][0]['codec_name'],
                'time_between_frames': 1 / eval(json_data['streams'][0]['r_frame_rate'])
            }

            # Print the video information
            print("Video Information Ffmpeg:")
            for key, value in video_info.items():
                print(f"{key}: {value}")
        else:
            print("Error: ffprobe command failed.")
        return video_info


def merge_video_and_audio(video_path, audio_path, output_path):
    if not os.path.exists(video_path):
        print(f"Not finding the input video file {video_path}")
        return
    if not os.path.exists(audio_path):
        print(f"Not finding the input audio file {audio_path}")
        return
    if os.path.exists(output_path):
        print(f"The output video already exists {output_path}")
        return

    # ffmpeg command to merge video and audio
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-map', '0:v',
        '-map', '1:a',
        '-c:v', 'copy',
        '-shortest',
        output_path
    ]

    try:
        # Run the ffmpeg command
        subprocess.run(cmd, check=True)
        print(f'Merged video and audio saved to: {output_path}')
    except subprocess.CalledProcessError as e:
        print(f'Error merging video and audio: {e}')


def extract_audio(original_video_path, audio_output_path):
    """
    Extracts audio from a video file and saves it to the specified output path.
    """
    if not os.path.exists(original_video_path):
        print(f"Not finding input video path {original_video_path}")
        return

    if os.path.exists(audio_output_path):
        print(f"Audio {audio_output_path} already exists.")
        return

    try:
        # Run ffmpeg command to extract audio
        command = ['ffmpeg', '-i', original_video_path, '-map', '0:a', '-acodec', 'copy', audio_output_path]
        subprocess.run(command, check=True)
        print(f"Audio extracted and saved to {audio_output_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
