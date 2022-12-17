import requests as req
from PIL import Image as pilImage
import PIL as pil
import base64 as b64
from datetime import datetime
from threading import Thread
from random import randint
import websockets
import asyncio
import shutil
import socket
import json
import io
import os

pil.Image = pilImage

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

imgMetaExample = {
    'id': ...,
    'date': ...,
    'comment': ...
}
imgsMeta = {}

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

def threadrun(func, daemon=True, *args):
    thread = Thread(target=func, daemon=daemon, args=args)
    thread.start()

def getTime():
    now = datetime.now()
    return now.strftime('%d/%m/%Y (%w/7) %H:%M:%S')

def encodeIm(im):
    bytes = io.BytesIO()
    im.save(bytes, format='PNG')
    return b64.b64encode(bytes.getbuffer()).decode('ascii')

def decodeIm(s):
    return pil.Image.open(io.BytesIO(b64.b64decode(s.encode('ascii'))))


os.makedirs('rcv-files',exist_ok=True)
os.makedirs('processed',exist_ok=True)
print('RCV SERVER')
cacheSize=cfg['cacheSize']
imgChunk = cfg['imgChunkSize']
host = ''
port = input('Port: (Leave empty for 45001) ')
port = int(port) if port.isdigit() else 45001

sock = socket.socket()
sock.bind(('',port))
sock.listen(10)
print('Started...')

def processFile(filename):
    filepath = os.path.join('rcv-files',filename)
    if filepath.split('.')[-1] != 'invalid':
        with open(filepath,'rb') as f:
            data = f.read().decode('utf-8')
            img = decodeIm(data)
            #img.crop()
            img.save(os.path.join('processed', filename))
            img.close()

        if os.path.exists(os.path.join('web','py','preview.png')): os.remove(os.path.join('web','py','preview.png'))
        shutil.copy(os.path.join('processed', filename), os.path.join('web','py','preview.png'), follow_symlinks=True)
    #with open(filepath, 'rb') as f:
    #    data = f.read()
    #    s = data.decode('utf-8')
    #    obj = json.loads(s)
    #    print(f'Received screenshot-{obj["id"]} taken at {obj["date"]} with crop {obj["crop"]} and comment {obj["comment"]}')
    #    img = decodeIm(obj["img"])
    #    #img.crop()                <-----------
    #    img.save(os.path.join('processed', f'screenshot-{obj["id"]}.png'))
    #    img.close()
    #    with open(os.path.join('processed', f'screenshot-{obj["id"]}.data'),'w') as datafile:
    #        del obj['img']
    #        datafile.write(json.dumps(obj))


def receive(client):
    with client, client.makefile('rb') as clientfile:
        filename = clientfile.readline().strip().decode()
        if filename[:3]!='scr':
            print(f'False connection with first msg: {filename}')
            client.close()
            return
        length = int(clientfile.readline())
        print(f'Downloading {filename}:{length}...')
        path = os.path.join('rcv-files', filename)
        if os.path.isfile(path):
            print(f'{path} is taken, using ',end='')
            filename=filename[:-4] + f'_{randint(0,999)}' + filename[-4:]
            path = os.path.join('rcv-files', filename)
            print(f'{path}')
        with open(path, 'wb') as f:
            while length:
                chunk = min(length, imgChunk)
                data = clientfile.read(chunk)
                if not data: break; print('broke')
                f.write(data)
                length -= len(data)
        if length != 0:
            print('Invalid download.')
            os.rename(path, os.path.join('rcv-files', filename + '.invalid'))
        else:
            print('Done. Running processFile()')
            threadrun(processFile, True, filename)

with sock:
    while True:
        client,addr = sock.accept()
        print(f'Connection from {addr}')
        receive(client)
        #threadrun(receive, 1, client)