from math import floor
from pprint import pprint
from video import Video
import datetime

class Test:
    def test(self):
        pass

def yield_class():
    yield Test()

def main1():

    tmp = []
    count = 0
    with open("metadata.txt", "r") as f:
        while True:
            tmpstr = f.readline()
            if tmpstr == "":
                break
            tmp.append(tmpstr)
            count += 1


    pprint(tmp)

def main2():
    asd = datetime.timedelta(seconds=0)
    print(asd)
    print(int(asd.total_seconds()))

    hours = floor(asd.total_seconds()/3600)
    minutes = floor((asd.total_seconds() - hours * 3600) / 60)
    seconds = floor(asd.total_seconds() - hours * 3600 - minutes * 60)

    now = datetime.datetime.now()
    now.strftime("%Y_%m_%d_%H_%M_%S")

    print(f'{hours}:{minutes:02d}:{seconds:02d}')

def main3():
    asd = yield_class()
    print()


if __name__ == "__main__":
    main3()