#!/bin/bash
cd ~/Documents/Jessamy
git pull origin main
source jessamy-tts-env/bin/activate
python launch_gui.py

