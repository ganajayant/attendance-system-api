import io
import time

import picamera
import requests
import RPi.GPIO as GPIO

GPIO_TRIGGER = 18
GPIO_ECHO = 24
GREEN_LED_PIN = 17
RED_LED_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(RED_LED_PIN, GPIO.OUT)


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
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    return distance


def capture_image():
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.start_preview()
        camera.capture(stream, format='jpeg')
    stream.seek(0)
    return stream


def send_attendance_request(stream):
    response = requests.post(
        'http://10.0.52.207:5000/attendance', files={'file': stream})
    return response


def optimize_code():
    try:
        while True:
            dist = measure_distance()
            print("Distance: %.1f cm" % dist)

            if 30 < dist < 100:
                image_stream = capture_image()
                response = send_attendance_request(image_stream)

                if response.status_code == 200:
                    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)  # Turn on green LED
                    GPIO.output(RED_LED_PIN, GPIO.LOW)  # Turn off red LED
                    time.sleep(2)
                else:
                    GPIO.output(GREEN_LED_PIN, GPIO.LOW)  # Turn off green LED
                    GPIO.output(RED_LED_PIN, GPIO.HIGH)  # Turn on red LED
                    time.sleep(2)

                GPIO.output(GREEN_LED_PIN, GPIO.LOW)
                GPIO.output(RED_LED_PIN, GPIO.LOW)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")

    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    optimize_code()
