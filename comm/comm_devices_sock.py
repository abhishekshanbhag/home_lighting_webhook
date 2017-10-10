import serial

from datetime import datetime
import json
import socket


with open('input.json') as doc:
    data = json.load(doc)
    U_ID = int(data['u_id'], 16)

ser = serial.Serial('/dev/tty.usbserial-A601D97W')

HOST = "192.168.1.147"
PORT = 40020

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(1)

conn, addr = s.accept()
print("Connected by",addr, conn)


def get_params(command):
    params = [command[0]]
    part = ""
    start = 0
    for i in command[1:]:
        if(i == " "):
            if(start == 0):
                start = 1
            else:
                params.append(part)
                part = ""
        else:
            part += i
    params.append(part)
    print(params)
    return params


def connect(mode, params):
    dev_id = hex(int(params[0]))
    ser.write(bytes.fromhex('7e'))
    ser.write(mode.encode())
    for i in range(0,12):
        uid_byte = hex((U_ID >> 8*i) & 0xff)
        try:
            ser.write(bytes.fromhex(uid_byte[2:]))
        except:
            ser.write(bytes.fromhex('0'+uid_byte[2:]))
    curr = datetime.now().second
    while(ser.in_waiting == 0 and datetime.now().second < (curr + 3)):
        pass
    if(ser.in_waiting == 0):
        ser.write(bytes.fromhex('00'))
        print("No device visible")
        mesg = b"No new device is visible"
        conn.send(mesg)
    else:
        len = int(ser.read().decode())
        while(ser.in_waiting < len):
            pass
        ack = (ser.read()).decode()
        if(ack == 'C'):
            try:
                #print(dev_id)
                ser.write(bytes.fromhex(dev_id[2:]))
                #print(bytes.fromhex(dev_id[2:]))
            except:
                #print("Reached here")
                ser.write(bytes.fromhex('0'+dev_id[2:]))
                #print(bytes.fromhex('0'+dev_id[2:]))
                mesg = "The device has been connects as device" + params[0]
            conn.send(mesg.encode())
    ser.flush()

def light(mode, params):
    dev_id = hex(int(params[0]))
    color = hex(int(params[1]))
    state = hex(int(params[2]))
    ser.write(bytes.fromhex('7e'))
    ser.write(mode.encode())
    for i in range(0,12):
        uid_byte = hex((U_ID >> 8*i) & 0xff)
        try:
            ser.write(bytes.fromhex(uid_byte[2:]))
        except:
            ser.write(bytes.fromhex('0'+uid_byte[2:]))
    try:
        ser.write(bytes.fromhex(dev_id[2:]))
    except:
        ser.write(bytes.fromhex('0'+dev_id[2:]))
    try:
        ser.write(bytes.fromhex(color[2:]))
    except:
        ser.write(bytes.fromhex('0'+color[2:]))
    try:
        ser.write(bytes.fromhex(state[2:]))
    except:
        ser.write(bytes.fromhex('0'+state[2:]))
    curr = datetime.now().second
    while(ser.in_waiting == 0 and datetime.now().second < (curr + 3)):
        pass
    if(ser.in_waiting == 0):
        print("Device",params[0],"disconnected.")
        mesg = "It appears that device " + params[0] + " has been disconnected."
        conn.send(mesg.encode())
    else:
        len = int(ser.read().decode())
        while(ser.in_waiting < len):
            pass
        ack = (ser.read()).decode()
        ser.flush()
        print("Success")
        mesg = "Here you go!"
        conn.send(mesg.encode())

def disconnect(mode, params):
    dev_id = hex(int(params[0]))
    ser.write(bytes.fromhex('7e'))
    ser.write(mode.encode())
    for i in range(0,12):
        uid_byte = hex((U_ID >> 8*i) & 0xff)
        try:
            ser.write(bytes.fromhex(uid_byte[2:]))
        except:
            ser.write(bytes.fromhex('0'+uid_byte[2:]))
    try:
        ser.write(bytes.fromhex(dev_id[2:]))
    except:
        ser.write(bytes.fromhex('0'+dev_id[2:]))
    curr = datetime.now().second
    while(ser.in_waiting == 0 and datetime.now().second < curr + 5):
        pass
    if(ser.in_waiting == 0):
        print("Device not found.")
        mesg = "I can't find this device."
        conn.send(mesg.encode())
    else:
        len = int((ser.read()).decode())
        while(ser.in_waiting < len):
            pass
        data = (ser.read()).decode()
        if(data == 'D'):
            print("Device",dev_id,"disconnected")
            mesg = "Device"+params[0]+"has been successfully disconnected"
            conn.send(mesg.encode())

def main():
    data = conn.recv(1024)
    if(data):
        print("Reached here")
        print(data.decode())
    while(True):
        data = conn.recv(1024)
        if(data):
            if(data == b"exit"):
                print(data.decode())
                break
            command = data.decode()
            print(command)
            params = get_params(command)
            print("Params:",params)
            mode = params[0]
            print("Mode: ", mode)
            if(mode == 'C'):
                connect(mode, params[1:])
            elif(mode == 'L'):
                light(mode, params[1:])
            elif(mode == 'D'):
                disconnect(mode, params[1:])
            else:
                print("Command not found")
    print("Exiting")
    conn.send(b"exit")
    conn.close()

if __name__ == '__main__':
    main()
