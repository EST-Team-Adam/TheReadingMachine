#!/bin/bash

rootDir=$(pwd)
dockerRepo="thereadingmachine"
appName="thereadingmachine"
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

sudo docker build -t $dockerRepo/$appName:$GIT_BRANCH .
sudo docker push $dockerRepo/$appName:$GIT_BRANCH
