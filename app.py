from flask import Flask, render_template, Response
import cv2
import torch

app = Flask(__name__)

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)


cap = cv2.VideoCapture(0)

@app.route('/')
def video_show():
    return render_template('index.html')

def gen_frames():
    while True:
        _, frame = cap.read()
        if not _:
            break
        else:
            results = model(frame)
            annotated_frame = results.render()
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)