#!/usr/bin/python
from sendCommands import *
from argparse import ArgumentParser
from ngfec_auto import getCmdList, getCmdString
from ROOT import TTree, TFile
from array import array

def writeLog(message, logFile, verbose=1):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = now + " " + message
    logFile.write(message + "\n")
    if verbose:
        print message

def peltier(steptime, intervaltime, testType):
    print "Step time: {0}".format(steptime)
    print "Interval time: {0}".format(intervaltime)
    cmdList1 = []
    cmdList2 = []
    port = 64400
    control_hub = "hcal904daq04"
    if testType == "disable":
        actionLog = "disable_peltier.log"
        dataLog = "HB_%s" % actionLog
        cmdFiles = ["enablePeltier.txt", "disablePeltier.txt", "enablePeltier.txt"]
        actions = ["Enabling Peltiers", "Disabling Peltiers", "Enabling Peltiers"]
        testName = "Disable Peltier Test"
    elif testType == "set":
        actionLog = "set_temperature.log"
        dataLog = "HB_%s" % actionLog
        cmdFiles = ["set_temp_18.txt", "set_temp_5.txt", "set_temp_18.txt"]
        actions = ["Set temperature to 18.0 deg C", "Set temperature to 5.0 deg C", "Set temperature to 18.0 deg C"]
        testName = "Set Temperature Test"
    elif testType == "scan":
        actionLog = "scan_voltage.log"
        dataLog = "HB_%s" % actionLog
        cmdFiles = list("set_voltage_%d.txt" % i for i in xrange(8))
        actions = list("Set Peltier Voltage to %fV" % i for i in xrange(8))
        testName = "Scan Peltier Voltage Test"
    elif testType == "monitor":
        actionLog = "monitor.log"
        dataLog = "HB_%s" % actionLog
        cmdFiles = []
        actions = ["Read values"]
        testName = "Monitor Values"
    else:
        print "Please use 'disable', 'set', 'scan', or 'monitor' for test type."
        return
    cmdLists = []
    for cmdFile in cmdFiles:
        cmdList = getCmdList(cmdFile)
        cmdLists.append(cmdList)
    # begin test
    with open(actionLog, 'a') as f:
        writeLog("Starting %s" % testName, f)
    
    readCmdFile = "HBcommandList.txt"
    readCmdList = getCmdList(readCmdFile)
    readCmdString = getCmdString(readCmdList)

    #Makeing Run Tree
    tfile = TFile('power_test.root', 'recreate')
    tree = TTree('t1', 't1')    
    tfile.Write()
    tfile.Close()
    #tfile = TFile.Open("power_test.root","UPDATE")
    #tree = tfile.Get("t1")
    runArray = array( 'i', [ 0 ] )
    #with open(dataLog, 'a') as f:
    #    writeLog(readCmdString, f, 0)
    # loop through actions
    for i, action in enumerate(actions):
        with open(actionLog, 'a') as f:
            writeLog(action, f)
            if cmdLists:
                results = send_commands(cmds=cmdLists[i],script=False,port=port,control_hub=control_hub)
                print results
        t = 0
        while t < intervaltime:
            runNum = (t/steptime)+1
            print "Processing Run  {0}".format(runNum)
            #if(tree.GetEntry(0)==0): tree.Branch('run', runArray, 'runArray/I') #Need a better way to check if branch exist
            runArray[0] = runNum
            os.system("./ngfec_auto.py %s -o %s -p %d -r True" % (readCmdFile, dataLog, port))
            t += steptime
            if t < intervaltime: sleep(steptime) # don't sleep on the final iteration

    #tree.Fill
    #tfile.Write()
    #tfile.Close()
    with open(actionLog, 'a') as f:
        writeLog("Finishing %s" % testName, f)

def runPeltier():
    parser = ArgumentParser()
    parser.add_argument("--step",     "-s", default=20,        help="step time in seconds between readings")
    parser.add_argument("--interval", "-i", default=20,        help="interval time in seconds between actions")
    parser.add_argument("--test",     "-t", default="monitor", help="test type (can be disable, set, scan, or monitor)")
    parser.add_argument("--current",  "-c", default=-1.0,      help="current from power supply")
    parser.add_argument("--voltage",  "-v", default=-1.0,      help="voltage from power supply")
    args = parser.parse_args()
    steptime = int(args.step)
    intervaltime = int(args.interval)
    testType = str(args.test)
    current = float(args.current)
    voltage = float(args.voltage)
    if (current == -1.0 and voltage != -1.0) or (current != -1.0 and voltage == -1.0):
        print "Please provide both -c current and -v voltage from the power supply."
        return
    elif current == -1.0 and voltage == -1.0:
        peltier(steptime, intervaltime, testType)
    else:
        with open ("power_supply.log", 'a') as f:
            writeLog("%f %f" % (voltage, current), f)

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

    with open(readLog, 'a') as f:
        writeLog("Read %s" % name, f)
        os.system("./ngfec_auto.py %s -o %s -p %d -r True" %(cmds, dataLog, port))

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

