import collections
from typing import overload

import legacyvideo
import datetime
from config import *

class VideoList(collections.UserList[video.Video]):
    STATIC_COUNT = 0

    def getAllVideosForDate(self, date: datetime.datetime, format: str = inputdateformat) -> VideoList:
        # return VideoList(list(filter(lambda x: (date.date() == x.date.date()), self)))
        tmp = []
        for i in self:
            if i.date.date() == date.date():
                tmp.append(i)
        return VideoList(tmp)


    def splitByDates(self) -> VideoList:
        result = []

        count = 0
        while count < len(self):
            tmp = self.getAllVideosForDate(self[count].date)
            count = count + len(tmp)

            result.append(tmp)


        # for i in range(len(self)):
        #     if self[i].date.date() == self[i-1].date.date() or i == 0:
        #         tmp.append(self[i])
        #
        # currentDate: datetime.datetime = self[0].date
        #
        
        return result

    def __init__(self, filenames: list[str], initlist=None):
        super().__init__(initlist)
        for i in filenames:
            currentvideo = video.Video(i)
            self.append(currentvideo)

            # ider what it does and why
            self.STATIC_COUNT = self.STATIC_COUNT + 1

    
