FROM jenkins:latest
USER root
RUN apt-get update && apt-get install -y docker.io
USER jenkins
COPY plugins.txt /usr/share/jenkins/plugins.txt
RUN /usr/local/bin/plugins.sh /usr/share/jenkins/plugins.txt
