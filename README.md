![이미지](https://github.com/user-attachments/assets/c92cbf79-a093-463a-9dd7-a86f75090d6c)![이미지](https://github.com/user-attachments/assets/6016227e-1120-4f2b-b124-e7bcda01c744)![image](https://github.com/user-attachments/assets/a8c73ddf-8a2e-45d2-825e-5cd2e812e545) 
# 인간-낙하-보행-감지-신호등-신호등-신호등
실시간으로 사람의 상태를 감지하고 신호 시간을 조정하는 신호등

# 소개
횡단 중인 보행자를 실시간으로 카메라로 촬영하고 yolov5 모델을 사용하여 보행자를 감지합니다.

걷기, 넘어짐 2가지 모델을 학습시켜 사람의 상태를 탐지합니다.

보행자가 횡단보도 보행 중일 때 보행시간에 추가시간을 부여하여 녹색 등을 유지하고 사람이 걷고 있다는 신호를 보냅니다.
보행자가 쓰러지면 쓰러졌다고 경고 알림을 소리와 메세지를 홈페이지에서 출력하고 사람이 쓰러졌다는 신호를 보냅니다.

# 사용 모델
https://github.com/ultralytics/yolov5

# 사람 상태 감지 

1. 걷기
![이미지 업로드 중.png...]()

2. 넘어짐
![이미지 업로드 중.png...]()


# 사람 넘어짐 통계
보행자 사고를 파이어베이스에서 로그 데이터를 가져와 x축은 날짜를 기준으로 구성, y축은 보행자의 쓰러짐을 감지한 횟수를 나타내는 그래프를 구성하여 보행자 사고를 집계합니다.

![이미지 업로드 중.png...]()

