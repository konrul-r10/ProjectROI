from flask import Flask, render_template, Response
import cv2
import numpy as np

app = Flask(__name__)

cap = cv2.VideoCapture('http://xxx.xxx.xxx.xxx:xxxx')  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = cap.read()  # read the camera frame
        if not success:
            break
        else:
            while True:
                ret, frame = cap.read()

                if ret == False:
                    break

                frame = cv2.resize(frame, (1024, 768))

                # Extract required section from entire frame
                # roiColor = cv2.rectangle(frame.copy(), (280, 505), (230, 535), (255, 255, 255), 2)  # For SampleTL.mp4
                roiColor = frame[500:550, 210:300]

                blcolor = (255, 0, 0)
                cv2.rectangle(frame, (280, 505), (230, 535), blcolor)

                hsv = cv2.cvtColor(roiColor, cv2.COLOR_BGR2HSV)

                # red
                lower_hsv_red = np.array([5, 20, 10])
                upper_hsv_red = np.array([20, 60, 255])
                mask_red = cv2.inRange(hsv, lowerb=lower_hsv_red, upperb=upper_hsv_red)
                red_blur = cv2.medianBlur(mask_red, 5)

                # green
                lower_hsv_green = np.array([49, 79, 137])
                upper_hsv_green = np.array([90, 255, 255])
                mask_green = cv2.inRange(hsv, lowerb=lower_hsv_green, upperb=upper_hsv_green)
                green_blur = cv2.medianBlur(mask_green, 7)

                lower_hsv_yellow = np.array([15, 150, 150])
                upper_hsv_yellow = np.array([35, 255, 255])
                mask_yellow = cv2.inRange(hsv, lowerb=lower_hsv_yellow, upperb=upper_hsv_yellow)
                yellow_blur = cv2.medianBlur(mask_yellow, 7)

                # Because the image is a binary image, If the image has a white point, which is 255, then take his maximum max value 255
                red_color = np.max(red_blur)
                green_color = np.max(green_blur)
                yellow_color = np.max(yellow_blur)

                if red_color == 255:
                    # print('Mama var')
                    cv2.rectangle(frame, (280, 505), (230, 535), (0, 0, 255),
                                  2)  # Draw a rectangular frame by coordinates
                    cv2.putText(frame, "Mama Var", (280, 495), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255),
                                1)  # red text information

                elif green_color == 255:
                    # print('green')
                    cv2.rectangle(frame, (280, 505), (230, 535), (0, 0, 255), 2)
                    cv2.putText(frame, "green", (280, 495), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

                elif yellow_color == 255:
                    # print('yellow')
                    cv2.rectangle(frame, (280, 505), (230, 535), (0, 0, 255), 2)
                    cv2.putText(frame, "yellow", (280, 495), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 2)

                cv2.imshow('frame', frame)
                red_blur = cv2.resize(red_blur, (300, 200))
                green_blur = cv2.resize(green_blur, (300, 200))
                yellow_blur = cv2.resize(yellow_blur, (300, 200))

                cv2.imshow('red_window', red_blur)
                cv2.imshow('green_window', green_blur)
                cv2.imshow('yellow_window', yellow_blur)
                cv2.imshow('deneme', hsv)
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
    app.run(debug=True)