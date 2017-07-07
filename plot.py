# plot temperature and humidity

import matplotlib.pyplot as plt
import imageio

def plot(filename,unit,plot_directory):
  data_directory = "measurements/"
  data = open(data_directory+filename+'.txt','r')
  values = []
  num_rm = 0
  for line in data:
    parsed = line.split(" ")
    if parsed[0] == "#":  continue
    #print parsed
    val = float((parsed[-1].split("\n"))[0])
    values.append(val)
    num_rm += 1
  
  data.close()
  
  vmin, vmax = 0.0, 100.0
  if "Temperature" in unit:
    vmin, vmax = 0.0, 50.0 # deg C
  elif "Humidity" in unit:
    vmin, vmax = 0.0, 10.0 # percent

  fig = plt.figure()
  
  # line graph (value vs readout modudle)
  plt.plot(values)
  plt.axis([0,num_rm,vmin,vmax])
  plt.ylabel(unit)
  plt.xlabel("Readout Module")
  plt.title("Monitoring "+unit)
  plt.grid(True)
  #plt.show()
  fig.savefig(plot_directory+filename+"_1.png")
  plt.clf()
  
  # histogram (count vs value)
  n, bins, patches = plt.hist(values, 20, facecolor='g', alpha=0.75)
  plt.axis([vmin,vmax,0,20])
  plt.ylabel("Number of Readout Modules")
  plt.xlabel(unit)
  plt.title("Monitoring "+unit)
  plt.grid(True)
  #plt.show()
  fig.savefig(plot_directory+filename+"_2.png")
  plt.clf()

def makeGif(filenames, gifname, unit):
  plot_directory = "images/"
  for append in [1,2]:
    with imageio.get_writer(gifname+'_'+str(append)+'.gif', mode='I') as writer:
      for filename in filenames:
        plot(filename, unit, plot_directory)
        image = imageio.imread(plot_directory+filename+"_"+str(append)+".png")
        writer.append_data(image)


if __name__ == "__main__":
  #plot("humidity-5-JUL-2017","Relative Humidity")
  #plot("temperature-5-JUL-2017","Temperature deg C")
  files = ["humidity-3-JUL-2017",
           "humidity-4-JUL-2017",
           "humidity-5-JUL-2017"]
  makeGif(files,"humidity","Relative Humidity")






