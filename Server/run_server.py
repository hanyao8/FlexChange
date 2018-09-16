import datetime
import requests

import threading

def printit():
    threading.Timer(5.0, printit).start()
    print("Hello, World!")
#printit()

def pingit():
    url='http://127.0.0.1:5000/'
    threading.Timer(5.0,pingit).start()
    resp=requests.get(url)
    print(resp.text)


if __name__=='__main__':
    pingit()

