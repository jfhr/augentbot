from sys import stdout
from time import sleep

# thanks to https://stackoverflow.com/a/5291044/8583511

def print_sleep(seconds, length):
    while True:
        for i in range(length):
            print("Loading" + "." * i)
            stdout.write("\033[F") # Cursor up one line
            stdout.write("\033[K") # Clear line

            sleep(1)
            seconds -= 1

            if seconds <= 0: return
