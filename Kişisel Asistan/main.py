from flask import Flask, request, jsonify
import speech_recognition as sr
import pyttsx3
import datetime
import requests
import smtplib

app = Flask(__name__)
recognizer = sr.Recognizer()
engine = pyttsx3.init()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def recognize_speech():
    with sr.Microphone() as source:
        print("Dinleniyor...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio, language='tr-TR')
            print(f"Kullanıcı dedi ki: {query}\n")
            return query.lower()
        except Exception as e:
            print("Tekrar edin lütfen.")
            return ""


def set_reminder(reminder_time, message):
    speak(f"{reminder_time} için hatırlatıcı ayarlandı: {message}")
    
# Hava durumu bilgisi alma
def get_weather(city):
    api_key = "YOUR_API_KEY" 
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=tr"
    response = requests.get(base_url)
    weather_data = response.json()

    if weather_data["cod"] != "404":
        main = weather_data["main"]
        temperature = main["temp"]
        weather_description = weather_data["weather"][0]["description"]
        speak(f"{city} için hava durumu: {temperature} derece ve {weather_description}.")
    else:
        speak("Şehir bulunamadı.")


def send_email(to_email, subject, message):
    try:
    
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "example@gmail.com" 
        password = "sifreniz" 

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        email_message = f"Subject: {subject}\n\n{message}"
        server.sendmail(sender_email, to_email, email_message)
        server.quit()
        speak("E-posta başarıyla gönderildi.")
    except Exception as e:
        speak("E-posta gönderiminde bir sorun oluştu.")


@app.route('/api/speech', methods=['POST'])
def handle_speech():
    query = recognize_speech()
    return jsonify({"query": query})

@app.route('/api/reminder', methods=['POST'])
def handle_reminder():
    data = request.json
    reminder_time = data.get('time')
    message = data.get('message')
    set_reminder(reminder_time, message)
    return jsonify({"status": "success"})

@app.route('/api/weather', methods=['POST'])
def handle_weather():
    data = request.json
    city = data.get('city')
    get_weather(city)
    return jsonify({"status": "success"})

@app.route('/api/email', methods=['POST'])
def handle_email():
    data = request.json
    to_email = data.get('to_email')
    subject = data.get('subject')
    message = data.get('message')
    send_email(to_email, subject, message)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
