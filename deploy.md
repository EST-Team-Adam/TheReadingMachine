# Deploy the Project to AWS

## Set up Docker image

### Build Docker image

The `build.sh` script is available to build the image then push to
[Dockerhub](https://hub.docker.com/r/thereadingmachine/thereadingmachine/).

Otherwise, you can build it manually by following the instructions
below.

```
sudo docker build -t thereadingmachine/thereadingmachine:<tag> .
```

The `-t` tag specifies the tag. Please specify the `<tag>` for each
build.

### Upload the image to Docker hub

In order to upload the image, we need to perform authentication.

```
sudo docker login
```

Then we can upload the image with

```
sudo docker push thereadingmachine/thereadingmachine:<tag>
```

You can view the repo on [Docker
Hub](https://hub.docker.com/r/thereadingmachine/thereadingmachine/)


## Deployment

### Launch EC2 and Docker on AWS

Follow this
[tutorial](https://www.ybrikman.com/writing/2015/11/11/running-docker-aws-ground-up/)
to manually launch an instance and setup Docker.


Currently, the ideal instance size has not yet been determined,
further optimisation is required. However, there are two known changes
required for the deployment.

After launching and ssh into the instance, update and install Docker as per tutorial.


```
sudo yum update -y && sudo yum install -y docker && sudo service docker start && sudo usermod -a -G docker ec2-user && exit
```

#### Increase DB size.

Make sure to allocate at least 30GB of storage for the instance as
shown in the following screenshot.

![storage_setting](https://user-images.githubusercontent.com/1054320/39852588-73de211e-5471-11e8-8214-ea2e0cde2d68.png)

#### Expose ports

Both port 8080 and 5000 need to be exposed in order for the Airflow UI
and the dashboard to be accessible to the public.

![security_group](https://user-images.githubusercontent.com/1054320/39852635-aa825b9a-5471-11e8-8f6d-306064a33cbd.png)

The security group can be saved and thus can be loaded when
relaunching the instance.

### Deploy `The Reading Machine`

`ssh` to the instance.

```
ssh -i <location_of_pem_file> ec2-user@<instance_endpoint>
```

Once in the instance, the reading machine can be launched via:

```
sudo docker run -d -p 8080:8080 -p 5000:5000 thereadingmachine/thereadingmachine:<tag> --storage-opt dm.basesize=20G
```

The storage option is required, otherwise, the container will run out
of memory.

Navigate to the endpoint and we will now have access to the `Airflow`
dashboard.


## Clean up

Sometimes the Docker container can occupy too much of the disk space
and require clean up. This can be done with the following command on
the instance.

```
docker system prune -a -f
```

Please see the [community
forum](https://forums.docker.com/t/some-way-to-clean-up-identify-contents-of-var-lib-docker-overlay/30604/2)
for more information.
