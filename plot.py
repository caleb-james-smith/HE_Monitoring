# plot temperature and humidity

import matplotlib.pyplot as plt

def plot(filename,unit):
  data = open(filename,'r')
  values = []
  for line in data:
    parsed = line.split(" ")
    if parsed[0] == "#":  continue
    #print parsed
    val = float((parsed[-1].split("\n"))[0])
    values.append(val)
  
  data.close()
  
  vmin, vmax = 0.0, 10.0

  # line graph (value vs readout modudle)
  plt.plot(values)
  plt.axis([0,72,vmin,vmax])
  plt.ylabel(unit)
  plt.xlabel("Readout Module")
  plt.title("Monitoring "+unit)
  plt.grid(True)
  plt.show()
  
  # histogram (count vs value)
  n, bins, patches = plt.hist(values, 20, facecolor='g', alpha=0.75)
  plt.axis([vmin,vmax,0,20])
  plt.ylabel("Number of Readout Modules")
  plt.xlabel(unit)
  plt.title("Monitoring "+unit)
  plt.grid(True)
  plt.show()

if __name__ == "__main__":
  plot("humidity-5-JUL-2017.txt","Relative Humidity")

