import sys

from merger import *
from tqdm import tqdm

# STARTDATE = ""
ENDDATE = ""

STARTDATE = "2026/7/4"
# ENDDATE = "2026/7/31"

# VIDEOSFROM = "D:\\Videos\\NVIDIATEST\\"
VIDEOSFROM = "D:\\Videos\\NVIDIA\\"
# VIDEOSTO = "D:\\Videos\\NVIDIAOUTPUT\\"
VIDEOSTO = "E:\\Videos\\NVIDIA\\"
DEFAULT_START_DATE = dt.datetime(1, 1, 1)
DEFAULT_END_DATE = dt.datetime(9999, 12, 31)

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

def amerge():
    videolist = get_all_videos_in_subfolders(VIDEOSTO+"backup")

    tmpoutput = []
    with tqdm(videolist, file=sys.stdout, position=0, leave=True) as mytqdm:
        for i in mytqdm:
            foldername = os.path.basename(re.match("^(.*) \\d{4}\\.\\d{2}\\.\\d{2}.*$", i).group(1))
            outputfile = VIDEOSFROM+foldername+"\\"+os.path.basename(i)
            ffmpegstring = f"ffmpeg -y -i \"{i}\" -c:v copy -c:a aac -ac 2 -filter_complex amerge=inputs=2 \"{outputfile}\""
            mytqdm.set_description(outputfile)
            tqdm.write(outputfile)
            objrun = subprocess.run(ffmpegstring, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, check=True)
            tmpoutput.append(objrun.stdout)

    return

def amix():
    videolist = get_all_videos_in_subfolders(VIDEOSTO+"backup")

    tmpoutput = []
    with tqdm(videolist, file=sys.stdout, position=0, leave=True) as mytqdm:
        for i in mytqdm:
            foldername = os.path.basename(re.match("^(.*) \\d{4}\\.\\d{2}\\.\\d{2}.*$", i).group(1))
            outputfile = VIDEOSFROM+foldername+"\\"+os.path.basename(i)
            ffmpegstring = f"ffmpeg -y -i \"{i}\" -c:v copy -c:a aac -b:a 196k -filter_complex \"[0:a]amix=inputs=2[aout]\" -map 0:v -map \"[aout]\" -map_metadata 0 \"{outputfile}\""
            mytqdm.set_description(outputfile)
            objrun = subprocess.run(ffmpegstring, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, check=True)
            tqdm.write(outputfile)
            tmpoutput.append(objrun.stdout)

    return

def genffprobe(videossplitbydate):
    abc = Path(SCRIPT_WORKING_DIRECTORY) / "ffprobe_output.txt"
    with open(abc, "wb") as f:
        for i in videossplitbydate[0]:
            f.write(f"{i}\n".encode("utf-8"))
            ffprobe_string = ["ffprobe", i]
            fff = subprocess.run(ffprobe_string, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            f.write(fff.stdout)
            f.write("\n".encode("utf-8"))
            # if fff.returncode != 0:
            #     raise subprocess.CalledProcessError(fff.returncode, ffprobe_string, fff.stdout, fff.stderr)

def main():
    print(1)
    amix()





    # abc = tqdm(range(100), file=sys.stdout, position=0, leave=True)
    #
    # for i in abc:
    #     abc.set_description(str(i))
    #     tqdm.write(str(i))
    #     time.sleep(1)

    # amerge()

    # MAIN PREPARATION PART
    tmptmp = []
    tmptmpdates = []
    with open("tmp_clip_has_multiple_audio_tracks.txt", "r") as f:
        lines = f.read().split("\n")
        for i in lines:
            if "True" in i:
                i = re.sub("^\"(.*)\" .*$", "\\1", i)
                tmptmp.append(i)
                tmptmpdates.append(get_date(i))
                # shutil.copy(i, VIDEOSTO+"backup")

    # merge_clips(tmptmp[0:50], "D:\\Desktop\\mp4file.mp4", video_encoding="av1_nvenc", audio_encoding="aac")
    asddsa = list(set(tmptmpdates))
    asddsa.sort()
    dsa = []
    for i in asddsa:
        dsa.append(i.strftime("%Y.%m.%d"))

    print(2)

    videolist = get_all_videos_in_subfolders(VIDEOSFROM)
    unique_dates = get_unique_dates(videolist)
    videossplitbydate = []
    # for i in unique_dates:
    #     i_datetime = dt.datetime.strptime(i, "%Y.%m.%d")
    #     if STARTDATE < i_datetime < ENDDATE:
    #         videossplitbydate.append(get_videos_by_date(videolist, i))

    for i in dsa:
        videossplitbydate.append(get_videos_by_date(videolist, i))

    print(3)

    print(4)

    tmp = []
    for i in videossplitbydate:
        tmp.extend(i)

    # objrun = subprocess.run(["ffprobe", videossplitbydate[0][0]], capture_output=True)
    # print(objrun.stdout)

    # with open("tmp_clip_has_multiple_audio_tracks.txt", "w") as f:
    #     for count, i in enumerate(tqdm(tmp)):
    #         f.write(f"\"{i}\" {has_multiple_audio_tracks(i)}\n")

    # END OF MAIN PREPARATION PART

    # videossplitbydate.pop(0)

    with tqdm(videossplitbydate, file=sys.stdout, position=0, leave=True) as mytqdm:
        for i in mytqdm:
            videoname = os.path.basename(i[0]).split(" - ")[0].replace(" ", "_").replace(".", "_").replace("'", "") + ".mp4"
            mytqdm.set_description(videoname)
            outputfilepath = VIDEOSTO+videoname
            merge_clips(i, outputfilepath, merge_2_audio_tracks=False, audio_encoding="aac", video_encoding="av1_nvenc")
            tqdm.write(videoname)
            pass
    print()

if __name__ == "__main__":
    main()