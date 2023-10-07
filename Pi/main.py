import io
import time

import picamera
import pygame
import requests
import RPi.GPIO as GPIO

pygame.mixer.init()

GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 18
GPIO_ECHO = 24

GREEN_LED_PIN = 17
RED_LED_PIN = 27

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

GPIO.setmode(GPIO.BCM)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(RED_LED_PIN, GPIO.OUT)


def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    if distance > 30 and distance < 100:
        print("Distance: %.1f cm" % distance)
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            camera.resolution = (1024, 768)
            camera.start_preview()
            camera.capture(stream, format='jpeg')
        stream.seek(0)
        response = requests.post(
            'http://192.168.114.188:5000/attendance', files={'file': stream})
        if response.status_code == 200:
            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)  # Turn on green LED
            GPIO.output(RED_LED_PIN, GPIO.LOW)  # Turn off red LED
            pygame.mixer.music.load("present.wav")
            pygame.mixer.music.play()
            time.sleep(2)
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            GPIO.output(RED_LED_PIN, GPIO.LOW)

        else:
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)  # Turn off green LED
            GPIO.output(RED_LED_PIN, GPIO.HIGH)  # Turn on red LED
            pygame.mixer.music.load("tryagain.wav")
            pygame.mixer.music.play()
            time.sleep(2)
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            GPIO.output(RED_LED_PIN, GPIO.LOW)

    return distance


if __name__ == '__main__':
    try:
        while True:
            distance()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
