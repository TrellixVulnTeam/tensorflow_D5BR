#!/home/pi/Projects/pyenv/ML/bin/python
import socket
import os, re, time, threading, subprocess, cv2
from detectionAPP_v3_noCAM import DetetionAPP 
from detectionAPP_v3_noCAM import Cap_background

model_dir = '/home/pi/Projects/py/ML/tensorflow/models'
cam_stop = False

class Capture_thread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.frame = None
        
    def run(self):
        global cam_stop
        frameGen = detetionAPP.camera_cap()
        while True:
            self.frame = frameGen.__next__()
            print('frame left', len(detetionAPP.camera.frame))
            if cam_stop == True:
                break

detetionAPP = DetetionAPP(model_dir)

class Camera_stream(threading.Thread):
    def __init__(self):
        super().__init__()
        
    def run(self):
        detetionAPP.camera.start()

camera_stream = Camera_stream()
camera_stream.start()

service_port = ('0.0.0.0', 9005)

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind(service_port)
print('socket established with {}'.format(service_port))

serv.listen()
print('Start listening')




while True:
    conn, addr = serv.accept()
    print('Client from', addr)

    while True:
        data = conn.recv(1024)
        data = data.decode('utf-8')
        print('Recieve data from client: ', data)

        if not data or data == '':
            break

        elif len(re.findall('GET /', data))>0 and len(re.findall('camera_on', data))>0:

            if detetionAPP.cam_status == True:
                res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"camera is already 'ON', no need to restart"
            else:
                # Try Turn camera capture on (time.sleep depands on capture speed)
                
                try:
                    cam_thread = Capture_thread()
                    cam_stop = False
                    cam_thread.start()
                    time.sleep(10) # this value depands, too small might casue mistaken respone of 'fail to turn camera on'
                except:
                    print('Error: Repeatly processing camera capture')

                if detetionAPP.cam_status == True:
                    res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"camera turned on"
                else:
                    res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"fail to turn camera on"

            res = res.encode('utf-8')
            conn.send(res)
            break

        elif len(re.findall('GET /', data))>0 and len(re.findall('camera_off', data))>0:

            cam_stop = True
            res = res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"Try to turn camera off" 
            print(res)              
            res = res.encode('utf-8')
            conn.send(res)
            detetionAPP.cam_status = False
            break

        else:
            res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"Argument incorrect: 1. Only support http 'GET'\n2.Either 'camera_on' or 'camera_off' "
            res = res.encode('utf-8')
            conn.send(res)
            break    
    
    conn.close()
    print('Client disconnected')
    
    