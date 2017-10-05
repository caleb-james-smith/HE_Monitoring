#!/bin/bash
ssh -T daq@cmshcaltb02 << 'END'
pushd /home/daq/HE_Monitoring
./ngfec_auto.py commandList.txt -o rbx.log
./statPlot.py rbx.log -n -10
popd
END
