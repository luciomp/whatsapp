
# FROM node:17-buster-slim
# FROM ubuntu:22.04
FROM openjdk:8
RUN apt update
RUN apt install -y libx11-6
RUN wget 'https://dl.google.com/android/repository/sdk-tools-linux-4333796.zip' -P /tmp 
RUN unzip -d /opt/android /tmp/sdk-tools-linux-4333796.zip
RUN yes Y | /opt/android/tools/bin/sdkmanager --install "platform-tools" 
RUN yes Y | /opt/android/tools/bin/sdkmanager --install "system-images;android-28;google_apis;x86"
RUN yes Y | /opt/android/tools/bin/sdkmanager --install "platforms;android-28"
RUN yes Y | /opt/android/tools/bin/sdkmanager --install "build-tools;28.0.3"
RUN yes Y | /opt/android/tools/bin/sdkmanager --install "emulator"
RUN yes Y | /opt/android/tools/bin/sdkmanager --licenses
RUN /opt/android/tools/bin/avdmanager --verbose create avd --force --name "em" --device "pixel" --package "system-images;android-28;google_apis;x86" --tag "google_apis" --abi "x86"
RUN echo "export ANDROID_HOME=/opt/android" >> ~/.bashrc
RUN echo "export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools" >> ~/.bashrc
# RUN apt install -u openjdk-18-jdk
# RUN npm install -g appium
# CMD ["appium", "--relaxed-security"]
WORKDIR /app
COPY start.sh /app
CMD ["bash"]
# EXPOSE 4723