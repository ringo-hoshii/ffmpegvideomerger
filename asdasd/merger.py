import random
import os
import re
import subprocess
import string
import videolist
from config import *

LISTFILENAMELENGTH = 8

class Merger:
    """
    so what the code has to do is the following:
    1.  collect data about everything in the folder (including file size and file name)
    2.  group lists by day
    3.  count days. set to 0 by default. increment when reached the end of the day's VideoList
    4.  keep track of video length. with each video added we have to increment the global video's length counter
    4a. keep track of video size.
    6.  check if new_size > 256gb or > free_space or new_length

    so like every VideoList has to have its own size and length probably... unless... well... you kinda.. ye
    you do have to calculate the length of it first to see if it can be merged because what if it's too long.
    but you can also kinda estimate it by size. I'd say if size check passes only then ..ok fuck checks

    well...

    uhh..

    ok so every VideoList has to have its size and length... but the length shouldn't be calculated in the
    constructor. instead, it should be called from the Merger class


    so first of all... hmmmm... I mean



    """


    vidlist: videolist.VideoList = None
    utilityfolder = utilityfolder

    def __init__(self, directory: str, startfile: str = None, endfile: str = None):
        self.directory = directory
        self.oldcwd = os.getcwd()
        os.chdir(self.directory)
        if not os.path.exists(self.utilityfolder):
            os.mkdir(self.utilityfolder)
        self.vidlist = self.initVideoList(directory, startfile, endfile)
        self.vidlistSplitByDates = self.vidlist.splitByDates()
        



    def merge(self):
        separator = self.generateSeparator(self.vidlist[0].date.strftime(format))
        

        # e.g. 882o5dqq.txt
        mergelist = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(LISTFILENAMELENGTH)).join(".txt")

        # subprocess.call(f"ffmpeg -f concat -safe 0 -i {} -c copy".split(" "))
        
        
    def generateSeparator(self, text: str) -> str:
        separatorfilename = re.sub(r"[^0-9a-zA-Z]", "_", text) + ".mp4"
        ffmpegstring = f"ffmpeg -y -f lavfi -i color=size={resolution}:duration={duration}:rate={framerate}:color={color} -vf \"drawtext=fontfile={font}:fontsize={fontsize}:fontcolor={fontcolor}:x=(w-text_w)/2:y=(h-text_h)/2:text='{text}'\" {separatorfilename}"
        subprocess.call(ffmpegstring)
        
        return separatorfilename
        
    def checkValidFilename(self, flnm: str):
        return flnm.endswith("DVR.mp4")

    def initVideoList(self, directory: str, startfile: str = None, endfile: str = None) -> videolist.VideoList:
        filenames = next(os.walk(directory), (None, None, []))[2]
        res = list(filter(self.checkValidFilename, filenames))
        return videolist.VideoList(res)
