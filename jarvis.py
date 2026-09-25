import pyttsx3
import speech_recognition as sr
import asyncio
import edge_tts
import pygame
import datetime
import os
import cv2
import random
import re
import threading
import json
from requests import get, post
import wikipedia
import time
import webbrowser
import pywhatkit
import smtplib as st
import sys  
import pyjokes
import pyautogui
import geocoder
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import instaloader
import PyPDF2
import sympy
import pywikihow
from pywikihow import search_wikihow

# Load API key from .env file
def get_gemini_api_key():
    paths = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    ]
    for env_file in paths:
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY"):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("GEMINI_API_KEY", "")

# Chat memory
conversation_history = []
def ask_gemini(user_prompt):
    api_key = get_gemini_api_key()
    if not api_key:
        return "Sir, please add your Gemini API key in the dot env file to activate my AI brain."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    # Keep history to last 6 messages (context memory)
    global conversation_history
    if len(conversation_history) > 6:
        conversation_history = conversation_history[-6:]
        
    conversation_history.append({"role": "user", "parts": [{"text": user_prompt}]})
    payload = {
        "system_instruction": {
            "parts": [{
                "text": (
                    "You are J.A.R.V.I.S., Tony Stark's sophisticated, polite, and loyal AI assistant. "
                    "Keep your responses concise (1 to 3 sentences maximum), natural, and clear. "
                    "Never use asterisks, markdown, bullets, or emojis because your answer will be read aloud by text-to-speech."
                )
            }]
        },
        "contents": conversation_history
    }
    try:
        response = post(url, json=payload, timeout=10)
        data = response.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            # Clean any remaining markdown formatting
            reply = re.sub(r'[*_#`]', '', reply).strip()
            
            conversation_history.append({"role": "model", "parts": [{"text": reply}]})
            return reply
        else:
            return "Sir, I encountered an issue processing that query."
    except Exception as e:
        print("Gemini API Error:", e)
        return "I am having trouble connecting to my neural network at the moment."

# ==========================================
# GEMINI VISION & SCREEN MULTIMODAL AI
# ==========================================
def ask_gemini_vision(prompt, image_b64, mime_type="image/jpeg"):
    api_key = get_gemini_api_key()
    if not api_key:
        return "Sir, please configure your Gemini API key in the dot env file to enable visual analysis."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    payload = {
        "system_instruction": {
            "parts": [{
                "text": (
                    "You are J.A.R.V.I.S., Tony Stark's sophisticated AI assistant. "
                    "Analyze the provided image and reply with a concise, intelligent, and natural description "
                    "(1 to 2 sentences max) suitable to be spoken aloud. Never use asterisks, markdown, or bullet points."
                )
            }]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_b64
                        }
                    }
                ]
            }
        ]
    }

    try:
        response = post(url, json=payload, timeout=15)
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            reply = re.sub(r'[*_#`]', '', reply).strip()
            return reply
        else:
            return "Sir, I could not extract clear visual data from that image."
    except Exception as e:
        print("Gemini Vision Error:", e)
        return "Visual sensor processing encountered an anomaly, sir."

def capture_webcam():
    try:
        import base64
        cap = cv2.VideoCapture(0)
        time.sleep(0.2)
        ret, frame = cap.read()
        cap.release()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print("Webcam capture error:", e)
    return None

def capture_screen():
    try:
        from PIL import ImageGrab
        import io, base64
        shot = ImageGrab.grab()
        buf = io.BytesIO()
        shot.thumbnail((1280, 720))
        shot.save(buf, format='JPEG', quality=85)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception as e:
        print("Screen grab error:", e)
    return None

# Initialize pygame mixer and select Jarvis voice
pygame.mixer.init()
JARVIS_VOICE = "en-GB-RyanNeural"

# Iron Man HUD Sound Effects
ACTIVATE_SOUND = os.path.join(os.path.dirname(__file__), "jarvis_activate.wav")
CONFIRM_SOUND = os.path.join(os.path.dirname(__file__), "jarvis_confirm.wav")

def play_hud_sound(sound_type="activate"):
    try:
        path = ACTIVATE_SOUND if sound_type == "activate" else CONFIRM_SOUND
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.4)
            sound.play()
    except Exception:
        pass

# SAFE SPEAK FUNCTION 
async def _edge_speak_async(text, output_path):
    # -4Hz pitch and -3% rate matches Paul Bettany's calm, deep cinematic cadence
    communicate = edge_tts.Communicate(text, JARVIS_VOICE, pitch="-4Hz", rate="-3%")
    await communicate.save(output_path)

def speak(text):
    print(f"Jarvis: {text}")
    audio_path = os.path.join(os.path.dirname(__file__), "temp_jarvis_speech.mp3")
    try:
        # Generate neural AI voice
        asyncio.run(_edge_speak_async(text, audio_path))
        
        # Play audio
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass
    except Exception as e:
        # Automatic fallback to pyttsx3 if offline
        print("Edge-TTS error (using pyttsx3 fallback):", e)
        engine = pyttsx3.init("sapi5")
        engine.setProperty('rate', 175)
        engine.say(text)
        engine.runAndWait()
        engine.stop()


# SPEAK LONG TEXT (Wikipedia fix)
def speak_long_text(text):
    words = text.split()
    chunk = []

    for word in words:
        chunk.append(word)
        if len(chunk) >= 15:     # small chunks = stable
            speak(" ".join(chunk))
            chunk = []
            time.sleep(0.1)

    if chunk:
        speak(" ".join(chunk))
        print(" ".join(chunk))

# NEWS FUNCTION
def news():
    main_url="https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=pub_4ebebb4f12304419ba6e2a6592556b27"
    main_page = get(main_url).json()
    articles = main_page["articles"]
    head = []
    day = ["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth"]
    for ar in articles:
        head.append(ar["title"])
    for i in range(len(day)):
        speak(f"Today's {day[i]} news is: {head[i]}")
        print(f"News {i+1}: {head[i]}")  # Print news

# Calculations
def calculate(expression):
    try:
        result = sympy.sympify(expression)
        speak(f"The result is {result}")
        print(f"Calculation: {expression} = {result}")
    except Exception as e:
        speak("Sorry Sir, I could not calculate that expression.")
        print("Calculation error:", e)

# GET LOCATION
def get_location():
    g = geocoder.ip('me')
    if g.ok:
        print("Latitude :", g.latlng[0])
        print("Longitude:", g.latlng[1])
        print("City     :", g.city)
        print("State    :", g.state)
        print("Country  :", g.country)
        return g.city, g.state, g.country
    else:
        print("Unable to get location")
        return None, None, None

# ==========================================
# TASK 3: PC SYSTEM CONTROLS (VOLUME, BRIGHTNESS, HARDWARE)
# ==========================================
def set_volume(percent):
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        speakers.EndpointVolume.SetMasterVolumeLevelScalar(max(0.0, min(1.0, percent / 100.0)), None)
        speak(f"Volume set to {percent} percent")
    except Exception as e:
        speak("Sorry sir, I could not adjust the volume.")
        print("Volume Error:", e)

def change_volume(delta):
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        curr = speakers.EndpointVolume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, min(1.0, curr + (delta / 100.0)))
        speakers.EndpointVolume.SetMasterVolumeLevelScalar(new_vol, None)
        speak(f"Volume {'increased' if delta > 0 else 'decreased'}")
    except Exception as e:
        speak("Sorry sir, could not adjust the volume.")

def mute_volume(mute=True):
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        speakers.EndpointVolume.SetMute(1 if mute else 0, None)
        speak("Audio muted" if mute else "Audio unmuted")
    except Exception as e:
        speak("Sorry sir, could not mute audio.")

def set_brightness(percent):
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(percent)
        speak(f"Brightness set to {percent} percent")
    except Exception as e:
        speak("Sorry sir, I could not adjust screen brightness.")
        print("Brightness Error:", e)

def change_brightness(delta):
    try:
        import screen_brightness_control as sbc
        curr = sbc.get_brightness()[0]
        new_b = max(10, min(100, curr + delta))
        sbc.set_brightness(new_b)
        speak(f"Brightness adjusted to {new_b} percent")
    except Exception as e:
        speak("Sorry sir, could not adjust brightness.")

def get_system_stats():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        msg = f"CPU load is at {int(cpu)} percent. RAM usage is at {int(ram)} percent."
        if battery:
            state = "plugged in" if battery.power_plugged else "on battery power"
            msg += f" Battery is at {battery.percent} percent and is {state}."
        speak(msg)
    except Exception as e:
        speak("Sorry sir, could not retrieve hardware diagnostics.")
        print("Stats Error:", e)

# ==========================================
# TASK 5: PRODUCTIVITY (WEATHER, NOTES, TIMERS, CONTACTS)
# ==========================================
def get_weather(city=""):
    try:
        url = f"https://wttr.in/{city}?format=%l:+%C,+%t" if city else "https://wttr.in/?format=%l:+%C,+%t"
        res = get(url, timeout=5).text.strip()
        clean_res = res.replace("°C", " degrees Celsius").replace("+", "")
        speak(f"Current weather: {clean_res}")
        print(f"Weather: {clean_res}")
    except Exception as e:
        speak("Sorry sir, I could not fetch the weather report.")
        print("Weather Error:", e)

NOTES_FILE = os.path.join(os.path.dirname(__file__), "jarvis_notes.txt")

def take_note(note_text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {note_text}\n")
    speak("Note saved successfully, sir.")

def read_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if lines:
            speak("Here are your recent notes:")
            for line in lines[-5:]:
                speak(line)
        else:
            speak("You have no saved notes, sir.")
    else:
        speak("You have no saved notes, sir.")

def set_timer(seconds, label="timer"):
    def timer_worker():
        time.sleep(seconds)
        play_hud_sound("activate")
        speak(f"Sir! Your {label} for {seconds} seconds has finished!")
    t = threading.Thread(target=timer_worker, daemon=True)
    t.start()
    speak(f"Timer set for {seconds} seconds, sir.")

def get_contact(name):
    contacts_path = os.path.join(os.path.dirname(__file__), "contacts.json")
    if os.path.exists(contacts_path):
        with open(contacts_path, "r", encoding="utf-8") as f:
            contacts = json.load(f)
            return contacts.get(name.lower(), None)
    return None

# ==========================================
# UNIVERSAL APPLICATION LAUNCHER
# ==========================================
COMMON_APPS = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "browser": "chrome",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "firefox": "firefox",
    "code": "code",
    "vs code": "code",
    "visual studio code": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "spotify": "spotify",
    "command prompt": "cmd",
    "cmd": "cmd",
    "terminal": "wt",
    "powershell": "powershell",
    "paint": "mspaint",
    "file explorer": "explorer",
    "files": "explorer",
    "explorer": "explorer",
    "task manager": "taskmgr",
    "settings": "start ms-settings:",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "whatsapp": "whatsapp",
}

def open_app(app_name):
    app_clean = app_name.lower().strip()
    cmd = COMMON_APPS.get(app_clean, None)

    if cmd:
        if cmd.startswith("start "):
            os.system(cmd)
        else:
            os.system(f'start "" "{cmd}"')
        speak(f"Opening {app_name}, sir.")
        return True

    # Try launching directly via Windows Start
    try:
        res = os.system(f'start "" "{app_clean}"')
        if res == 0:
            speak(f"Opening {app_name}, sir.")
            return True
    except Exception:
        pass

    # Fallback: Type in Windows Search
    try:
        pyautogui.press('win')
        time.sleep(0.3)
        pyautogui.write(app_name, interval=0.03)
        time.sleep(0.4)
        pyautogui.press('enter')
        speak(f"Searching and opening {app_name}, sir.")
        return True
    except Exception as e:
        speak(f"Sorry sir, could not find application {app_name}.")
        print("Open App Error:", e)
        return False

# INSTAGRAM PROFILE DOWNLOADER
from instaloader import Instaloader, Profile

def download_instagram_profile_pic(username):
    try:
        loader = Instaloader()
        profile = Profile.from_username(loader.context, username)
        loader.download_profilepic(profile)
        speak(f"{username}'s profile picture has been downloaded successfully.")
        print(f"Downloaded Instagram profile picture of: {username}")
    except Exception as e:
        speak("Sorry Sir, I could not download this Instagram profile.")
        print("Instagram download error:", e)


#  SPEECH TO TEXT 
def takeCommand():
    play_hud_sound("activate")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source, timeout=5, phrase_time_limit=8)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print("User said:", query)
        play_hud_sound("confirm")
        return query.lower()
    except Exception:
        speak("Say that again please")
        return ""

#  WISH 
def wish():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good Morning Sir. I am your Jarvis. How may I help you?")
        print("Good Morning Sir. I am your Jarvis. How may I help you?")
    elif hour < 18:
        speak("Good Afternoon Sir. I am your Jarvis. How may I help you?")
        print("Good Afternoon Sir. I am your Jarvis. How may I help you?")
    else:
        speak("Good Evening Sir. I am your Jarvis. How may I help you?")
        print("Good Evening Sir. I am your Jarvis. How may I help you?")

def search_wikihow(query, max_results=10,langs=["en"]):
    return pywikihow.search_wikihow(query, max_results=max_results, langs=langs)

# SEND EMAIL
def sendEmail(to, content):
    server = st.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login("kevinsadguru@gmail.com", "mabf wkar aikz tgib")
    server.sendmail("kevinsadguru@gmail.com", to, content)
    server.close()
    print(f"Email sent to {to} with content: {content}")

def reader_pdf():
    try:
        path = r"C:\Users\HP\pdf\Python Programming.pdf"  # change username if needed
        book = open(path,"rb")

        reader = PyPDF2.PdfReader(book)
        total_pages = len(reader.pages)

        speak(f"Total number of pages in this book is {total_pages}")
        speak("Sir, please enter the page number I have to read")

        pg = int(input("Enter page number: "))

        if pg < 1 or pg > total_pages:
            speak("Invalid page number")
            return

        page = reader.pages[pg - 1]   # FIXED indexing
        text = page.extract_text()

        if text:
            speak(text)
        else:
            speak("Sorry sir, no readable text found on this page")

    except FileNotFoundError:
        speak("PDF file not found. Please check the file path")
    except Exception as e:
        speak("Sorry sir, I am unable to read the PDF")
        print("PDF Error:", e)

# MAIN FUNCTION
def run_jarvis(callback=None):
    wish()
    while True:
        query = takeCommand()
        if not query:
            continue
            
        if callback:
            callback("USER: " + query)
            
        # ==========================================
        # TASK 4: WAKE WORD DETECTION ("Jarvis" / "Hey Jarvis")
        # ==========================================
        if query in ["jarvis", "hey jarvis"]:
            play_hud_sound("confirm")
            speak("At your service, sir. What can I do for you?")
            continue
        elif query.startswith("jarvis "):
            query = query[7:].strip()
        elif query.startswith("hey jarvis "):
            query = query[11:].strip()
        
        # ==========================================
        # IN-APP ACTIONS (PERFORM TASKS ON ACTIVE APP)
        # ==========================================
        if query.startswith("type ") or query.startswith("write "):
            text_to_type = query.split(" ", 1)[1]
            speak("Typing now, sir.")
            time.sleep(0.5)
            pyautogui.write(text_to_type + " ", interval=0.03)

        elif "press enter" in query or "hit enter" in query:
            pyautogui.press("enter")

        elif "press backspace" in query or "delete that" in query:
            pyautogui.press("backspace")

        elif "select all" in query:
            pyautogui.hotkey("ctrl", "a")

        elif "copy that" in query or "copy this" in query:
            pyautogui.hotkey("ctrl", "c")
            speak("Copied to clipboard, sir.")

        elif "paste that" in query or "paste here" in query or "paste" in query:
            pyautogui.hotkey("ctrl", "v")

        elif "undo that" in query or "undo" in query:
            pyautogui.hotkey("ctrl", "z")

        elif "save file" in query or "save this" in query:
            pyautogui.hotkey("ctrl", "s")
            speak("File saved, sir.")

        # In-App Scrolling & Tab Navigation
        elif "scroll down" in query:
            pyautogui.scroll(-600)

        elif "scroll up" in query:
            pyautogui.scroll(600)

        elif "new tab" in query:
            pyautogui.hotkey("ctrl", "t")

        elif "close tab" in query:
            pyautogui.hotkey("ctrl", "w")

        elif "reload" in query or "refresh page" in query:
            pyautogui.hotkey("ctrl", "r")

        elif "zoom in" in query:
            pyautogui.hotkey("ctrl", "+")

        elif "zoom out" in query:
            pyautogui.hotkey("ctrl", "-")

        # Window Sizing & Control
        elif "maximize" in query or "maximize window" in query:
            pyautogui.hotkey("win", "up")

        elif "minimize" in query or "minimize window" in query:
            pyautogui.hotkey("win", "down")

        elif "close this window" in query or "close this app" in query or "close window" in query:
            pyautogui.hotkey("alt", "f4")
            speak("Window closed, sir.")

        elif "pause video" in query or "play video" in query:
            pyautogui.press("space")

        # ==========================================
        # ADVANCED MEDIA CONTROLS
        # ==========================================
        elif "next track" in query or "next song" in query or "skip track" in query:
            pyautogui.press("nexttrack")
            speak("Skipping to next track, sir.")

        elif "previous track" in query or "previous song" in query or "last song" in query:
            pyautogui.press("prevtrack")
            speak("Playing previous track, sir.")

        elif "stop music" in query or "stop audio" in query:
            pyautogui.press("stop")
            speak("Audio stopped, sir.")

        # ==========================================
        # VISION AI & SCREEN READING (WEBCAM & SCREEN)
        # ==========================================
        elif "look at this" in query or "what am i holding" in query or "what do you see" in query or "scan this" in query:
            speak("Scanning optical feed now, sir...")
            b64 = capture_webcam()
            if b64:
                analysis = ask_gemini_vision("Describe what the user is holding or what is in front of the camera.", b64)
                speak(analysis)
            else:
                speak("Optical camera sensor is unavailable, sir.")

        elif "summarize screen" in query or "summarize my screen" in query or "what is on my screen" in query or "read my screen" in query:
            speak("Scanning display contents, sir...")
            b64 = capture_screen()
            if b64:
                analysis = ask_gemini_vision("Summarize the main content, window, or document shown on this computer screen in 2 clear sentences.", b64)
                speak(analysis)
            else:
                speak("Display sensor unavailable, sir.")

        elif "explain this error" in query or "diagnose error" in query or "debug this" in query:
            speak("Diagnosing screen error, sir...")
            b64 = capture_screen()
            if b64:
                analysis = ask_gemini_vision("Identify and diagnose the programming error, bug, or issue shown on this screen, and explain the solution in 2 clear sentences.", b64)
                speak(analysis)
            else:
                speak("Could not capture display, sir.")

        # ==========================================
        # AUTONOMOUS AGENT ACTIONS
        # ==========================================
        elif "search youtube for" in query:
            topic = query.replace("search youtube for", "").replace("and play", "").strip()
            speak(f"Searching YouTube for {topic}, sir.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")

        elif ("open notepad and write" in query) or ("open word and write" in query):
            target_app = "notepad" if "notepad" in query else "word"
            text_body = query.split("write", 1)[1].strip()
            open_app(target_app)
            time.sleep(1.0)
            pyautogui.write(text_body + " ", interval=0.03)
            speak("I have opened the editor and written your text, sir.")

        elif "lock pc" in query or "lock my pc" in query or "lock computer" in query:
            speak("Locking workstation immediately, sir.")
            os.system("rundll32.exe user32.dll,LockWorkStation")

        # ==========================================
        # UNIVERSAL APP LAUNCHER ("open <any app>")
        # ==========================================
        elif "open camera" in query:
            cap = cv2.VideoCapture(0)
            while True:
                ret, img = cap.read()
                cv2.imshow("Camera", img)
                if cv2.waitKey(50) == 27:
                    break
            cap.release()
            cv2.destroyAllWindows()
            print("Camera opened")

        elif query.startswith("open "):
            target_app = query[5:].strip()
            if target_app == "youtube":
                webbrowser.open("www.youtube.com")
            elif target_app == "google":
                speak("Sir, what should I search on Google?")
                q = takeCommand()
                if q:
                    webbrowser.open("https://www.google.com/search?q=" + q)
            elif target_app == "stackoverflow":
                webbrowser.open("www.stackoverflow.com")
            else:
                open_app(target_app)

        #  PLAY MUSIC FUNCTION

        elif "play music" in query:
            music_dir = "C:\\music"
            songs = os.listdir(music_dir)
            song = random.choice(songs)
            os.startfile(os.path.join(music_dir, song))
            print(f"Playing music: {song}")

        #  IP ADDRESS FUNCTION

        elif "ip address" in query:
            ip = get("https://api.ipify.org").text
            speak(f"Your IP address is {ip}")
            print("IP Address:", ip)

        # WIKIPEDIA FUNCTION

        elif "wikipedia" in query:
            try:
                speak("Searching Wikipedia")
                query = query.replace("wikipedia", "").strip()
                if query == "":
                    speak("Please say a topic to search on Wikipedia")
                else:
                    result = wikipedia.summary(query, sentences=2)
                    print(result)
                    speak("According to Wikipedia")
                    speak_long_text(result)
            except Exception:
                speak("Sorry, I could not find any information")
                print("Wikipedia search failed")

        # OPEN YOUTUBE FUNCTION

        elif "open youtube" in query:
            webbrowser.open("www.youtube.com")
            print("Opening YouTube")

        # OPEN GOOGLE FUNCTION

        elif "open google" in query:
            speak("Sir, what should I search on Google?")
            query = takeCommand()
            webbrowser.open("https://www.google.com/search?q=" + query)
            print(f"Searching Google for: {query}")

        # OPEN STACKOVERFLOW FUNCTION

        elif "open stackoverflow" in query:
            webbrowser.open("www.stackoverflow.com")
            print("Opening StackOverflow")

        #  WHATSAPP MESSAGE FUNCTION
        elif "send message" in query or "send whatsapp" in query or "whatsapp" in query:
            speak("Who would you like to message, sir?")
            recipient = takeCommand()
            contact = get_contact(recipient)
            phone = contact["phone"] if contact else None

            if not phone:
                speak(f"Contact {recipient} not found. Please enter phone number in the terminal.")
                phone = input("Enter phone number with country code (e.g. +91...): ")

            speak("What is the message, sir?")
            msg_text = takeCommand()
            if msg_text:
                speak(f"Sending WhatsApp message to {recipient or phone} now, sir.")
                try:
                    pywhatkit.sendwhatmsg_instantly(phone, msg_text, 15, True, 3)
                    print(f"WhatsApp sent to {phone}: {msg_text}")
                except Exception as e:
                    speak("Could not send WhatsApp message.")
                    print("WhatsApp Error:", e)

        #  YOUTUBE SONG FUNCTION

        elif "play song on youtube" in query:
            speak("Which song do you want to play?")
            song = takeCommand()
            pywhatkit.playonyt(song)
            print(f"Playing on YouTube: {song}")

        #  EMAIL FUNCTION

        elif "email" in query or "send email" in query:
            speak("Who should I send the email to, sir?")
            recipient_name = takeCommand()
            contact = get_contact(recipient_name)
            send_to_email = contact["email"] if contact else None

            if not send_to_email:
                speak(f"Contact {recipient_name} not found. Please enter the email address.")
                send_to_email = input("Enter recipient email address: ")

            speak("What is the subject of the email?")
            subject = takeCommand()
            speak("What is the message, sir?")
            message = takeCommand()

            sender_email = os.environ.get("EMAIL_USER", "kevinsadguru@gmail.com")
            sender_pass = os.environ.get("EMAIL_PASSWORD", "mabf wkar aikz tgib")

            try:
                server = st.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_pass)
                server.sendmail(sender_email, send_to_email, f"Subject: {subject}\n\n{message}")
                server.quit()
                speak(f"Email has been sent to {recipient_name or send_to_email}")
                print(f"Email sent to {send_to_email}")
            except Exception as e:
                speak("Sorry sir, I could not send the email.")
                print("Email Error:", e)

        #  CLOSE APPLICATIONS FUNCTION

        elif "closed all applications" in query:
            speak("Closing all applications")
            os.system("taskkill /f /im notepad.exe")
            os.system("taskkill /f /im cmd.exe")
            os.system("taskkill /f /im camera.exe")
            os.system("taskkill /f /im music.exe")
            os.system("taskkill /f /im google.exe")
            print("Closed all applications")

        #  JOKE FUNCTION

        elif "tell me a joke" in query:
            joke = pyjokes.get_joke()
            speak(joke)
            print("Joke:", joke)

        #  WINDOW SWITCHER FUNCTION

        elif "switch the window" in query:
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
            pyautogui.keyUp("alt")
            print("Switched window")

        # NEWS FUNCTION

        elif "tell me the news" in query:
            news()

        # SHUTDOWN FUNCTION

        elif "shutdown the system" in query:
            os.system("shutdown /s /t 5")
            print("System will shutdown in 5 seconds")

        # RESTART FUNCTION

        elif "restart the system" in query:
            os.system("shutdown /r /t 5")
            print("System will restart in 5 seconds")

        #  SLEEP FUNCTION

        elif "sleep the system" in query:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            print("System going to sleep")

        # LOCATION FUNCTION

        elif "where i am" in query or "where we are" in query:
            city, state, country = get_location()
            if city and state and country:
                speak(f"Sir, You are in {city}, {state}, {country}.")
            else:
                speak("Sorry Sir, I am unable to fetch your location at the moment.")

        # INSTAGRAM PROFILE FUNCTION

        elif "instagram profile" in query or "profile on instagram" in query:
                speak("Sir, please enter the username of the Instagram profile.")
                name = input("Enter Instagram username here: ")
                webbrowser.open(f"https://www.instagram.com/{name}/")
                speak(f"Sir, here is the profile of {name} on Instagram.")
                print(f"Opened Instagram profile: {name}")
                time.sleep(5)
                
                speak("Do you want to download the profile picture of this account?")
                condition = takeCommand()
                if "yes download" in condition:
                    download_instagram_profile_pic(name)

        #  SCREENSHOT FUNCTION

        elif "take a screenshot" in query:
            speak("Taking screenshot sir")
            img = pyautogui.screenshot()
            img.save("screenshot.png")
            speak("Screenshot taken and saved as screenshot.png")
            print("Screenshot saved as screenshot.png")

        #  READ PDF FUNCTION
        
        elif "read pdf" in query:
            reader_pdf()

        #  HIDE/UNHIDE FILES FUNCTION

        elif "hide all files" in query or "hide the files" in query or "visible for everyone" in query:
            speak("Sir please tell me do you want to hide the files or make it visible for everyone")
            condition = takeCommand()
            if "hide" in condition or "hide the files" in condition or "hide for everyone" in condition:
                os.system("attrib +h \"C:\\Users\\HP\\numpy\" /s /d")  # change path if needed
                speak("All files are now hidden")
                print("All files hidden")

            elif "visible the files" in condition or "make it visible" in condition or "visible for everyone" in condition:
                os.system("attrib -h \"C:\\Users\\HP\\numpy\" /s /d")  # change path if needed
                speak("All files are now visible")
                print("All files visible") 
            
            elif "leave it" in condition or "leave for now" in condition:
                speak("Ok sir, as you wish")
                print("No changes made to file visibility")

        # Calculate functions

        elif "calculate" in query or "what is" in query:
            speak("Sir, please tell me the calculation")
            math_query = takeCommand()
            answer = calculate(math_query)
            speak(f"The answer is {answer}")
            print(f"Answer: {answer}")

        #  HOW TO MODE FUNCTION

       # HOW TO MODE FUNCTION

        elif "activate how to mode" in query or "how to do mode" in query:
            speak("How to mode activated. Please tell me what you want to learn.")
            print("How-To Mode Activated")

            while True:
                speak("Please tell me what you want to know.")
                how = takeCommand()
                print("How-To Query:", how)

                if how == "":
                    continue

                if "exit how to mode" in how or "close how to mode" in how:
                    speak("Exiting how to mode.")
                    print("Exited How-To Mode")
                    break

                try:
                    max_results = 1
                    how_to = search_wikihow(how, max_results)

                    if len(how_to) == 0:
                        speak("Sorry sir, I could not find any information.")
                        print("No WikiHow results found")
                        continue

                    article = how_to[0]

                    print("\n--- WikiHow Result ---")
                    print("Title:", article.title)
                    print("Summary:", article.summary)
                    print("----------------------\n")

                    speak_long_text(article.summary)

                except Exception as e:
                    speak("Sorry sir, I am unable to find the information.")
                    print("How-To Mode Error:", e)


        #  EXIT JARVIS 

        elif "exit" in query:
            speak("Goodbye Sir. Have a nice day.")
            print("Exiting Jarvis")
            sys.exit()

        # ==========================================
        # TASK 3: PC SYSTEM CONTROLS
        # ==========================================
        elif "mute" in query:
            mute_volume(True)
        elif "unmute" in query:
            mute_volume(False)
        elif "volume up" in query or "increase volume" in query:
            change_volume(15)
        elif "volume down" in query or "decrease volume" in query:
            change_volume(-15)
        elif "set volume to" in query:
            nums = re.findall(r'\d+', query)
            if nums:
                set_volume(int(nums[0]))
            else:
                speak("Please specify a percentage, sir.")

        elif "set brightness to" in query or "brightness to" in query:
            nums = re.findall(r'\d+', query)
            if nums:
                set_brightness(int(nums[0]))
            else:
                speak("Please specify a brightness percentage, sir.")
        elif "increase brightness" in query or "more brightness" in query:
            change_brightness(20)
        elif "decrease brightness" in query or "lower brightness" in query:
            change_brightness(-20)

        elif "system status" in query or "hardware status" in query or "battery" in query or "cpu" in query:
            get_system_stats()

        # ==========================================
        # TASK 5: WEATHER, NOTES & TIMERS
        # ==========================================
        elif "weather" in query or "temperature" in query:
            if " in " in query:
                city = query.split(" in ")[-1].strip()
                get_weather(city)
            else:
                get_weather()

        elif "take a note" in query or "write this down" in query or "make a note" in query:
            speak("What would you like me to write down, sir?")
            note = takeCommand()
            if note:
                take_note(note)
        elif "read notes" in query or "show notes" in query or "my notes" in query:
            read_notes()

        elif "set a timer for" in query or "timer for" in query:
            nums = re.findall(r'\d+', query)
            if nums:
                val = int(nums[0])
                if "minute" in query:
                    set_timer(val * 60, f"{val} minute timer")
                else:
                    set_timer(val, f"{val} second timer")
            else:
                speak("Please specify how many minutes or seconds for the timer, sir.")

        elif query != "":
            print(f"Routing to Gemini AI: {query}")
            reply = ask_gemini(query)
            speak(reply)

        speak("Sir, do you have any other work for me?")

if __name__ == "__main__":
    run_jarvis()
