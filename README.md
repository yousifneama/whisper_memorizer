# 🎙 Whisper Memorizer

**Whisper Memorizer** is a **real-time speech transcription and memorization tool** built with **Python**, **Faster Whisper**, and **Flask**. It allows users to record their voice, transcribe it using AI, and compare it against a reference text with detailed feedback on word-level accuracy. Perfect for **learning, practicing speeches, or language memorization**.

---
![App Screenshot](./screenshot.png)

## 🧾 Features

- 🎤 **Real-time voice recording** via keyboard (PageDown key)  
- 🔹 **Transcription using Faster Whisper** for fast and accurate speech-to-text  
- 🔹 **Word-by-word comparison** with a reference text  
- 🔹 Highlights words as:  
  - ✅ **Correct** (exact match)  
  - ⚠️ **Partial match**  
  - ❌ **Incorrect**  
- 🔹 Removes filler words automatically for cleaner analysis  
- 🔹 Detects **merged words** and aligns them with reference  
- 🌐 **Live web dashboard** built with Flask and JavaScript for visualization  
- 🔹 Calculates **accuracy percentage** in real-time  
- 🔹 Keyboard controls for recording, stopping, and toggling reference display  

---

## 🛠️ Technologies Used

| Technology      | Purpose |
|-----------------|---------|
| Python          | Core programming language |
| PyAudio         | Audio recording |
| Faster Whisper  | High-performance Whisper speech-to-text model |
| Flask & CORS    | Web server for live transcription dashboard |
| NLTK            | Tokenization & NLP processing |
| JavaScript/HTML | Frontend visualization and word highlighting |

---

## 📌 How It Works

1. **Recording Audio**  
   Press and hold **PageDown** to record your speech. Release to stop recording.  

2. **Transcription**  
   Audio is processed by the **Faster Whisper model** to generate text.  

3. **Text Processing**  
   - Removes punctuation and filler words  
   - Handles merged words  
   - Tokenizes words for comparison  

4. **Comparison & Scoring**  
   - Compares spoken words against a reference text  
   - Rates each word as:  
     - `h` → High / Correct  
     - `m` → Medium / Partial  
     - `l` → Low / Incorrect  

5. **Live Dashboard**  
   - Displays reference text and spoken text side by side  
   - Highlights word accuracy with colors (green, yellow, red)  
   - Calculates overall accuracy percentage  

---

## 🚀 Setup & Installation

1. **Clone the repository**

```bash
git clone https://github.com/yousifneama/whisper_memorizer.git
cd whisper_memorizer
