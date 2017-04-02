import time
import sys
import pigpio

PIN_OUT = 15

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: servo.py [u/l] [u/l] (first is action, second is current state"
    assert sys.argv[1] == 'u' or sys.argv[1] == 'l', "Enter a valid option."
    assert sys.argv[2] == 'u' or sys.argv[2] == 'l', "Enter a valid option."
    if sys.argv[1] == sys.argv[2]:
        sys.exit("State already matches action.")
    pi = pigpio.pi()
    if not pi.connected:
        sys.exit()
    if sys.argv[1] == 'u':
        pi.set_servo_pulsewidth(PIN_OUT,1200)
    elif sys.argv[1] == 'l':
        pi.set_servo_pulsewidth(PIN_OUT,2100)
    time.sleep(1)
    pi.set_servo_pulsewidth(PIN_OUT,0)
    pi.stop();
