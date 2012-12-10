RaspberryPi-IP-Camera-Viewer
============================

This is an remote IP camera viewer for the raspberry pi. The raspberry
pi is connected to a cheap automobile backup camera display via
composite video. Pygame displays the image stream from the camera on
the display. RPi.GPIO controls the VCC input of the display to turn on
the camera when this script receives a system signal.

This is intended to be run alongside the Motion package
(http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome). When Motion
detects movement on the camera it sends a signal to this script to
turn on the display and to turn up the fps of the image stream. Once
the Motion event is over another signal is sent to this script to turn
the screen back off and to decrease the fps of the image stream.

This script is written by Ryan McGuire. I don't make any IP claims on
this script, you can use it however you wish. It is public domain or
MIT licenced, your choice.

Usage:

1. Physically hookup the raspberry pi to the display, wire the VCC
cable to pin number 11 on the GPIO header of the raspberry pi (this
is so the script can automatically turn on the display.)
 
1. Configure the WEBCAM_URL below to use the right URL for your IP
camera.

1. Run:  python2 image.py

1. Configure Motion to send the signal to the script when it detects
movement (see motion.conf)

 -OR-

1. If you want to turn on the display manually you can send the
signal manually:


       pkill --signal 21 -f "python2 image.py"    # Turns the display ON
       pkill --signal 20 -f "python2 image.py"    # Turns the display OFF

