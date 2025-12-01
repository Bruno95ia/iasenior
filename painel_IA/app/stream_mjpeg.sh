#!/bin/bash

# Converte RTSP para MJPEG acessível via http://localhost:8888/mjpeg
ffmpeg -re -i rtsp://localhost:8554/ia -f mjpeg -q:v 5 -r 20 http://localhost:8888/mjpeg/fall.mjpg
