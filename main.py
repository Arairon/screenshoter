import pyautogui as pag
import requests as req
import PIL as pil
import base64 as b64
from datetime import datetime
from threading import Thread
from time import sleep
from random import randint
import socket
import json
import io

cfg = {
    'sockServer1': 'arairon.xyz:45000',
    'defaultPostServer': 'https://ntfy.sh/',
    'backupPostServer': 'http://ntfy.sh/',
    'cmdPostChannel': 'arai-ss-POST',
    'cmdOutChannel': 'arai-ss-OUT',
    'cmdInfoChannel': 'arai-ss-INFO',
    'autoCrop': False,  # Not yet implemented
    'cropValues': [0, 0, 0, 48],
    'cacheSize': 1024,
    'imgCacheSize':4096,
    'timeout': 5,
    'msgManifest': 'Arai\'s msg format v0.1',
    'clientManifest': '{"role":"screen"}',
}

typesDict = {
    'info': cfg['cmdInfoChannel'],
    'out': cfg['cmdOutChannel'],
    'post': cfg['cmdPostChannel']
}

S = None
def connect(host,port):
    global S
    try: S.close()
    except: pass
    S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    S.connect((host, int(port)))

def send(msg):
    global S
    try:
        S.sendall(msg.encode('utf-8'))
    except OSError: post('info','Error sending a msg', f'Sent a message through a non-socket object\nmsg: {msg}')

def fsend(header='msg',data='No data given'):
    obj = {
        'manifest': cfg['msgManifest'],
        'header': header,
        'data': data
    }
    send(json.dumps(obj))

def imgSend():
    global imagesToSend
    img = imagesToSend.pop()
    S.sendall(img.encode('utf-8'))

def listen():
    global S
    while True:
        try:
            data = S.recv(cfg['cacheSize']).decode('utf-8')
            print(data)
            if (type(data) == type(str())) and ((data[0]== '{' and data[-1]== '}')or(data[1]== '{' and data[-2]== '}')):
                print('Recognised json ', end='')
                data = json.loads(data)
                print(data)
                if 'msgManifest' not in data: print('Not a valid json');continue
        #except IndexError
        except ConnectionResetError:
            post('info','Lost connection','Lost connection to server')
            S.close();S=None;break
        except KeyboardInterrupt: raise KeyboardInterrupt
        except Exception as e:
            print(f'Exception@listen: {e}')


def threadrun(func, daemon=True, *args):
    thread = Thread(target=func, daemon=daemon, args=args)
    thread.start()


def post(t='info', title='Error: No topic given', msg='Error: No msg given', priority=1):
    t = t.lower().strip()
    channel = typesDict.get(t, cfg['cmdInfoChannel'])
    obj = {'topic': channel,
           'title': title,
           'message': msg,
           'priority': priority, }
    try:
        server = cfg['defaultPostServer']
        req.post(f'{server}', data=json.dumps(obj))
    except Exception as e:
        server = cfg['backupPostServer']
        post('info', f'Exception@send', f'{e}', 3)
        req.post(f'{server}', data=json.dumps(obj))
    #add recursion protection


def getTime():
    now = datetime.now()
    return now.strftime('%d/%m/%Y (%w/7) %H:%M:%S')


def encodeIm(im):
    bytes = io.BytesIO()
    im.save(bytes, format='PNG')
    return b64.b64encode(bytes.getbuffer()).decode('ascii')


def decodeIm(s):
    return pil.Image.open(io.BytesIO(b64.b64decode(s.encode('ascii'))))

imagesToSend=[]
def screenshot(comment='none'):
    global imagesToSend
    im = pag.screenshot()
    encoded = encodeIm(im)
    obj={
        'id': randint(0,100000),
        'date': getTime(),
        'comment': comment,
        'img': encoded,
        'thumbnail':None} #Add thumbnails
    im.close()
    s = json.dumps(obj)
    imagesToSend.append(s)
    return s

def connector():
    global S
    tempS = socket.socket()
    while True:
        if type(S) != type(tempS):
            try:
                host, port = cfg['sockServer1'].split(':')
                print(host, port)
                connect(host, port)
                threadrun(listen)
                post('info','Connection established',f'Successfully connected to {host}:{port}',1)
                fsend('clientManifest', cfg['clientManifest'])
            except Exception as e:
                post('info', 'Error connecting', f'Connection to {host}:{port} failed with E:{e}', 1)
                S=None
        sleep(cfg['timeout'])
    tempS.close()

threadrun(connector)


try:
    sleep(1)
except Exception as e:
    print(f'Exception: {e}')

while True:
    exec(input('Exec: '))