#!/bin/bash
pushd /home/daq/HE_Monitoring
./ngfec_auto.py commandList.txt -o rbx.log
./statPlot.py rbx.log -n -10
popd
