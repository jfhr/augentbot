from sys import stdout
from time import sleep

# thanks to https://stackoverflow.com/a/5291044/8583511


def print_sleep(seconds: int, length: int = 3, prompt: str = 'Sleeping') -> None:
    while True:
        for i in range(length):
            print(prompt + "." * i)
            stdout.write("\033[F") # Cursor up one line
            stdout.write("\033[K") # Clear line

            sleep(1)
            seconds -= 1

            if seconds <= 0: return
