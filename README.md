# rpicolor
Web interface for controlling a RGB LED strip with a raspberry pi and Django.

## Setup [WIP]

*These instructions are mainly a documentation of what I have done in an attempt to get this project setup on my raspberry pi and should NOT be used by anyone...*

##### Update the raspberry pi's software:
```
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get autoremove -y
```

##### Ensure python3 is installed:
```
python3 --version
```

##### Install venv:
```
sudo pip3 install virtualenv
```

##### Install pigpio:
```
wget https://github.com/joan2937/pigpio/archive/v74.zip
unzip v74.zip
cd pigpio-74
make
sudo make install
```

