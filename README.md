# thunktemp
Python daemon for sensor temperature smoothing to work with thinkfan

Reads sensors from for ex. hwmon paths every X seconds, keeping a running list of N interval and writes to /shm/thinktemp the median value. 
This file can be used as source for thinkfan sensors input for a nice smooth fan progression.
Sample thinkfan config provided in thinkfan directory
Sample systemd service in sysd directory
