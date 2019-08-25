"""Optimize images and videos on folders and subfolders

This is a simple script that can optimize images and videos (reduce size) for
whatever reason you'd like to do so.

I used pillow and ffmpeg, so you have to install both.
For ffmpeg, you'll have to change the ffmpeg path according to your system 
platform in the "ffmpeg_command" function.
"""

import os
import sys
from PIL import Image


def ffmpeg_command(input_video, output_video='', video_crf=23):
    """Creates the ffmpeg command

    Args:
        input_video (str): The input video path.
        output_video (str): The output video path.
        video_crf (int): 0 to 51 (0 lossless, 51 worst quality possible)

    Returns:
        list: The full command line as a list
    """

    if not os.path.isfile(input_video):
        raise FileExistsError(f'File "{input_video}" does not exist')

    # Platform specific ffmpeg path
    if sys.platform.startswith('freebsd'):
        # FreeBSD (not really sure)
        ffmpeg_path = 'ffmpeg'
    elif sys.platform.startswith('linux'):
        # Linux (ffmpeg has to be installed)
        ffmpeg_path = 'ffmpeg'
    elif sys.platform.startswith('win32'):
        # Windows (change this to the ffmpeg correct path)
        ffmpeg_path = ''
    elif sys.platform.startswith('cygwin'):
        # Windows (change this to the ffmpeg correct path)
        ffmpeg_path = ''
    elif sys.platform.startswith('darwin'):
        # Mac (change this to the ffmpeg correct path)
        ffmpeg_path = 'ffmpeg'

    # Starts creating the final command
    final_command = [ffmpeg_path, '-i', f'"{input_video}"']

    # Video codec
    final_command.extend(['-c:v', 'libx264'])
    # Preset
    final_command.extend(['-preset:v', 'ultrafast'])
    # CRF
    final_command.extend(['-crf', str(video_crf)])
    # Audio codec
    final_command.extend(['-c:a', 'aac'])
    # Audio bitrate
    final_command.extend(['-b:a', '320k'])
    # Threads
    final_command.extend(['-threads', '0'])
    # Flags
    final_command.extend(['-movflags', '+faststart'])
    # From - to (For testing purposes)
    # final_command.extend(['-ss', '00:00:00.00', '-to', '00:00:30.00'])

    # Output
    final_command.extend([f'"{output_video}"'])
    return final_command


def ffmpeg_convert(original_file_path, new_file_path, delete_original=False,
                   video_crf=23):
    """Execute ffmpeg command

    Args:
        original_file_path (str): Original video full path
        new_file_path (str): New video full path
        delete_original (bool): Set to True will move original files to trash
        video_crf (int): 0 to 51 (0 lossless, 51 worst quality possible)
    """
    # FFMPEG command
    command = ffmpeg_command(
        input_video=original_file_path,
        output_video=new_file_path,
        video_crf=video_crf
    )
    command = ' '.join(command)

    print(command)
    os.system(command)

    # Move original file to trash
    if delete_original:
        send_file_to_trash(original_file_path)


def image_resize(original_file_path, new_file_path, new_width=0,
                 delete_original=False, image_quality=70):
    """Resize or optimize image file

    Args:
        original_file_path (str): Original image full path
        new_file_path (str): New image full path
        new_width (int): The new image width, 0 only optimize
        delete_original (bool): Set to True will move original files to trash
        image_quality (int): 1 to 100, 1 worst, 100 best
    """
    img_pillow = Image.open(original_file_path)
    width, height = img_pillow.size

    if not new_width:
        new_width = width

    if new_width > width:
        new_width = width

    # New hight
    new_height = round((new_width * height) / width)

    # Resize
    new_img = img_pillow.resize((new_width, new_height), Image.LANCZOS)

    # Save
    new_img.save(new_file_path, optimize=True,
                 quality=image_quality, exif=img_pillow.info["exif"])

    # Close
    img_pillow.close()
    new_img.close()

    old_size = readable_size(os.path.getsize(original_file_path))
    new_size = readable_size(os.path.getsize(new_file_path))

    print(
        f'From {width}x{height} to {new_width}x{new_height}. '
        f'Optimized from {old_size} to {new_size}. '
        f'Original file: {os.path.basename(original_file_path)}'
    )

    # Move original file to trash
    if delete_original:
        send_file_to_trash(original_file_path)


def send_file_to_trash(path):
    """Move file to trash

    Args:
        path (str): Original file path
    """
    # send2trash.send2trash(path)
    os.remove(path)


def main(main_folder_path, delete_original=False, new_image_width=0,
         image_quality=70, video_crf=23):
    """Walk folders and subfolders and convert the videos

    Args:
        main_folder_path (str): The input folder path
        delete_original (bool): Set to True will move original files to trash
        new_image_width (int): The new image width, 0 only optimize
        image_quality (int): 1 to 100 (1 worst, 100 best)
        video_crf (int): 0 to 51 (0 lossless, 51 worst quality possible)
    """
    if not os.path.isdir(main_folder_path):
        raise NotADirectoryError('Path is not a directory.')

    video_extensions = ['.mp4', '.mov', '.mkv']
    image_extensions = ['.jpg', '.jpeg', '.png']
    allowed_extensions = video_extensions + image_extensions

    # Converted files will have this appended to their names
    converted_tag = '_CONVERTED'

    for root, dirs, files in os.walk(main_folder_path):
        for file in files:
            file_name, extension = os.path.splitext(file)

            # Only continue if the file extension is allowed
            if extension.lower() not in allowed_extensions:
                continue

            # Prevents reconvertion
            if converted_tag in file_name:
                continue

            # Output file
            new_file_name = file_name + converted_tag + extension

            # Full paths
            original_file_path = os.path.join(root, file)
            new_file_path = os.path.join(root, new_file_name)

            # Prevents overwrite
            if os.path.isfile(new_file_path):
                continue

            # Videos
            if extension.lower() in video_extensions:
                ffmpeg_convert(
                    original_file_path=original_file_path,
                    new_file_path=new_file_path,
                    delete_original=delete_original,
                    video_crf=video_crf
                )

            # Images
            elif extension.lower() in image_extensions:
                image_resize(
                    original_file_path=original_file_path,
                    new_file_path=new_file_path,
                    new_width=new_image_width,
                    delete_original=delete_original,
                    image_quality=image_quality
                )


def readable_size(size_in_bytes):
    """Converts bytes in a readable appropriate format

    Args:
        size_in_bytes (int): The size in bytes

    Returns:
        str: A readable number with the appropriate metric
    """

    # 1024 for Mebibyte
    # See: https://en.wikipedia.org/wiki/Mebibyte
    base = 1000

    # Choose the appropriate metric
    if size_in_bytes < base:
        new_size = f'{size_in_bytes:.2f}B'                 # Bytes
    elif size_in_bytes < (base ** 2):
        new_size = f'{size_in_bytes / (base ** 1):.2f}KB'  # Kilobytes
    elif size_in_bytes < (base ** 3):
        new_size = f'{size_in_bytes / (base ** 2):.2f}MB'  # Megabytes
    elif size_in_bytes < (base ** 4):
        new_size = f'{size_in_bytes / (base ** 3):.2f}GB'  # Gigabytes
    elif size_in_bytes < (base ** 5):
        new_size = f'{size_in_bytes / (base ** 4):.2f}TB'  # Terabytes
    else:
        new_size = f'{size_in_bytes / (base ** 5):.2f}PB'  # Petabytes

    return new_size


if __name__ == '__main__':
    # This is the main folder containing video or image files
    # This script will search any folder and subfolder inside the main folder
    main_folder_path = '/home/user/Desktop/100CANON/'

    delete_original_files = True  # Set to True will delete the original files
    new_image_width = 0  # if you don't want to resize, use 0
    image_quality = 70  # 70 is a good quality (1 worst, 100 best)
    video_crf = 23  # 17 to 28 are good values (17 better, 28 worse)

    main(
        main_folder_path=main_folder_path,
        delete_original=delete_original_files,
        new_image_width=new_image_width,
        image_quality=image_quality,
        video_crf=video_crf
    )
