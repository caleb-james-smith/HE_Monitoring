logfile="torch.log"
host="cms904usr"
dir="$(pwd)"

ssh -T $host << EOF
  cd $dir
  echo "V2O?;I2O?" | nc localhost 39221
  echo "$(date) Read voltage and current." >> $logfile
  echo "V2O?;I2O?" | nc localhost 39221 >> $logfile
EOF
