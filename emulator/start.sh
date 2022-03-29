#!/bin/bash

emulator -avd em -no-audio -no-boot-anim -no-window -accel on -gpu off -skin 1440x2880 &
appium --relaxed-security &

wait -n