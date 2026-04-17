# spotify_module.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from rapidfuzz import fuzz
from gtts import gTTS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
SCOPE = "user-read-playback-state user-modify-playback-state"

# Spotify client setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

def get_active_device():
    devices = sp.devices()
    if not devices["devices"]:
        speak("❌ No active Spotify device found.")
        return None
    return devices["devices"][0]["id"]

def play_song(song_name):
    speak(f"🔍 Searching for: {song_name}")
    results = sp.search(q=f"track:{song_name}", type="track", limit=10)
    tracks = results.get("tracks", {}).get("items", [])

    if not tracks:
        speak("❌ No tracks found.")
        return

    # Fuzzy match for better accuracy
    track = max(tracks, key=lambda t: fuzz.ratio(song_name.lower(), t['name'].lower()))
    track_uri = track["uri"]
    speak(f"🎵 Found: {track['name']} by {track['artists'][0]['name']}")

    device_id = get_active_device()
    if device_id:
        sp.start_playback(device_id=device_id, uris=[track_uri])
        speak("▶️ Playing the track...")

def show_current_playing():
    current = sp.current_playback()
    if current and current['is_playing']:
        track = current['item']
        speak(f"🎶 Currently playing: {track['name']} by {track['artists'][0]['name']}")
    else:
        speak("⏹️ Nothing is currently playing.")

def pause_song():
    sp.pause_playback()
    speak("⏸️ Music paused.")

def resume_song():
    sp.start_playback()
    speak("▶️ Music resumed.")

def next_song():
    sp.next_track()
    speak("⏭️ Skipped to next track.")

def previous_song():
    sp.previous_track()
    speak("⏮️ Playing previous track.")

def like_current_song():
    current = sp.current_playback()
    if current:
        track_id = current['item']['id']
        sp.current_user_saved_tracks_add([track_id])
        speak(f"❤️ Liked: {current['item']['name']}")
    else:
        speak("❌ No track to like.")

def enable_shuffle(state=True):
    sp.shuffle(state)
    speak("🔀 Shuffle " + ("enabled." if state else "disabled."))

def set_repeat_mode(mode='track'):
    sp.repeat(mode)
    speak(f"🔁 Repeat mode set to {mode}.")



def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = "temp.mp3"
    tts.save(filename)
    os.system(f"start {filename}" if os.name == "nt" else f"mpg123 {filename}")