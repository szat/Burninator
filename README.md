# Read-Write-Video-Frame-Nb
Some video processing tools, more to be added. Let me know in the issues section what could be useful. 
Here you can take an initial video and burn the frame number and timestamp on it. Then you can retrieve the frame number and the timestamp with a function call on that frame. 
Like this:

```
    # Define the name of your video file
    video_filename = "SiliconValleyBigHeadFiredFromHooli.mp4"  # Replace with the actual filename
    video_filename_burned = "SiliconValleyBigHeadFiredFromHooli_burned.mp4"

    # Burn the video info onto the frames
    burn_frame_info(video_filename, video_filename_burned)
    # Not necessary to convert to h264, but opencv will not do it automatically cause of license. 
    convert_to_h264(video_path_burned)

    # Get the video info from the burnt frames
    frame_request = 50
    frame = extract_frame(video_path_burned, frame_request)
    frame_nb, seconds = get_frame_info_ocr(frame_start)

    assert frame_nb == frame_request
```

Here is an example of the original video:

https://github.com/szat/Read-Write-Video-Frame-Nb/assets/5555551/c577ce0c-b12d-4413-903f-e97b6af66afd

And here an example of the burnt video:

https://github.com/szat/Read-Write-Video-Frame-Nb/assets/5555551/98e29ddb-6ed9-4adb-8e54-90683b7170c3



Let me know of any bugs or of cool functionality that could be implemnted in the issues section. Share if you find this useful for your work or research. 
