# Build Service:
- cd service
- docker build --tag service_img .
- docker run -p8080:8080/tcp service_img

## test: http://127.0.0.1:8080/getinfo?target=123456

<!-- adb -P 5037 -s emulator-5554 shell am start -W -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=+554899518589&msg=Hi" -->
<!-- adb -P 5037 -s emulator-5554 shell am start -W -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=+5548999890650&msg=Hi" -->