import functools
import json
import os
import re
import datetime
import subprocess
from math import floor
from pprint import pprint

import cv2
import pymediainfo
from tqdm import tqdm

DIRECTORY = "D:\\Videos\\NVIDIA\\Desktop\\"
REMOTEDIRECTORY = "E:\\Videos\\NVIDIA\\"

def getlength(filename):
    obj = pymediainfo.MediaInfo.parse(filename)
    length = int(obj.video_tracks[0].duration)
    return length

def getdate(filename: str) -> tuple[datetime.datetime, str]:
    leftpart = filename.split(" - ")[0]
    replacedfilename = leftpart.replace(".", "_").replace(" ", "_")
    videodate = re.search("^.*(\\d\\d\\d\\d\\.\\d\\d\\.\\d\\d).*$", leftpart).group(1)
    videodate = datetime.datetime.strptime(videodate, "%Y.%m.%d")
    return videodate, replacedfilename

def get_video_resolution_v2(file_path):
    obj = pymediainfo.MediaInfo.parse(file_path)
    return f'{obj.video_tracks[0].width}x{obj.video_tracks[0].height}'


@functools.cache
def get_video_resolution(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json", file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    data = json.loads(result.stdout)
    stream = data["streams"][0]
    return f'{stream["width"]}x{stream["height"]}'


def main():
    # get all files in a directory
    allfiles = next(os.walk(DIRECTORY), (None, None, []))[2]
    # filter out files ending with DVR.mp4
    filenames: list[str] = list[str](filter((lambda x: x.endswith("DVR.mp4")), allfiles))

    videosbyday = []
    tmp = []
    iterationdate, _ = getdate(filenames[0])

    f = open("test.txt", "r+")
    size = 0
    count = 0
    videocount = 0
    for i in tqdm(filenames):
        videodate, txtfilename = getdate(i)
        if videodate != iterationdate:
            videosbyday.append(tmp)
            iterationdate = videodate
            tmp = []
            count += 1
        tmp.append(i)
        videocount += 1
    videosbyday.append(tmp)
    f.close()

    os.chdir(f'{REMOTEDIRECTORY}')

    daycount = 0

    print()
    print("[Merging videos]")
    for day in videosbyday:
        # if daycount == 14:
        #     break
        f = open("__input.txt", "w")
        now = datetime.datetime.now()
        ffmpeglogfilename = now.strftime("ffmpeg_%Y_%m_%d_%H_%M_%S.txt")
        ffmpeglog = open(f"logs/{ffmpeglogfilename}", "a")
        replacedfilename = getdate(day[0])[1]
        fhumanreadable = open(f'manifests/{replacedfilename}.txt', "w")

        offset = 0

        for video in day:
            delta = datetime.timedelta(seconds=offset/1000)
            hours = floor(delta.total_seconds() / 3600)
            minutes = floor((delta.total_seconds() - hours * 3600) / 60)
            seconds = floor(delta.total_seconds() - hours * 3600 - minutes * 60)
            offsetstr = f'{hours}:{minutes:02d}:{seconds:02d}'
            f.write(f"file '{DIRECTORY}{video}'\n")
            fhumanreadable.write(f'"{video}" {offsetstr}\n')
            offset += getlength(DIRECTORY+video)

        f.close()
        print(os.getcwd())
        if "2026.08.25" not in video:
            continue
        subprocess.call(f"ffmpeg -f concat -safe 0 -hwaccel cuda -hwaccel_output_format cuda -i __input.txt -c:a copy -c:v av1_nvenc {replacedfilename}.mp4", stdout=ffmpeglog, stderr=ffmpeglog)
        print(f'{replacedfilename}.mp4 DONE')

        fhumanreadable.close()
        ffmpeglog.close()



        daycount += 1


if __name__ == "__main__":
    main()