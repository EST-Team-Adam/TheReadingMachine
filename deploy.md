# Deploy the Project to AWS

## Set up Docker image

### Build Docker image

The image can be built by

```
sudo docker build -t thereadingmachine/thereadingmachine:<tag> .
```

The `-t` tag specifies the tag. Please specify the `<tag>` for each build.

### Upload the image to Docker hub

In order to upload the image, we need to perform authentication.

```
sudo docker login
```

Then we can upload the image with

```
sudo docker push thereadingmachine/thereadingmachine:<tag>
```

You can view the repo on [Docker Hub](https://hub.docker.com/r/thereadingmachine/thereadingmachine/)


## Deployment

### Launch EC2 and Docker on AWS

Follow this
[tutorial](https://www.ybrikman.com/writing/2015/11/11/running-docker-aws-ground-up/)
to manually launch an instance and setup Docker.


### Launch `The Reading Machine`

`ssh` to the instance.

```
ssh -i <location_of_pem_file> ec2-user@<instance_endpoint>
```

Once in the instance, the reading machine can be launched via:

```
sudo docker run -d -p 80:8080 thereadingmachine/thereadingmachine:<tag> --storage-opt dm.basesize=20G
```

The storage option is required, otherwise the container will run out of memory.

Navigate to the endpoint and we will now have access to the `Airflow` dashboard.
