import pyautogui as pag
import requests as req
import PIL as pil
import base64 as b64
from datetime import datetime
from threading import Thread
import socket
import json
import io


cfg = {
    'sockServer1': '46.0.130.94:50000',
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
}

typesDict = {
    'info': cfg['cmdInfoChannel'],
    'out': cfg['cmdOutChannel'],
    'post': cfg['cmdPostChannel']
}

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

cacheSize=1024
host = ''
port = input('Port: (Leave empty for 50000) ')
port = int(port) if port.isdigit() else 50000

S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.bind((host, port))
print(f"Bound to {host} with port {port}")
S.listen(5)

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
    def send(self, msg):
        self.s.sendall(msg.encode('utf-8'))

def bigRCV(cache=4096):
    pass

def sendById(id, msg):
    Client.instances[id].send(msg)

def listen(client):
    while client.active:
        try:
            data = client.s.recv(cacheSize).decode('utf-8')
            print(data)
            if (type(data) == type(str())) and ((data[0]== '{' and data[-1]== '}')or(data[1]== '{' and data[-2]== '}')):
                print('Recognised json ',end='')
                data=json.loads(data)
                print(data)
                if 'manifest' not in data: print('Not a valid json');continue
                if data['header']=='clientManifest':
                    obj=json.loads(data['data'])
                    client.role=obj['role']
                elif data['header']=='msg':
                    print(data['data'])
                    post('info','Msg received',data['data'])
                elif data['header']=='cmd':
                    cmd = data['data'].split('>')
                elif data['header']=='getImg':
                    pass #ask client to send image and prepare for receiving


            #client.send(data)
        except ConnectionResetError:
            client.active=False
            client.s.close()
            print(f'Lost connection to client ID {client.id} @{client.ip}')
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
while True: exec(input('Exec: '))