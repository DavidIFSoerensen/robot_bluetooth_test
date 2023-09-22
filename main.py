import cv2
from flask import Flask, Response
import serial

app = Flask(__name__)
computerSerial = serial.Serial('COM8')
robotSerial = serial.Serial('COM9')
video = cv2.VideoCapture(0)

def get_camera_feed():

    if not video.isOpened():
        print('Cannot open video feed')
        return
    
    while True:
        success, frame = video.read()  # read the camera frame
        if not success:
            print('Couldn\'t get frame from video.')
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def start_serial_input_output():
    print('Starting the serial input and receive loop')
    
    if not computerSerial.is_open:
        computerSerial.open()

    if not robotSerial.is_open:
        robotSerial.open()

    while True:
        received_bytes = computerSerial.readline()

        if not received_bytes:
            continue
        
        command = received_bytes.decode('utf-8').strip()

        print('Received data')
        print(command)

        if command is 'W' or 'S' or 'A' or 'D' or 'J' or 'K' or 'L' or 'I':
            command_to_be_sent = str.format('{0}{1}', command.encode('utf-8'),'\n')
            print('Sending data')
            print(command)
            robotSerial.write(command_to_be_sent)
            print('Data sent')

@app.get('/video')
def video_stream_endpoint():
    return Response(get_camera_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
