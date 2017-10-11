logfile="torch.log"
echo "V2O?;I2O?" | nc localhost 39221
echo "$(date) Read voltage and current." >> $logfile
echo "V2O?;I2O?" | nc localhost 39221 >> $logfile
