import os
import base64

# 랜덤한 바이트 문자열 생성
secret_key = base64.urlsafe_b64encode(os.urandom(24)).decode('utf-8')

# 생성된 시크릿 키 출력
print(f"Generated secret key: {secret_key}")