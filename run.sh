#!/bin/sh
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.8
sudo apt-get install python3-pip
pip3 install -r requirements.txt
ENV="production"
python3 main.py