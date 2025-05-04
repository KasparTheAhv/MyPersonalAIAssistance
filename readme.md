# 🎙️ Multi-Modal Voice Assistant with Mouse Activation

This is a multi-modal AI voice assistant that uses your **microphone, clipboard, screenshots, webcam, and mouse** to interact with you through speech. It integrates with **Groq**, **Gemini (Google Generative AI)**, and **Whisper** to transcribe speech, understand prompts, generate intelligent responses, and use visual context.

---

## 🚀 Features

- 🎤 Voice-controlled prompt input (record by holding **middle mouse**)
- 🖼️ Supports screenshots, webcam captures, and clipboard content
- 🧠 Uses **Groq LLaMA3** and **Gemini 1.5 Flash** for fast, intelligent responses
- 🧾 Link extraction, Chrome automation, and contextual vision AI
- 🔊 Real-time text-to-speech feedback

---

## 🧱 One-Click Dependency Installation

Install all required packages at once using:

```
pip install faster-whisper==1.0.2 groq==0.6.0 openai==1.30.1 google-generativeai==0.5.4 opencv-python==4.9.0.80 Pillow==10.3.0 PyAudio==0.2.14 SpeechRecognition==3.10.1 pyperclip==1.8.2 pyttsx3 pynput termcolor pygetwindow keyboard
```

> ⚠️ Also, install `ffmpeg` if Whisper complains:
> - [FFmpeg for Windows](https://www.gyan.dev/ffmpeg/builds/)
> - Add the `bin/` folder to your system PATH.

---

## 🔐 API Keys Required

Set these in your script by replacing the placeholders:

```python
groq_client = Groq(api_key='INSERT_YOUR_GROQ_API_KEY_HERE')
genai.configure(api_key='INSERT_YOUR_GENERATIVE_AI_API_KEY_HERE')
```

---

## 🖱️ How to Use

1. **Run the script** in a terminal or IDE.
2. You'll hear the assistant say: **"How can I help you?"**
3. **Hold your middle mouse button** to start recording your voice.
4. **Release** it to stop recording and hear the AI's response.
5. Press **ESC** to exit the assistant cleanly.

---

## 🧠 Functional Intelligence

Based on your voice commands, the assistant can:

- 🖼️ **Take a screenshot** → `"take screenshot"`
- 📸 **Capture a webcam image** → `"capture webcam"`
- 📋 **Read clipboard content** → `"extract clipboard"`
- 🌐 **Launch Chrome** → `"open chrome"`
- 🔗 **Extract and return links** → `"provide link"`

Visual inputs are processed into rich prompts using **Gemini**, then passed to **Groq’s LLaMA3** for a final response.

---

## 📂 Files Saved

- `screenshot.jpg`, `HQscreenshot.jpg` — Screenshots (low/high quality)
- `webcam.jpg` — Captured webcam photo
- Temporary `.wav` files — Voice input (auto-deleted after use)

---

## ⚠️ Disclaimers

- This script **records audio** and may access your **clipboard, webcam, or screen**.
- Do **not** use it on shared/public machines without permission.
- Ensure your usage complies with local privacy and surveillance laws.

---

## 🧊 Cool Tip

To change the voice, speed, or personality of the assistant, tweak the `pyttsx3` settings in your code:

```python
engine.setProperty("rate", 250)
engine.setProperty("voice", voices[1].id)
```

---

## 🧵 Coming Soon (Ideas)

- 🎛️ GUI version
- 🗂️ History log of interactions
- 🧩 Plugin support for custom actions

---

## 🙏 Credits

- [Groq](https://groq.com/)
- [Google Gemini](https://ai.google.dev/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Pynput](https://pynput.readthedocs.io/)
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
- [Pyttsx3](https://pyttsx3.readthedocs.io/)

---

> Built for tinkering and personal AI productivity. Stay curious 🧠
