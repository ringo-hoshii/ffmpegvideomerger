for i in filenames:
    videodate, txtfilename = getdate(i)
    if videodate.date() == iterationdate:
        tmp.append(i)
    else:
        videosbyday.append(tmp)
        iterationdate = videodate.date()
        tmp = []
