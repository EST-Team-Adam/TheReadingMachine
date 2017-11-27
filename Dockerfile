# Use official python image
FROM python:2.7.12

# Set the file maintainer
MAINTAINER Michal C. J. Kao

# Set project home
ENV PROJECT_HOME=/app

# Copy the current directory contents into the container at /app
ADD . $PROJECT_HOME

# Change working directory
WORKDIR $PROJECT_HOME

# Run setup
RUN ./setup.sh

# Port to expose
EXPOSE 8080


# Start with entry script
ENTRYPOINT ./start_pipeline.sh

