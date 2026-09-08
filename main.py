import cProfile
import pstats
from datetime import timedelta
from http.cookiejar import cut_port_re

from tqdm import tqdm

import os
import re
import srt
import subprocess
import pymediainfo

import datetime as dt

STARTDATE = ""
ENDDATE = ""

# VIDEOSFROM = "D:\\Videos\\NVIDIATEST\\"
VIDEOSFROM = "D:\\Videos\\NVIDIA\\"
# VIDEOSTO = "D:\\Videos\\NVIDIAOUTPUT\\"
VIDEOSTO = "E:\\Videos\\NVIDIA\\"
DEFAULT_START_DATE = dt.datetime(1, 1, 1)
DEFAULT_END_DATE = dt.datetime(9999, 12, 31)

VIDEO_DATE_PART = r'(\d{4}\.\d{2}\.\d{2} - \d{2}\.\d{2}\.\d{2})'
FILTER_FOR_VIDEOS = r'^.*' + VIDEO_DATE_PART + '.*\\.DVR\\.mp4$'
GLOBAL_COUNT = 0
FFMPEG_INPUT_FILE = "ffmpeg_input_list.txt"
METADATA_FILE = "metadata.txt"

SCRIPT_WORKING_DIRECTORY = os.getcwd()

if not STARTDATE or STARTDATE == "":
    STARTDATE = DEFAULT_START_DATE
else:
    STARTDATE = dt.datetime.strptime(STARTDATE, "%Y/%m/%d")

if not ENDDATE or ENDDATE == "":
    ENDDATE = DEFAULT_END_DATE
else:
    ENDDATE = dt.datetime.strptime(ENDDATE, "%Y/%m/%d")

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


def load_metadata(path):
    metadata = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r'^"([^"]+)"\s+([\d.]+)', line)

            if match:
                filename = match.group(1)
                duration = float(match.group(2))
                metadata[filename] = duration

    return metadata

def timedelta_to_milliseconds(delta):
    # return delta.days * 86400000 + delta.seconds * 1000 + delta.microseconds / 1000
    return int(delta / timedelta(milliseconds=1))

def get_length(video):
    obj = pymediainfo.MediaInfo.parse(video)
    length = int(obj.video_tracks[0].duration)
    return timedelta(milliseconds=length)

def get_length_list(videolist):
    res = []
    for i in videolist:
        res.append(get_length(i))
    return res

def generate_subtitles_file(videolist, path, lengthlist):
    count = 1
    totallength = srt.ZERO_TIMEDELTA
    sublist = []
    for i, j in zip(videolist, lengthlist):
        starttime = totallength
        totallength += j
        endtime = totallength
        sublist.append(srt.Subtitle(count, start=starttime, end=endtime, content=os.path.basename(i)))
        count += 1
    with open(path, "w") as f:
        f.write(srt.compose(sublist))

def generate_ffmetadata(videolist, lengthlist, path):
    currentlength = srt.ZERO_TIMEDELTA
    with open(path, "w") as f:
        f.write(";FFMETADATA1\n\n")
        for i, j in zip(videolist, lengthlist):
            metadata_block = f"""[CHAPTER]
TIMEBASE=1/1000
START={timedelta_to_milliseconds(currentlength)}
END={timedelta_to_milliseconds(currentlength+j)}
TITLE={os.path.basename(i)}\n\n"""
            f.write(metadata_block)
            currentlength += j

def run_ffmpeg_merge(inputfile, outputfile, logfile, subtitlesfile, metadatafile):
    with open(logfile, "a") as f:
        ffmpeg_string = f"ffmpeg -y -i \"{subtitlesfile}\" -i \"{metadatafile}\" -f concat -safe 0 -i \"{inputfile}\" -c:a copy -c:v h264_nvenc -c:s mov_text -map_metadata 1 -map_chapters 1 \"{outputfile}\""
        runobj = subprocess.run(ffmpeg_string, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
        f.write(dt.datetime.now().strftime("[%Y/%m/%d %H:%M:%S]\n"))
        f.write(runobj.stdout)
        f.write("\n")
        if runobj.returncode != 0:
            raise subprocess.CalledProcessError(runobj.returncode, ffmpeg_string, runobj.stdout, runobj.stderr)

def main():
    count = 0

    videolist = get_all_videos_in_subfolders(VIDEOSFROM)
    unique_dates = get_unique_dates(videolist)
    videossplitbydate = []
    for i in unique_dates:
        i_datetime = dt.datetime.strptime(i, "%Y.%m.%d")
        if STARTDATE < i_datetime < ENDDATE:
            videossplitbydate.append(get_videos_by_date(videolist, i))

    for i in tqdm(videossplitbydate):
        if count >= 2:
            break
        outputfilepath = VIDEOSTO+os.path.basename(i[0])
        ffmpeg_input_file_path = VIDEOSTO + "__input.txt"
        subfilepath = VIDEOSTO+f"subtitles\\"+os.path.basename(i[0])+".srt"
        logfilepath = VIDEOSTO+f"logs\\ffmpeglog_{dt.datetime.now().strftime("%Y_%m_%d")}.txt"
        metadatapath = VIDEOSTO+f"ffmpegmetadata.txt"

        generate_ffmpeg_list_file(i, ffmpeg_input_file_path)
        lengthlist = get_length_list(i)
        generate_subtitles_file(i, subfilepath, lengthlist)
        generate_ffmetadata(i, lengthlist, metadatapath)
        run_ffmpeg_merge(ffmpeg_input_file_path, outputfilepath, logfilepath, subfilepath, metadatapath)

        count += 1
    print()

def show_profiler_data(path):
    with open(path, "w") as f:
        profiler = cProfile.Profile()
        stats = pstats.Stats(profiler, stream=f)
        stats.strip_dirs().sort_stats("cumulative").print_stats()

if __name__ == "__main__":

    # profiler = cProfile.Profile()
    # profiler.enable()
    main()
    # profiler.disable()
    # os.chdir(SCRIPT_WORKING_DIRECTORY)
    # profiler.dump_stats("main.prof")

    # show_profiler_data("main.prof")