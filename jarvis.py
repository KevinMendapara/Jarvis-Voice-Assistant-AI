import pyttsx3
import speech_recognition as sr
import datetime
import os
import cv2
import random
from requests import get
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

# SAFE SPEAK FUNCTION 
def speak(text):
    engine = pyttsx3.init("sapi5")   # re-init EVERY time (important)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 175)

    engine.say(text)
    engine.runAndWait()
    engine.stop()
    print(f"Jarvis: {text}")  # Print what Jarvis speaks

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
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source, timeout=5, phrase_time_limit=8)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print("User said:", query)
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
        if callback:
            callback("USER: " + query)
        
        #  OPEN NOTEPAD FUNCTION

        if "open notepad" in query:
            os.startfile("C:\\Windows\\System32\\notepad.exe")
            print("Opening Notepad")

        #  OPEN COMMAND PROMPT FUNCTION

        elif "open command prompt" in query:
            os.startfile("C:\\Windows\\System32\\cmd.exe")
            print("Opening Command Prompt")

        #  OPEN CAMERA FUNCTION
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

        elif "send messaage" in query:
            pywhatkit.sendwhatmsg(
                "+919892976105",
                "Hello from Python",
                11,
                40
            )
            print("WhatsApp message scheduled")

        #  YOUTUBE SONG FUNCTION

        elif "play song on youtube" in query:
            speak("Which song do you want to play?")
            song = takeCommand()
            pywhatkit.playonyt(song)
            print(f"Playing on YouTube: {song}")

        #  EMAIL FUNCTION

        elif "email to kevin" in query:
            speak("Sir, what should I say?")
            content = takeCommand()
            if "send a file" in content:
                email = 'your@gmail.com'
                password = 'your-password'
                send_to_email = 'person@gmail.com'
                speak("ok sir, What is the subject of the email?")
                subject = takeCommand()
                speak("And sir, what is the message of the email?")
                message = takeCommand()
                speak("Sir, please enter the file path of the document.")
                file_location = input("Enter the file path here: ")

                speak("please wait sir, I am sending email now")
                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = send_to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))

                filename = os.path.basename(file_location)
                attachment = open(file_location, "rb")
                part = MIMEBase('application', 'octet-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                msg.attach(part)

                server = st.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, password)
                server.sendmail(email, send_to_email, msg.as_string())
                server.quit()
                speak("Email has been sent to Kevin")
                print(f"Email with attachment sent to {send_to_email}")
            else:
                email = 'your@gmail.com'
                password = 'your-password'
                send_to_email = 'person@gmail.com'
                message = content

                server = st.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, password)
                server.sendmail(email, send_to_email, message)
                server.quit()
                speak("Email has been sent to Kevin")
                print(f"Email sent to {send_to_email}")

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

        speak("Sir, do you have any other work for me?")

if __name__ == "__main__":
    run_jarvis()
