import requests as req
import PIL as pil
import base64 as b64
from datetime import datetime
from threading import Thread
import websockets
import asyncio
import socket
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

class Client:
    instances=[]
    totalCons=0
    def __init__(self,socket,addr):
        Client.instances.append(self)
        Client.totalCons+=1
        self.s=socket
        self.id=Client.totalCons
        self.ip=addr[0]
        self.port=addr[1]
        self.role='undefined'
        self.active=True
        self.f=0
    def send(self, msg):
        self.s.sendall(msg.encode('utf-8'))

def sendById(id, msg):
    Client.instances[id].send(msg)

print('CMD SERVER')
cacheSize=cfg['cacheSize']
host = ''
port = input('Port: (Leave empty for 45000) ')
port = int(port) if port.isdigit() else 45000
S = socket.socket()
S.bind((host, port))
S.listen(5)


def listen(client):
    while client.active:
        try:
            data = client.s.recv(cacheSize).decode('utf-8')
            print(data)

        except ConnectionResetError:
            client.active=False
            client.s.close()
            print(f'Lost connection to client ID {client.id} @{client.ip}')
            post('info','-CON',f'Lost connection to client ID {client.id} @{client.ip}',3)
        except IndexError:
            client.f+=1
            print(f'Index error {client.f=}  ',end='')
            if client.f>3: print('Dropping client');client.active=False
            else: print('Ignoring')
        except KeyboardInterrupt: raise KeyboardInterrupt
        except Exception as e:
            print(f'Exception at listen: {e}')


def accept():
    while True:
        try:
            newC = S.accept()
            client=Client(newC[0],newC[1])
            print(f'New connection from {client.ip}, assigned ID {client.id}')
            threadrun(listen,True,client)
        except KeyboardInterrupt: raise KeyboardInterrupt
        except Exception as e:
            print(f'Exception at accept: {e}')
threadrun(accept)

cmdList = []
def ws():
    async def wsHandle(ws):
        global cmdList
        try:
            async for msg in ws:
                cmdList.append(msg)
                print(cmdList)
        except Exception as e:
            print(f'Exception@wsHandle: {e}')

    async def wsServer():
        async with websockets.serve(wsHandle,'',45002):
            await asyncio.Future()
    asyncio.run(wsServer())
threadrun(ws)

def cmdListHandle():
    global cmdList
    while True:
        try:
            if cmdList:
                cmd = cmdList.pop()
                print(f'Received msg: {cmd}',end='')
                if len(cmd)<3: print('');continue
                elif cmd[:2]!='>>': print('');continue
                else:
                    print('   executing...')
                    split = cmd[2:].split('|')
                    print(split)
                    act = split[0]
                    if act=='screen':
                        sendById(-1,f'qscreen-{split[1]}')
                #post('info','CMD received',f'CMD: {cmd}', 1)
        except Exception as e:
            print(f'Error@cmdListHandle: {e}')
threadrun(cmdListHandle)


while True:
    s = input('Cmd: ')
    try:
        exec(s)
    except Exception as e:
        print(f'Exception: {e}')









