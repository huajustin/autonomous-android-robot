# Autonomous Android Line Tracking Robot

## Overview
This was a project that I worked on with a group to develop a robot that could track and follow a given black line. Using optical sensors to feed information to a PID controller designed by our teammates, this robot was able to successfully manuever through given test courses containing obstacles such as intersections and gaps in the track. Additional features were included such as outputting a video feed to an LCD screen as well as the ability to manually control the robot through an Android or web app.

## Technology
The main piece of hardware that was used to control all the motors was a Raspberry Pi with an Adafruit DC and Stepper Motor HAT. The Raspberry Pi ran on an operating system based off of Debian called Raspbian (now known as "Raspberry Pi OS"), providing a Linux environment for the development of our software controlling the robot. The majority of the software responsible for controlling the robot and interacting with the hardware was written in Python using CircuitPython. For the manual control feature, the Android app was developed in Java using Android Studio. 

## Design
My main roles in this project were developing the Android app responsible for manual control as well as the services on the Raspberry Pi to support this. In addition, I developed the basic functions to control the motors and perform basic movements.

From a high-level, the Android app works by looking for nearby Bluetooth devices on startup and connecting to the Pi. The app performs this through creating a new thread that communicates with the Pi. On-touch event listeners are added to buttons on the app, which sends an output stream of bytes correspponding to different movement commands through the created thread. 

On the Raspberry Pi side, a Bluetooth socket is opened and blocks until a connection is formed with the app. It then enters a loop that receives the byte stream and performs movement commands based on the byte encoding (e.g. receiving "0x02" issues a move forward command). This connection is closed when the app has sent an exit signal or disconnects unexpectedly. 

## Takeaways
This project was super interesting and gave me experience working with microcontrollers and writing mobile applications and servers using Bluetooth communication. It also gave me the opportunity to actually wire and solder some of the components myself, as well as trying to debug said wiring when our LCD screen would not light up (because some of the wires were connected to the wrong pins). I learned a lot from this, and there are a few things that I would have liked to implement given a larger time constraint:
 
* Live video feed in the Android app from the robot's connected camera
* Ability to switch modes (autonomous tracking vs manual movement) within the Android app
* More robust code while establishing the Bluetooth connection (possibly allowing the user to specify which Pi to connect to versus hardcoding and automatically connecting to the first Pi)



