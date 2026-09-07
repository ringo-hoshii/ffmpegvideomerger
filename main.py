import os
import re
from datetime import timedelta

import srt
import subprocess
import datetime as dt
from tqdm import tqdm

import pymediainfo

VIDEOSFROM = "D:\\Videos\\NVIDIA\\"
VIDEOSTO = "E:\\Videos\\NVIDIA\\"
VIDEO_DATE_PART = r'(\d{4}\.\d{2}\.\d{2} - \d{2}\.\d{2}\.\d{2})'
FILTER_FOR_VIDEOS = r'^.*' + VIDEO_DATE_PART + '.*\\.DVR\\.mp4$'
GLOBAL_COUNT = 0
FFMPEG_INPUT_FILE = "ffmpeg_input_list.txt"

def get_files_in_directory(directory):
    files = next(os.walk(directory), (None, None, []))[2]
    return files

def get_directories_in_directory(working_directory) -> list[str]:
    directories = next(os.walk(working_directory), (None, None, []))[1]
    return directories

def get_videos_in_directory(working_directory, filter_string=FILTER_FOR_VIDEOS):
    pattern = re.compile(filter_string)
    video_filter_lambda = lambda x: pattern.match(x)
    videos_in_directory = list(filter(video_filter_lambda, get_files_in_directory(working_directory)))
    return videos_in_directory

def list_files_walk(start_path='.'):
    lst = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            lst.append(os.path.join(root, file))
    return lst

def get_date_part(videoname):
    return re.search(FILTER_FOR_VIDEOS, videoname).group(1)

def get_all_videos_in_subfolders(working_directory):
    fileslist = list_files_walk(working_directory)
    videoslist = list(filter(lambda x: re.compile(FILTER_FOR_VIDEOS).match(x), fileslist))
    videoslist.sort(key=lambda x: get_date_part(x))
    return videoslist

def get_unique_dates(videolist):
    tmp = []
    for i in videolist:
        tmp.append(get_date_part(i).split(" - ")[0])
    res = list(set(tmp))
    res.sort()
    return res

def get_videos_by_date(videolist, date):
    resultlist = list(filter(lambda x: date in x, videolist))
    return resultlist

def generate_ffmpeg_list_file(videolist, path):
    with open(path, "w") as f:
        for video in videolist:
            f.write(f"file '{video}'\n")

def get_length(video):
    obj = pymediainfo.MediaInfo.parse(video)
    length = int(obj.video_tracks[0].duration)
    return timedelta(milliseconds=length)

def generate_subtitles_file(videolist, path):
    count = 1
    totallength = srt.ZERO_TIMEDELTA
    sublist = []
    for i in videolist:
        starttime = totallength
        totallength += get_length(i)
        endtime = totallength
        sublist.append(srt.Subtitle(count, start=starttime, end=endtime, content=os.path.basename(i)))
        count += 1
    with open(path, "w") as f:
        f.write(srt.compose(sublist))

def run_ffmpeg_merge(inputfile, outputfile, logfile, subtitlesfile):
    with open(logfile, "a") as f:
        ffmpeg_string = f"ffmpeg -y -i \"{subtitlesfile}\" -f concat -safe 0 -i \"{inputfile}\" -c:a copy -c:v copy -c:s mov_text \"{outputfile}\""
        runobj = subprocess.run(ffmpeg_string, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True, check=True)
        f.write(dt.datetime.now().strftime("[%Y/%m/%d %H:%M:%S]\n"))
        f.write(runobj.stdout)
        f.write("\n")

def generate_ffmetadata(videolist, lengthlist, path):




def main1():
    os.chdir(VIDEOSTO)

    videoslist = get_all_videos_in_subfolders(VIDEOSFROM)
    unique_dates = get_unique_dates(videoslist)

    print(get_length(videoslist[0]))

    asd = get_videos_by_date(videoslist, unique_dates[0])
    with open(FFMPEG_INPUT_FILE, "w") as ffmpeg_input_fd:
        for i in asd:
            ffmpeg_input_fd.write(f"file '{i}'\n")

    replacedfilename = asd[0].split("\\")[-1].split(" - ")[0].replace(".", "_").replace(" ", "_")
    # ffmpeg_string = f"ffmpeg -y -f concat -safe 0 -hwaccel cuda -hwaccel_output_format cuda -i ffmpeg_input_list.txt -c:a copy -c:v av1_nvenc {replacedfilename}"



    ffmpeg_string = f"ffmpeg -y -i {replacedfilename}.srt -f concat -safe 0 ffmpeg_input_list.txt -c:a copy -c:v copy -c:s mov_text {replacedfilename}.mp4"

    runobj = subprocess.run(ffmpeg_string, capture_output=True, text=True)
    runstderr = runobj.stderr
    runstdout = runobj.stdout


    print()

def main():
    videolist = get_all_videos_in_subfolders(VIDEOSFROM)
    unique_dates = get_unique_dates(videolist)
    videossplitbydate = []
    for i in unique_dates:
        videossplitbydate.append(get_videos_by_date(videolist, i))

    for i in tqdm(videossplitbydate):
        outputfilepath = VIDEOSTO+os.path.basename(i[0])
        ffmpeg_input_file_path = VIDEOSTO + "__input.txt"
        subfilepath = VIDEOSTO+"subtitles\\"+os.path.basename(i[0])+".srt"
        logfilepath = VIDEOSTO+"ffmpeglog.txt"

        generate_ffmpeg_list_file(i, ffmpeg_input_file_path)
        generate_subtitles_file(i, subfilepath)
        run_ffmpeg_merge(ffmpeg_input_file_path, outputfilepath, logfilepath, subfilepath)
    print()

if __name__ == "__main__":
    main()