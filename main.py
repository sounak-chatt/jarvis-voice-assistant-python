import speech_recognition as sr
from gtts import gTTS
import os
import webbrowser
import time
import playsound
from spotify_module import play_song, pause_song,previous_song, resume_song, next_song, show_current_playing, like_current_song,enable_shuffle, set_repeat_mode
import requests
from dotenv import load_dotenv

recognizer = sr.Recognizer()

load_dotenv()

newsapi = os.getenv("NEWSAPI_KEY")
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

def speak(text, filename="response.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

def processCommand(c):
    c = c.lower()
    if "open google" in command:
        webbrowser.open("https://google.com")
    elif "open instagram" in command:
        webbrowser.open("https://instagram.com")
    elif "open facebook" in command:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
    elif c.lower().startswith("play "):
        song = c.lower().replace("play ", "").strip()
        speak(f"Playing {song}")
        play_song(song)
    elif "pause" in command:
        pause_song()
    
    elif "resume" in command or "play music" in command:
        resume_song()
    
    elif "next" in command:
        next_song()
    
    elif "previous" in command or "go back" in command:
        previous_song()
    
    elif "like this song" in command:
        like_current_song()

    elif "shuffle on" in command:
        enable_shuffle(True)

    elif "shuffle off" in command:
        enable_shuffle(False)

    elif "repeat song" in command:
        set_repeat_mode("track")

    elif "repeat context" in command:
        set_repeat_mode("context")

    elif "repeat off" in command:
        set_repeat_mode("off")
        
    elif "tell news" in command:
        try:
            url = f"https://newsapi.org/v2/everything?q=India&sortBy=publishedAt&apiKey={newsapi}"
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                articles = data.get('articles', [])
                
                if not articles:
                    speak("No news articles found at the moment.")
                else:
                    for i, article in enumerate(articles[:5], start=1):
                        speak(f"Headline {i}: {article['title']}")
            else:
                speak(f"Unable to fetch news, error code {r.status_code}")
        except Exception as e:
            speak("Unable to fetch news at the moment.")
            print(f"News API error: {e}")



    else:
        speak("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    speak("Initializing Jarvis...")

    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=2)
                word = recognizer.recognize_google(audio)
                print(f"Wake word detected: {word}")

                if word.lower() == "jarvis":
                    speak("Yes sir, how may I help you?")

                    print("Listening for command...")
                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        command_audio = recognizer.listen(source, timeout=6, phrase_time_limit=5)
                        command = recognizer.recognize_google(command_audio, language="en-IN")
                        print(f"Command received: {command}")
                        processCommand(command)

        except sr.WaitTimeoutError:
            print("Timeout. Restarting listening cycle...")
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            print(f"API request error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
