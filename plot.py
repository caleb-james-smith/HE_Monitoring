# plot temperature and humidity

import matplotlib.pyplot as plt

def plot(filename,unit):
  data = open(filename,'r')
  values = []
  for line in data:
    parsed = line.split(" ")
    if parsed[0] == "#":  continue
    print parsed
    val = float((parsed[-1].split("\n"))[0])
    values.append(val)
  
  
  plt.plot(values)
  plt.ylabel(unit)
  plt.xlabel("Readout Module")
  plt.show()
  data.close()

if __name__ == "__main__":
  plot("humidity-5-JUL-2017.txt","Relative Humidity")

