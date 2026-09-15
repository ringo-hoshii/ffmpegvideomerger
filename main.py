from merger import *
from tqdm import tqdm

STARTDATE = ""
ENDDATE = ""

# STARTDATE = "2026/6/1"
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

def main():
    # MAIN PREPARATION PART
    videolist = get_all_videos_in_subfolders(VIDEOSFROM)
    unique_dates = get_unique_dates(videolist)
    videossplitbydate = []
    for i in unique_dates:
        i_datetime = dt.datetime.strptime(i, "%Y.%m.%d")
        if STARTDATE < i_datetime < ENDDATE:
            videossplitbydate.append(get_videos_by_date(videolist, i))

    tmp = []
    for i in videossplitbydate:
        tmp.extend(i)

    with open("tmp_clip_has_multiple_audio_tracks.txt", "w") as f:
        for count, i in enumerate(tqdm(tmp)):
            f.write(f"\"{i}\" {has_multiple_audio_tracks(i)}\n")

    # END OF MAIN PREPARATION PART

    for i in tqdm(videossplitbydate):
        videoname = os.path.basename(i[0]).split(" - ")[0].replace(" ", "_").replace(".", "_").replace("'", "") + ".mp4"
        outputfilepath = VIDEOSTO+videoname
        # merge_clips(i, outputfilepath)
    print()

if __name__ == "__main__":
    main()