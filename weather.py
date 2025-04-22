import json, requests, pyttsx3, pyaudio, vosk
from datetime import datetime

"""
"погода" - говорит текущую температуру и состояние

"ветер" - сообщает скорость ветра

"направление" - говорит направление ветра

"записать" - сохраняет данные в файл weather.txt

"прогулка" - рекомендует или не рекомендует прогулку

"стоп" - выход из программы
"""

class WeatherAssistant:
    def __init__(self, city = "Санкт-Петербург"):
        #синтез речи
        self.engine = pyttsx3.init()
        
        #модель распознавания речи
        self.model = vosk.Model("vosk-model-small-ru-0.22")
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.in_dialoge = False

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, 
                                    channels=1, 
                                    rate=16000, 
                                    input=True, 
                                    frames_per_buffer=8000)
        
        self.city = city
        self.weather_data = None

    def speak(self, text): #озвучивание текста
        print(text)
        self.engine.say(text)
        self.engine.runAndWait() #отдаем на исполнение

    def listen(self):
        self.speak("Говорите ...")
        
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                command = result.get('text', '').lower()
                
                if command:
                    print(f"Распознано: {command}")
                    self.process_command(command)

    def get_weather(self):
        try:
            url = f"http://wttr.in/{self.city}?format=j1"
            response = requests.get(url)
            self.weather_data = response.json()
            return True
        except Exception as e:
            self.speak(f"Ошибка при получении погоды: {str(e)}")
            return False

    def process_command(self, command):
        if not self.weather_data and not self.get_weather():
            return
            
        if "погода" in command:
            temp = self.weather_data['current_condition'][0]['temp_C']
            desc = self.weather_data['current_condition'][0]['weatherDesc'][0]['value']
            self.speak(f"Сейчас в {self.city} {temp} градусов, {desc}")
            
        elif "ветер" in command:
            wind_speed = self.weather_data['current_condition'][0]['windspeedKmph']
            self.speak(f"Скорость ветра {wind_speed} километров в час")
            
        elif "направление" in command:
            wind_dir = self.weather_data['current_condition'][0]['winddir16Point']
            self.speak(f"Ветер дует с {wind_dir} направления")
            
        elif "записать" in command:
            self.save_weather_to_file()
            self.speak("Данные о погоде сохранены в файл weather.txt")
            
        elif "прогулка" in command:
            temp = int(self.weather_data['current_condition'][0]['temp_C'])
            wind_speed = int(self.weather_data['current_condition'][0]['windspeedKmph'])
            
            if temp < 5 or wind_speed > 15:
                self.speak("Прогулка не рекомендуется, слишком холодно или ветрено")
            else:
                self.speak("Можно идти на прогулку, погода хорошая")
                
        elif "стоп" in command:
            self.speak("Завершаю работу")
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            exit()
            
        else:
            self.speak("Не распознал команду. Попробуйте еще раз")

    def save_weather_to_file(self):
        with open('weather.txt', 'w', encoding='utf-8') as f:
            f.write(f"""Погода в {self.city} на {datetime.now().strftime('%Y-%m-%d %H:%M')}
Температура: {self.weather_data['current_condition'][0]['temp_C']}°C
Состояние: {self.weather_data['current_condition'][0]['weatherDesc'][0]['value']}
Ветер: {self.weather_data['current_condition'][0]['windspeedKmph']} км/ч
Направление ветра: {self.weather_data['current_condition'][0]['winddir16Point']}""")

if __name__ == "__main__":
    assistant = WeatherAssistant()
    assistant.listen()