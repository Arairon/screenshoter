import pyautogui as pag
import requests as req
import PIL as pil
import base64 as b64
from datetime import datetime
from threading import Thread
from time import sleep
from random import randint
import socket
from sys import getsizeof
import json
import io

cfg = {
    'sockServerCmd': 'arairon.xyz:45000',
    'sockServerRcv': 'arairon.xyz:45001',
    'defaultPostServer': 'https://ntfy.sh/',
    'backupPostServer': 'http://ntfy.sh/',
    'cmdPostChannel': 'arai-ss-POST',
    'cmdOutChannel': 'arai-ss-OUT',
    'cmdInfoChannel': 'arai-ss-INFO',
    'autoCrop': False,  # Not yet implemented
    'cropValues': [0, 0, 0, 48],
    'cacheSize': 1024,
    'imgChunkSize': 100_000,
    'timeout': 5,
    'msgManifest': 'Arai\'s msg format v0.1',
    'clientManifest': '{"role":"screen"}',
}
typesDict = {
    'info': cfg['cmdInfoChannel'],
    'out': cfg['cmdOutChannel'],
    'post': cfg['cmdPostChannel']
}

def threadrun(func, daemon=True, *args):
    thread = Thread(target=func, daemon=daemon, args=args)
    thread.start()

def post(t='info', title='Error: No title given', msg='Error: No msg given', priority=1):
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

def getTime():
    now = datetime.now()
    return now.strftime('%d/%m/%Y (%w/7) %H:%M:%S')

def encodeIm(im):
    bytes = io.BytesIO()
    im.save(bytes, format='PNG')
    r = b64.b64encode(bytes.getbuffer()).decode('ascii')
    bytes.close()
    return r

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
        'crop': cfg['cropValues'],
        'comment': comment,
        'img': encoded}
    im.close()
    s = json.dumps(obj)
    imagesToSend.append(s)
    return s

def sendImage(img):
    chunk = cfg['imgChunkSize']
    sock = socket.socket()
    ip = cfg['sockServerRcv'].split(':')
    port = int(ip[1]);ip=ip[0]
    sock.connect((ip,port))
    bimg = io.BytesIO(img.encode('utf-8'))
    id=str(img[7:14].split(',')[0]).strip()
    with sock,bimg:
        sock.sendall(f'screenshot-{id}.a'.encode('utf-8')+b'\n')
        sock.sendall(f'{bimg.getbuffer().nbytes}'.encode('utf-8') + b'\n')
        while True:
            data = bimg.read(chunk)
            if not data: break
            sock.sendall(data)


def quickScreenshot(comment='QuickScreenshot'):
    screenshot(comment)
    sendImage(imagesToSend.pop())

S = socket.socket()
def reconnect():
    global S
    try: S.close();S=socket.socket()
    except:pass
    ip = cfg['sockServerCmd'].split(':')
    port = int(ip[1]);
    ip = ip[0]
    S.connect((ip, port))
    post('info', '+CON', 'Connected to cmd server',3)
reconnect()

def listen():
    global S
    while True:
        try:
            data = S.recv(cfg['cacheSize']).decode('utf-8').lower()
            data=data.split('-')
            if data[0]=='qscreen':
                quickScreenshot(' '.join(data[1:]))

        except ConnectionResetError:
            post('info','-CON','Lost connection to server', 3)
            reconnect()
        except Exception as e:
            post('info','Exception@listen',str(e))
#threadrun(listen)
listen()