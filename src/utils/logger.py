import termcolor
from datetime import datetime

def log(text, color = None):
    time = datetime.now().time().strftime('%H:%M:%S')
    print(termcolor.colored(time + ": ", color=color) + str(text))

def error(text):
    log(text, "red")

def warn(text):
    log(text, "yellow")

def info(text):
    log(text, "cyan")