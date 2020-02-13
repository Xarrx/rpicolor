# rpicolor
Web interface for controlling a RGB LED strip with a raspberry pi and Django.

## Setup [WIP]

*These instructions are mainly a documentation of what I have done in an attempt to get this project setup on my raspberry pi and should NOT be used by anyone...*

#### Update the raspberry pi's software:
```
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get autoremove -y
```

#### Ensure python3 is installed:
```
python3 --version
```

#### Install venv:
```
sudo pip3 install virtualenv
```

#### Install pigpio:
```
wget https://github.com/joan2937/pigpio/archive/v74.zip
unzip v74.zip
cd pigpio-74
make
sudo make install
```

#### Install sqlite3 & libsqlite3-dev
```
sudo apt install sqlite3 libsqlite3-dev -y
```

#### Create directory and change to it:
```
mkdir pcs
cd pcs
```

#### Create virtual environment and activate it:
```
virtualenv venv
source venv/bin/activate
```

#### Install django and pigpio to the virtual environment:
```
pip install django
pip install pigpio
```

#### Clone the repo
```
git clone https://github.com/Xarrx/rpicolor.git
```

#### Create a new django start project:
```
django-admin.py startproject pcs
```

#### Move the newly created project files into the cloned repo folder and delete the empty folder:
```
mv pcs/manage.py rpicolor/manage.py
mv pcs/pcs rpicolor/pcs
rm -r pcs/pcs
```
