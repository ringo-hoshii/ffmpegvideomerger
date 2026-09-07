import subprocess
import datetime
import re
import cv2
from config import *

class Video:
    length: float = None
    filename: str = None
    date: datetime.datetime = None

    def __init__(self, filename):
        self.filename = filename
        self.date = self.getDate(regex)
        # self.length = self.getLength()

    def initLength(self) -> None:
        self.length = self.getLength()

    def getLength(self) -> float:
        video = cv2.VideoCapture(self.filename)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = video.get(cv2.CAP_PROP_FPS) 
        return frame_count / fps

    @DeprecationWarning
    def oldGetLength(self) -> float:
        result = float(subprocess.check_output(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{self.filename}\""))
        return float(result)
    
    def getDate(self, regex: str) -> datetime.datetime:
        # regex string must contain 2 capture groups
        
        # e.g. 2026.03.02
        searchres = re.search(regex, self.filename)
        datestr = searchres.group(1) + " " + searchres.group(2)
        
        return datetime.datetime.strptime(datestr, inputdateformat)

