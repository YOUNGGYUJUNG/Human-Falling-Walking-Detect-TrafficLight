import serial
from flask import Flask, render_template, Response, send_file, request, jsonify, session, redirect, url_for, send_from_directory, flash
from flask_socketio import SocketIO
from flask_assets import Environment, Bundle
import cv2
import torch
import time
import logging
import firebase_admin
import asyncio
import threading

from firebase_admin import credentials, auth, db


app = Flask(__name__)
assets = Environment(app)

app.secret_key = '1hRTFZEPIPlVclJkOGIFt4kTY2e9Ae77'  # Flask 세션을 사용하기 위한 시크릿 키 설정

# Firebase 프로젝트 설정
cred = credentials.Certificate("C:/python/yolov5-master/static/silverlightDB.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://silverlight-d3108-default-rtdb.firebaseio.com'})

# 로그 파일의 경로와 이름 설정
log_file = 'detection.log'

# 로깅 설정
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(message)s')


# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/python/yolov5-master/best.pt')

socketio = SocketIO(app)

# 초기값 설정
status_message = '감지되지 않았습니다 (카메라 1).'

# 감지 통계 데이터
detection_data = []

# OpenCV의 VideoCapture 객체를 초기화
#cap = cv2.VideoCapture('http://172.16.4.178:8090/?action=stream/')
cap = cv2.VideoCapture(1)

# Realtime Database 초기화
root_ref = db.reference()

# 이벤트 카운터 초기화
event_counter = 0

# 지연을 제어하기 위한 변수 정의
delay_flag = threading.Event()

def get_user_info(uid):
    user_data = root_ref.child('users').child(uid).get()
    return user_data

@app.route('/')
def index():
    return render_template('index.html', status1=status_message)



@app.route('/stat')
def stats():
    return render_template('stat.html', status1=status_message)

@app.route('/status2')
def status2():
    return render_template('stat2.html', status1=status_message)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        employee_id = request.form['employee_id']
        name = request.form['name']
        department = request.form['department']
        birth = request.form['birth']
        position = request.form['position']

        try:
            # Firebase에 사용자 등록
            user = auth.create_user(email=email, password=password)

            # Realtime Database에 추가 정보 저장
            user_data = {
                'email': email,
                'employee_id': employee_id,
                'name': name,
                'department': department,
                'birth': birth,
                'position': position
            }
            root_ref.child('users').child(user.uid).set(user_data)

            flash('사용자가 성공적으로 등록되었습니다.', 'success')  # 사용자에게 등록 성공 메시지 플래시

            return redirect('/login')  # 로그인 페이지로 리다이렉트
        except Exception as e:
            flash(f'등록 중 오류가 발생했습니다. 오류 메시지: {str(e)}', 'error')  # 오류 메시지 플래시
            return render_template('signup.html')

    # GET 요청에 대한 처리
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Firebase에서 사용자 인증
            user = auth.get_user_by_email(email)

            # 사용자의 이메일과 비밀번호로 로그인
            auth.update_user(user.uid, password=password)

            # 사용자 정보를 세션에 저장
            session['user_id'] = user.uid

            return redirect(url_for('index'))  
        except Exception as e:
            return jsonify({'error': str(e)}), 401

    # GET 요청에 대한 처리
    return render_template('login.html')

@app.route('/logout')
def logout():
    # 세션에서 사용자 ID를 제거하고 로그인 페이지로 리다이렉트
    session.pop('user_id', None)
    return redirect(url_for('login'))

def generate_frames(cap, status_message):
    global event_counter  # 전역 변수로 선언

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            results = model(frame)
            result_frame = results.render()[0]
            ret, buffer = cv2.imencode('.jpg', result_frame)
            frame = buffer.tobytes()

        # 클래스 0 (예: "person")에 대한 탐지 개수
        class_0_count = len([pred for pred in results.pred[0] if pred[5] == 0])

        if class_0_count > 0:
            status_message = '사고를 감지했습니다.'
            socketio.emit('status', status_message)  # 클라이언트로 상태 메시지를 보냅니다.
            time.sleep(3)

            # Firebase에 이벤트 정보 저장
            event_info = {
                'event_number': event_counter,
                'date': time.strftime("%Y-%m-%d %H:%M"),
                'camera_location': '죽교동 노인복지센터'  # 카메라 위치를 필요에 따라 수정하세요
            }
            root_ref.child('events').push(event_info)
            event_counter += 1  # 이벤트 카운터 증가

            # 로그에 기록
            log_message = f'events : {class_0_count} 개의 객체 감지'
            logging.info(log_message)
        else:
            status_message = '감지되지 않았습니다.'

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  
               
# 카메라 1 스트리밍 엔드포인트
@app.route('/camera1')
def camera1_feed():
    return Response(generate_frames(cap, status_message),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alarm.mp3')
def serve_alarm_mp3():
    return send_file('C:/python/yolov5-master/templates/alert.mp3', mimetype='audio/mpeg')

if __name__ == '__main__':
    socketio.run(app, debug=True)
