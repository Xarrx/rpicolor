# rpicolor
A web interface for controlling a RGB LED strip with a raspberry pi and Django.

## Requirements
...

## Setup [WIP]

*These instructions are mainly a documentation of what I have done in an attempt to get this project setup on my raspberry pi and should NOT be used by anyone...*

Update the raspberry pi's software:
```
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get autoremove -y
```

Make sure that python3 is installed:
```
python3 --version
```

Install venv:
```
sudo pip3 install virtualenv
```

Install pigpio:
```
wget https://github.com/joan2937/pigpio/archive/v74.zip
unzip v74.zip
cd pigpio-74
make
sudo make install
```

Install sqlite3 & libsqlite3-dev
```
sudo apt install sqlite3 libsqlite3-dev -y
```

Clone the repo and cd into to it:
```
git clone https://github.com/Xarrx/rpicolor.git
cd rpicolor
```

Create virtual environment and activate it:
```
virtualenv venv
source venv/bin/activate
```

Install django and pigpio to the virtual environment:
```
pip install django
pip install pigpio
```


