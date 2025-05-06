from groq import Groq
from PIL import ImageGrab, Image
from faster_whisper import WhisperModel
from termcolor import colored
from pynput import mouse
import pygetwindow as gw
import cv2
import pyperclip
import google.generativeai as genai
import pyttsx3
import os
import sys
import speech_recognition as sr
import time
import re
import keyboard
import tempfile
import winsound
import logging

# Initialize clients and configuration
groq_client = Groq(api_key='INSERT_YOUR_GROQ_API_KEY_HERE')
genai.configure(api_key='INSERT_YOUR_GENERATIVE_AI_API_KEY_HERE')

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 250)
engine.setProperty("volume", 1.0)
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

# Initialize the speech recognizer
r = sr.Recognizer()
mic = sr.Microphone()


# System message for the conversation
sys_msg = (
    'You are a multi-modal AI voice assistant. Your user may or may not have attached a photo for context '
    '(either a screenshot or a webcam capture). Any photo has already been processed into a highly detailed '
    'text prompt that will be attached to their transcribed voice prompt. Generate the most useful and '
    'factual response possible, carefully considering all previous generated text in your response before '
    'adding new tokens to the response. Do not expect or request images, just use the context if added. '
    'Use all of the context of this conversation so your response is relevant to the conversation. Make '
    'your responses clear and concise, avoiding any verbosity.'
)

convo = [{'role': 'system', 'content': sys_msg}]

# Generation configuration
generation_config = {
    'temperature': 0.7,
    'top_p': 1,
    'top_k': 1,
    'max_output_tokens': 2048
}

# Safety settings
safety_settings = [
    {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_NONE'},
    {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_NONE'},
    {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_NONE'},
    {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_NONE'},
]

# Initialize the generative model
model = genai.GenerativeModel('gemini-1.5-flash-latest',
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Initialize Whisper model
num_cores = os.cpu_count()
whisper_size = 'base'
whisper_model = WhisperModel(
    whisper_size,
    device='cpu',
    compute_type='int8',
    cpu_threads=num_cores // 2,
    num_workers=num_cores // 2
)

# Global variables for recording
is_recording = False
recording_thread = None
speaking_in_progress = False



def speak(text):
    """Convert text to speech"""
    global engine, speaking_in_progress
    speaking_in_progress = True  
    engine.say(text)
    engine.runAndWait()
    speaking_in_progress = False

def stop_speaking():
    """Stop the speech engine"""
    global engine
    if engine:
        engine.stop()

def groq_prompt(prompt, img_context):
    """Generate a response using the Groq API"""
    if img_context:
        prompt = f'\nUSER PROMPT: {prompt}\n\n    IMAGE CONTEXT: {img_context}'
    convo.append({'role': 'user', 'content': prompt})
    chat_completion = groq_client.chat.completions.create(messages=convo, model='llama3-70b-8192')
    
    response = chat_completion.choices[0].message   
    convo.append(response)

    return response.content

def function_call(prompt):
    """Determine which function to call based on the prompt"""
    sys_msg = (
        'You are an AI function calling model. You will determine whether extracting the users clipboard content, '
        'taking a screenshot, capturing the webcam or calling no functions is best for a voice assistant to respond '
        'to the users prompt. The webcam can be assumed to be a normal laptop webcam facing the user. You will '
        'respond with only one selection from this list: ["open chrome","provide link", "extract clipboard", "take high quality shot", "take screenshot", "capture webcam", "None"] \n'
        'Do not respond with anything but the most logical selection from that list with no explanations. Format the '
        'function call name exactly as I listed.'
    )
    
    function_convo = [{'role': 'system', 'content': sys_msg},
                     {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    response = chat_completion.choices[0].message

    return response.content

def open_chrome():
    """Open Chrome browser"""
    print(colored('\n[Opening Chrome TEST]', 'yellow'))
    os.system('start chrome')  # For Windows
    # os.system('open -a "Google Chrome"')  # For macOS

def provide_link(text):
    """Provide link"""
    url_pattern = r'(https?://[^\s]+)'  # Regular expression for URLs
    match = re.search(url_pattern, text)

    if match:
        link = match.group(0)
        link = link.rstrip(')')  
        link = link.rstrip('.')
        link = link.rstrip(',')
        pyperclip.copy(link)
        print(colored(f"\n[Copied successfully]: {link}", 'yellow'))

def take_high_quality_shot():
    """Take a high-quality screenshot"""
    path = 'HQscreenshot.jpg'
    screenshot = ImageGrab.grab()
    screenshot.save(path, quality=100)

def take_screenshot(): 
    """Take a regular screenshot"""
    path = 'screenshot.jpg'
    screenshot = ImageGrab.grab()
    rgb_screenshot = screenshot.convert('RGB')
    rgb_screenshot.save(path, quality=15)

def web_cam_capture():
    """Capture an image from the webcam"""
    web_cam = cv2.VideoCapture(0)
    if not web_cam.isOpened():
        print('Error: Camera did not open')
        exit()

    path = 'webcam.jpg'
    ret, frame = web_cam.read()
    cv2.imwrite(path, frame)
    web_cam.release()
    cv2.destroyAllWindows()
    
def get_clipboard_text():
    """Get text from the clipboard"""
    clipboard_content = pyperclip.paste()
    if isinstance(clipboard_content, str):
        return clipboard_content
    else:
        print('No clipboard text to copy')
        return None

def vision_prompt(prompt, photo_path):
    """Generate a vision prompt from an image"""
    img = Image.open(photo_path)
    prompt = (
        'You are the vision analysis AI that provides semtantic meaning from images to provide context '
        'to send to another AI that will create a response to the user. Do not respond as the AI assistant '
        'to the user. Instead take the user prompt input and try to extract all meaning from the photo'
        'relevant to the user prompt. Then generate as much objective data about the image for the AI '
        f'assistant who will respond to the user. \nUSER PROMPT: {prompt}'
    )
    response = model.generate_content([prompt, img])
    return response.text

def wav_to_text(audio_path):
    """Convert a WAV file to text using Whisper"""
    segments, _ = whisper_model.transcribe(audio_path)
    text = ''.join(segment.text for segment in segments)
    return text   

def record_audio():
    """Record audio while Enter is pressed"""
    global is_recording
    
    # Use direct file recording instead of frames
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_file.close()
    
    try:
        with mic as source:
            try:
                r.adjust_for_ambient_noise(source, duration=0.5)
            except Exception as e:
                print(colored(f"Warning: Couldn't adjust for ambient noise - {str(e)}", "yellow"))
            
            winsound.Beep(500, 300)
            print(colored('\n[Recording... (Release Enter to stop)]', 'yellow'))
            
            # Record directly to a file
            audio_data = r.listen(source)
            
            with open(temp_file.name, 'wb') as f:
                f.write(audio_data.get_wav_data())
            
            is_recording = False
            winsound.Beep(500, 300)
            print(colored('[Recording stopped]', 'yellow'))
            time.sleep(0.1)
            winsound.Beep(500, 300)

            return temp_file.name
    except Exception as e:
        print(colored(f"Recording error: {str(e)}", "red"))
        is_recording = False
        return None
    

def shorten_text(text, limit=500):
    if len(text) <= limit:
        return text  # No need to cut if it's already short

    short_text = text[:limit]  # Cut at 500 characters
    period_index = short_text.rfind('.')  # Find the last period before the limit

    if period_index != -1:
        return short_text[:period_index + 1]  # Include the period
    else:
        return short_text  # If no period found, return as is

def process_recording(audio_path):
    """Process the recorded audio"""
    if not audio_path or not os.path.exists(audio_path):
        print(colored('No audio recorded', 'red'))
        return
    
    try:
        # Convert speech to text
        prompt = wav_to_text(audio_path)
        if not prompt or len(prompt.strip()) == 0:
            print(colored('No speech detected', 'red'))
            return
        
        # Process the prompt
        print(colored("\nUSER:", 'green'))
        print(f'{prompt}')
        
        # Determine which function to call
        call = function_call(prompt)
        visual_context = None
        
        if 'take high quality shot' in call:
            print(colored('\n[Taking HQ screenshot]', 'yellow')) 
            take_high_quality_shot()
        elif 'take screenshot' in call:
            print(colored('\n[Taking screenshot]', 'yellow'))
            take_screenshot()
            visual_context = vision_prompt(prompt=prompt, photo_path='screenshot.jpg')
        elif 'capture webcam' in call:
            print(colored('\n[Capturing webcam]', 'yellow'))
            web_cam_capture()
            visual_context = vision_prompt(prompt=prompt, photo_path='webcam.jpg')
        elif 'extract clipboard' in call:
            print(colored('\n[Copying clipboard text]', 'yellow'))
            paste = get_clipboard_text()
            prompt = f'{prompt}\n\nCLIPBOARD CONTENT: {paste}'
        elif 'open chrome' in call:
            open_chrome()
            print(colored('\n[Opening chrome]', 'yellow'))
            prompt='Respond to me with ONLY: I have opened chrome for you my king'

        # Generate and speak the response
        response = groq_prompt(prompt=prompt, img_context=visual_context)

        if 'provide link' in call:
            print(colored('\n[Providing link]', 'yellow'))
            provide_link(response)

        print(colored("\nASSISTANT:", 'cyan'))
        print(f' {response}')
        speak(shorten_text(response))
    
    except Exception as e:
        print(colored(f"Error: {str(e)}", 'red'))  
    
    finally:
        # Clean up
        try:
            os.remove(audio_path)
        except:
            pass

# Global flag to track middle mouse button press
middle_mouse_pressed = False

def on_click(x, y, button, pressed):
    global middle_mouse_pressed
    if button == mouse.Button.middle:
        middle_mouse_pressed = pressed  # True on press, False on release

# Start the mouse listener in a background thread
mouse.Listener(on_click=on_click).start()

def monitor_enter_key():
    """Monitor the Middle Mouse Button for press and release"""
    global is_recording
    print(colored('\nBitch here, how can I help?', 'magenta'))
    speak("How can I help you?")
    print(colored('\nHold Middle mouse to record your prompt...', 'magenta'))
    print(colored('Release to process your prompt...', 'magenta'))

    while True:
        if keyboard.is_pressed('esc'):
            speak("Goodbye my king and have a lovely day!")
            os.system('cls' if os.name == 'nt' else 'clear')
            sys.exit()
            break

        if middle_mouse_pressed and not is_recording and not speaking_in_progress:
            is_recording = True
            audio_path = record_audio()
            if audio_path:
                process_recording(audio_path)
            is_recording = False  # Reset recording flag after processing
        time.sleep(0.1)


if __name__ == "__main__":
    # Monitor the Enter key
    monitor_enter_key()