#test for optimisation
from flask import Flask, render_template, Response
import paho.mqtt.client as mqtt
import cv2
import numpy as np
import time
from suntime import Sun, SunTimeException
import datetime
import pytz

app = Flask(__name__)

##############gun batimi gor##################
pst = pytz.timezone('Asia/Istanbul')
tnow = pst.localize(datetime.datetime.now())

lat = 41.17 ; lon = 28 # one particular place
sun = Sun(lat, lon)

# Get today's sunrise and sunset in local time
today_sr = (sun.get_local_sunrise_time() )
today_ss = (sun.get_local_sunset_time() )
#print (("Saat:"), tnow.strftime("%Y-%m-%d %H:%M:%S"))
if (today_sr < tnow) and (tnow < today_ss):
  print("Gunes tepede")
else:
  print("Gun batti")
##############gun batimi gor##################

########MQTT Iletisim protokolu##################
broker ="XXX.XXX.XX.XXX"
port = XXXX

client = mqtt.Client("Temperature_Inside")
client.connect(broker, port)
################################################

cap = cv2.VideoCapture('http://XXX.XXX.XX.XXX:XXXX')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
    while True:
        _, frame = cap.read()
        # hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # height, width, _ = frame.shape
        x = int(410)
        y = int(430)
        x2 = int(162)
        y2 = int(190)

        ##################################
        roiColor = frame[x:y, x2:y2]
        blcolor = (0, 0, 255)
        ##################################

        cx = int(162)
        cy = int(410)
        cxx = int(190)
        cyy = int(430)

        blcolor = (255, 0, 0)
        alan = cv2.rectangle(frame, (x2, x), (y2, y), blcolor)

        ################################renk ortalaması için gerekli################################################
        src_img = roiColor
        average_color_row = np.average(src_img, axis=0)
        average_color = np.average(average_color_row, axis=0)
        # print("d1", average_color)

        d_img = np.ones((312, 312, 3), dtype=np.uint8)
        d_img[:, :] = average_color
        npa = np.median(average_color)
        averaj = round(npa)
        print(averaj)
        # print(time.daylight)
        client.publish("averaj", averaj)
        cv2.imshow('Average Color', d_img)
        ################################################################################
        ############# time modülü ile zaman kontrolü yapılır. Gündüz ise aşağıdaki kod çalışır. #############
        if (tnow) < today_ss:
            # gunduz
            if averaj > 149:
                mama = "mama yetersiz"
                client.publish("mama", mama)
                cv2.putText(frame, mama, (cx - 150, 70), 0, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Gunduz zamani algilandi.", (10, 580), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
                cv2.rectangle(frame, (cx - 4, cy - 6), (cxx + 5, cyy + 5), (0, 0, 255), 2)
                cv2.putText(frame, mama, (cx, cy - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            elif averaj < 150:
                mama2 = "mama var"
                client.publish("mama", mama2)
                # print("Vega mama durumu " + str(mama2) + " baslik ile yayinda")
                cv2.putText(frame, mama2, (cx - 150, 70), 0, 0.5, (0, 255, 0), 1)
                cv2.putText(frame, "Gunduz zamani algilandi.", (10, 580), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
                cv2.rectangle(frame, (cx - 4, cy - 6), (cxx + 5, cyy + 5), (0, 255, 0), 2)
                cv2.putText(frame, mama2, (cx, cy - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)
        if (tnow) > today_ss:
            # gece
            if averaj > 150:
                mama = "mama yetersiz"
                client.publish("mama", mama)
                cv2.putText(frame, mama, (cx - 150, 70), 0, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Aksam zamani algilandi.", (10, 580), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
                cv2.rectangle(frame, (cx - 4, cy - 6), (cxx + 5, cyy + 5), (0, 0, 255), 2)
                cv2.putText(frame, mama, (cx, cy - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            elif averaj < 149:
                mama2 = "mama var"
                client.publish("mama", mama2)
                cv2.putText(frame, mama2, (cx - 150, 70), 0, 0.5, (0, 255, 0), 1)
                cv2.putText(frame, "Aksam zamani algilandi.", (10, 580), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
                cv2.rectangle(frame, (cx - 4, cy - 6), (cxx + 5, cyy + 5), (0, 255, 0), 2)
                cv2.putText(frame, mama2, (cx, cy - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)
        ############################################################################################################

        cv2.imshow("Frame", frame)
        # cv2.imshow('deneme', alan2)
        cv2.imshow('deneme2', roiColor)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        c = cv2.waitKey(10)
        if c == 27:
            break


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host="XXX.XXX.X.XX", port=XXXX, debug=True)
