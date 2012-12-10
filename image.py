#!/usr/bin/python2

import os
import pygame
import pycurl
import StringIO
import time
import signal
import logging
import RPi.GPIO as GPIO

WEBCAM_URL = 'http://user:password@10.13.37.128/snapshot.cgi'


class ImageViewer(object):
    def __init__(self):
        self._running = False
        self._image_surf = None
        self._screen = None
        self._setup_logger()
        self._connection_problem = False

    def _setup_logger(self):
        self._logger = logging.getLogger('image')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self._logger.addHandler(ch)
        self._logger.setLevel(logging.DEBUG)


    def fast_capture(self, *args, **kwargs):
        self._wait_time = 0
        #Turn on the screen:
        GPIO.output(11, GPIO.HIGH)
        self._logger.debug("FAST image capture enabled.")

    def slow_capture(self, *args, **kwargs):
        self._wait_time = 5
        # Turn off the screen:
        GPIO.output(11, GPIO.LOW)
        self._logger.debug("SLOW image capture enabled.")

    def setup_screen(self):
        drivers = ['fbcon', 'directfb', 'svgalib']

        found = False
        for driver in drivers:
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print 'Driver: {0} failed.'.format(driver)
                continue
            found = True
            break
        pygame.mouse.set_visible(False)

        if not found:
           raise Exception('No suitable video driver found!')

        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

        return screen

    def on_init(self):
        pygame.font.init()

        self._screen = self.setup_screen()

        # Font rendering:
        self._timestamp_font = pygame.font.SysFont("dejavusansmono", 15)

        # Curl
        self._curl = pycurl.Curl()
        self._curl.setopt(self._curl.URL, WEBCAM_URL)
        self._curl.setopt(pycurl.CONNECTTIMEOUT, 2)
        self._curl.setopt(pycurl.TIMEOUT, 2)
        self._curl.setopt(pycurl.NOSIGNAL, 1)

        # Raspberry Pi GPIO:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.OUT)
        self.slow_capture()
        
        self._running = True

    def on_event(self, event):
        if event.type == "QUIT":
            self._running = False

    def on_loop(self):
        self._image = StringIO.StringIO()
        self._curl.setopt(self._curl.WRITEFUNCTION, self._image.write)

        try:
            self._curl.perform()
        except Exception, e:
            #Problem fetching the image
            self._logger.error("Problem fetching image: %s" % e)
            self._connection_problem = True
            #Try again in a few seconds:
            time.sleep(5)
            return
        else:
            if self._connection_problem:
                self._connection_problem = False
                self._logger.info("Connection problem resolved, contining capture")
                
        self._image.seek(0)
        self._image_surf = pygame.image.load(self._image, "cam1.jpg").convert()
        time.sleep(self._wait_time)

    def on_render(self):
        self._screen.fill((0,0,0))
        if self._connection_problem:
            self._screen.fill((255,0,0))
        else:
            self._screen.blit(self._image_surf,(0,0))
            
        timestamp = self._timestamp_font.render(time.ctime(), True, (255,255,255))
        self._screen.blit(timestamp, (0,0))

        pygame.display.flip()
 
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 

if __name__ == "__main__":
    app = ImageViewer()

    #Setup signals to control the speed of image capture:
    # 20 - slow
    # 21 - fast
    signal.signal(20, app.slow_capture)
    signal.signal(21, app.fast_capture)
    
    app.on_execute()
