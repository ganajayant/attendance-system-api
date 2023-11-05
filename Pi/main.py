import io
import time

import picamera
import pygame
import requests
import RPi.GPIO as GPIO

# Define constants for pin numbers
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GREEN_LED_PIN = 17
RED_LED_PIN = 27

# Define constants for distances
MIN_DISTANCE = 30
MAX_DISTANCE = 100

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(RED_LED_PIN, GPIO.OUT)

# Initialize pygame mixer
pygame.mixer.init()


def setup_camera():
    camera = picamera.PiCamera()
    camera.resolution = (1024, 768)
    return camera


def measure_distance():
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
    # Multiply with the sonic speed (34300 cm/s) and divide by 2 (there and back)
    distance = (TimeElapsed * 34300) / 2
    return distance


def capture_and_send_image():
    stream = io.BytesIO()
    with setup_camera() as camera:
        camera.start_preview()
        camera.capture(stream, format='jpeg')
    stream.seek(0)
    return stream


def main():
    try:
        while True:
            dist = measure_distance()
            if MIN_DISTANCE < dist < MAX_DISTANCE:
                print(f"Distance: {dist:.1f} cm")
                stream = capture_and_send_image()
                response = requests.post(
                    'http://192.168.114.188:5000/attendance', files={'file': stream})
                if response.status_code == 200:
                    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
                    pygame.mixer.music.load("present.wav")
                else:
                    GPIO.output(RED_LED_PIN, GPIO.HIGH)
                    pygame.mixer.music.load("tryagain.wav")

                pygame.mixer.music.play()
                time.sleep(2)
                GPIO.output(GREEN_LED_PIN, GPIO.LOW)
                GPIO.output(RED_LED_PIN, GPIO.LOW)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
    finally:
        GPIO.cleanup()


if __name__ == '__main':
    main()
