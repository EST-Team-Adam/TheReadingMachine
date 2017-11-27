#!/bin/bash

dockerRepo="thereadingmachine"
appName="thereadingmachine"

read -p "Enter a version number to build Docker [latest/dev/]: "\
     dockerVersion
if [ "$dockerVersion" = "" ];
then
    dockerVersion="latest"
fi

sudo docker build -t $dockerRepo/$appName:$dockerVersion .

sudo docker push $dockerRepo/$appName:$dockerVersion
