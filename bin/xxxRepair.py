import os
import re
import sys
import threading

def getNumbersInText(text):
    return re.findall(r"(-?\d+)", text)

fp = open(sys.argv[2], 'r')
ip = sys.argv[1]
text = fp.read()
fp.close()
logNum = text.count('ranges have been repaired')
text = text.split('\n')
totalRangeNum = len(text) - logNum - 2
keyspaceAndCF = text[0]
repairedNum = int(getNumbersInText(text[-2])[0])

terminateProcess = False
def terminateProcessManually():
    print raw_input()
    global terminateProcess
    terminateProcess = True
terminateThread = threading.Thread(target=terminateProcessManually)
terminateThread.start()

print "xxxRepair : Repairing all ranges that need to be repaired"
hasFailure = False
fpFailed = open(sys.argv[2][:-4] + "_failed.txt", "w")
fpFailed.write(keyspaceAndCF + '\n')
# Repair all ranges that need to be repaired
for i in range(repairedNum + 1, totalRangeNum + 1):
    if terminateProcess == True:
        print "xxxRepair is terminated manually"
        break
    repairedNum = repairedNum + 1
    log = os.popen("nodetool -h %s repair -st %s -et %s %s" % (ip,\
            getNumbersInText(text[i])[0], getNumbersInText(text[i])[1], keyspaceAndCF)).read()
    if "successfully" in log:
        print str(repairedNum) + " / " + str(totalRangeNum) + " has been repaired successfully"
    else:
        hasFailure = True
        print "Failed to repair range " + str(repairedNum)
        print log
        fpFailed.write(getNumbersInText(text[i])[0] + " " + getNumbersInText(text[i])[1] + "\n")
    print "Press Enter to terminate the process"

if hasFailure:
    print str(repairedNum) + ' ranges have been repaired with some failures'
    fpFailed.writelines('0 ranges have been repaired' + '\n')
    fpFailed.close()
else:
    print str(repairedNum) + ' ranges have been repaired'
    fpFailed.close()
    os.remove(sys.argv[2][:-4] + "_failed.txt")
fp = open(sys.argv[2], 'a')
fp.writelines(str(repairedNum) + ' ranges have been repaired' + '\n')
fp.close()