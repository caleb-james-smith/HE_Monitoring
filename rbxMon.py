from sendCommands import *
from argparse import ArgumentParser

def writeLog(message, logFile):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = now + " " + message
    logFile.write(message + "\n")
    print message

def peltier(steptime, intervaltime, testType):
    print "Step time: {0}".format(steptime)
    print "Interval time: {0}".format(intervaltime)
    cmdList1 = []
    cmdList2 = []
    port = 64400
    control_hub = "hcal904daq04"
    if testType == "disable":
        actionLog = "peltier.log"
        dataLog = "HB_Peltier_RM1_RM2.log"
        cmdFile1 = "enablePeltier.txt"
        cmdFile2 = "disablePeltier.txt"
        action1 = "Enabling Peltiers"
        action2 = "Disabling Peltiers"
        testName = "Peltier Enable / Disable Test"
    elif testType == "set":
        actionLog = "set_temp.log"
        dataLog = "HB_set_temperature.log"
        cmdFile1 = "set_temp_18.txt"
        cmdFile2 = "set_temp_5.txt"
        action1 = "Set temperature to 18.0 deg C"
        action2 = "Set temperature to 5.0 deg C"
        testName = "Set Temperature Test"
    else:
        print "Please use 'disable' or 'set' for test type."
        return
    for cmdFile, cmdList in zip(list(cmdFile1, cmdFile2), list(cmdList1, cmdList2)):
        with open(cmdFile, 'r') as f:
            for line in f:
                l = line.strip()
                if l != "": # Only consider non-empty lines
                    cmdList.append(line.strip())
    # enable, disable, and then enable peltier
    with open(actionLog, 'a') as pl:
        writeLog("Starting %s" % testName, pl)
        for i in xrange(3):
            if i in [0,2]:
                writeLog(action1, pl)
                results = send_commands(cmds=cmdList1,script=False,port=port,control_hub=control_hub)
            else:
                writeLog(action2, pl)
                results = send_commands(cmds=cmdList2,script=False,port=port,control_hub=control_hub)
            t = 0
            if i == 2:
                intervaltime *= 4
            while t < intervaltime:
                os.system("./ngfec_auto.py HBcommandList.txt -o " + dataLog)
                t += steptime
                if t < intervaltime: sleep(steptime) # don't sleep on the final iteration
        writeLog("Finishing %s" % testName, pl)

def runPeltier():
    parser = ArgumentParser()
    parser.add_argument("--step",     "-s", default=20,        help="step time in seconds between readings")
    parser.add_argument("--interval", "-i", default=240,       help="interval time in seconds between actions")
    parser.add_argument("--test",     "-t", default="disable", help="test type (can be disable or set)")
    args = parser.parse_args()
    steptime = int(args.step)
    intervaltime = int(args.interval)
    testType = str(args.test)
    peltier(steptime, intervaltime, testType)

def readRM(rbx, rm):
    nchannels = 0
    port = 0
    if "HE" in rbx:
        nchannels = 48
        port = 64100
    elif "HB" in rbx:
        nchannels = 64
        port = 64400
    name = "%s_RM%d" % (rbx, rm)
    dataLog = "%s_data.log" % (name)
    readLog = "%s_read.log" % (name)
    cmds = "%s.txt" % (name)
    control_hub = "hcal904daq04"
    cmdList = []
    with open(cmds, 'r') as f:
        for line in f:
            l = line.strip()
            if l != "": # Only consider non-empty lines
                cmdList.append(line.strip())

    with open(readLog, 'a') as rl:
        writeLog("Read %s" % name, rl)
        os.system("./ngfec_auto.py %s -o %s -p %d" %(cmds, dataLog, port))

def runRead():
    parser = ArgumentParser()
    parser.add_argument("--rbx",    "-r", default="HE0", help="RBX name (HE0, HB0)")
    parser.add_argument("--rm",     "-s", default="1",   help="Read from this RM slot number (1-4)")
    args = parser.parse_args()
    rbx = str(args.rbx)
    rm = int(args.rm)
    readRM(rbx, rm)

def main():
    runPeltier()
    #runRead()

if __name__ == "__main__":
    sys.exit(main())

