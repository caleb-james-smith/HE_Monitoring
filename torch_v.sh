logfile="torch.log"
echo "V2V $1" | nc localhost 39221
sleep 1
echo "V2O?; I2O?" | nc localhost 39221

echo "$(date) Set voltage to $1" >> $logfile
echo "V2O?;I2O?" | nc localhost 39221 >> $logfile
