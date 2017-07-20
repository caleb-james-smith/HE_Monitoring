#!/bin/bash
ssh -T hcal904daq02 << 'END'
pushd /cms904nfshome0/nfshome0/msaunder/HE_Monitoring
./ngfec_auto.py commandList.txt -o rbx.log
./statPlot.py rbx.log
popd
END
