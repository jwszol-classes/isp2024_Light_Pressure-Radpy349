import numpy as np
import matplotlib.pyplot as plt
import json
import matplotlib.dates
import boto3
from datetime import datetime

s3 = boto3.resource('s3')
obj = s3.Object("iotstorage180281", "fajny_slownik.json")
slownik = obj.get()['Body'].read()
data = json.loads(slownik)

lights = []
pressures = []
timestamps = []

for x in data["day: 5"]:
    light = x['light']
    pressure = x['pressure']
    date = x['timestamp']
    timestamps.append(date)
    lights.append(light)
    pressures.append(pressure)

dates=[]
for i in timestamps:
    dates.append(datetime(i[0],i[1],i[2],i[4],i[5],i[6]))

times = matplotlib.dates.date2num(dates)
dates=np.array(dates)
data = np.array([lights,pressures])
print("średnia jasność:", np.mean(data[0]))
print("średnie ciśnienie:", np.mean(data[1]))
korelacja = np.corrcoef(data[1], data[0])[0, 1]

print(f"Korelacja między ciśnieniem a jasnością: {korelacja}")
plt.plot_date(times, lights)
plt.show()
plt.plot_date(times, pressures)
plt.show()