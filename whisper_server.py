import pyaudio
import wave
import keyboard
import os
import time
import faster_whisper
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import difflib
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import string

# Initialize NLTK
nltk.download('punkt')
nltk.download('wordnet')

# Configuration
FILLER_WORDS = {
    'the', 'a', 'an', 'it', 'and', 'as', 'or', 'is', 'are', 'was', 'were', "in", 
    "with", "of", "are", "that", 'um', 'uh', 'ah', 'like', 'you know', 'i mean', 
    'so', 'well', "this", "is", "are", "which"
}

# Reference text
reference_text = """





because the irreversible reactions in which all the concentrations of
reactant substances are consumed and transformed into products, so the
concentrations of products are very big and since the relationship is directly proportional
between the concentration of products and the equilibrium constant. then the
equilibrium constant will be very big.



"""

# Initialize Flask server
app = Flask(__name__)
CORS(app)
current_transcription = ""
reference_text = reference_text.lower()

def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

def get_similarity_rating(expected, actual):
    if not actual:
        return 'l'
    
    if expected.lower() == actual.lower():
        return 'h'
    
    close_matches = difflib.get_close_matches(actual.lower(), [expected.lower()], cutoff=0.7)
    if close_matches:
        return 'm'
    
    return 'l'

def split_merged_words(spoken_text, reference_words):
    spoken_words = spoken_text.split()
    corrected_words = []
    ref_index = 0
    
    for word in spoken_words:
        if ref_index >= len(reference_words):
            corrected_words.append(word)
            continue
            
        if word.lower() == reference_words[ref_index].lower():
            corrected_words.append(word)
            ref_index += 1
            continue
            
        possible_merge = False
        merge_length = min(3, len(reference_words) - ref_index)
        
        for i in range(1, merge_length + 1):
            merged_ref = ''.join(reference_words[ref_index:ref_index+i]).lower()
            if word.lower() == merged_ref:
                corrected_words.extend(reference_words[ref_index:ref_index+i])
                ref_index += i
                possible_merge = True
                break
                
        if not possible_merge:
            corrected_words.append(word)
            ref_index += 1
            
    return ' '.join(corrected_words)

def remove_word_and_before(text, target):
    words = text
    result = []
    i = 0
    while i < len(words):
        if words[i] == target:
            if result:
                result.pop()
            i += 1
        else:
            result.append(words[i])
            i += 1
    return result

def compare_strings(reference, spoken):
    words_ref = word_tokenize(reference.lower())
    words_spoken = word_tokenize(spoken.lower())
    
    words_ref = [w for w in words_ref if w not in FILLER_WORDS and w.isalpha()]
    words_spoken = [w for w in words_spoken if w not in FILLER_WORDS and w.isalpha()]
    words_spoken = remove_word_and_before(words_spoken, "remove")
    
    aligned_spoken = []
    ref_idx = 0
    spk_idx = 0
    
    while ref_idx < len(words_ref) and spk_idx < len(words_spoken):
        ref_word = words_ref[ref_idx]
        spk_word = words_spoken[spk_idx]
        
        if ref_word == spk_word:
            aligned_spoken.append(spk_word)
            ref_idx += 1
            spk_idx += 1
            continue
            
        merged = False
        for lookahead in range(1, min(3, len(words_ref) - ref_idx) + 1):
            merged_ref = ''.join(words_ref[ref_idx:ref_idx+lookahead])
            if merged_ref == spk_word:
                aligned_spoken.extend(words_ref[ref_idx:ref_idx+lookahead])
                ref_idx += lookahead
                spk_idx += 1
                merged = True
                break
                
        if not merged:
            aligned_spoken.append(spk_word)
            ref_idx += 1
            spk_idx += 1
    
    while spk_idx < len(words_spoken):
        aligned_spoken.append(words_spoken[spk_idx])
        spk_idx += 1
    
    result = []
    for i, word in enumerate(aligned_spoken):
        expected = words_ref[i] if i < len(words_ref) else ""
        rate = get_similarity_rating(expected, word)
        result.append({
            "word": word,
            "rate": rate,
            "expected": expected
        })
    return result

@app.route('/get_transcription')
def get_transcription():
    return jsonify({
        "text": current_transcription,
        "reference": reference_text,
        "comparison": compare_strings(reference_text, current_transcription)
    })

def run_flask():
    app.run(port=5000, use_reloader=False)

# Start Flask in background
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Load Whisper model
model = faster_whisper.WhisperModel("base", device="cuda", compute_type="float16")
print("Whisper model loaded")

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_KEY = 'pagedown'
OUTPUT_FILENAME = "record.wav"

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print(f"Press and hold '{RECORD_KEY}' to record. Release to stop. Press 'esc' to exit.")

try:
    while True:
        frames = []

        if keyboard.is_pressed(RECORD_KEY):
            print("Recording...")
            while keyboard.is_pressed(RECORD_KEY):
                data = stream.read(CHUNK)
                frames.append(data)
            
            print("Recording stopped. Processing...")
            start_time = time.time()

            with wave.open(OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            segments, info = model.transcribe(OUTPUT_FILENAME, "en", initial_prompt=reference_text)
            full_text = " ".join(segment.text for segment in segments)
            clean_text = remove_punctuation(full_text)
            
            # Process the text to handle merged words
            reference_words = word_tokenize(reference_text.lower())
            reference_words = [w for w in reference_words if w not in FILLER_WORDS and w.isalpha()]
            clean_text = split_merged_words(clean_text, reference_words)
            
            current_transcription = clean_text
            
            print("\nTranscription:")
            print(full_text)
            print("\nProcessed Transcription:")
            print(clean_text)
            
            os.remove(OUTPUT_FILENAME)
            print(f"Processing time: {time.time()-start_time:.2f}s")

        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break

except KeyboardInterrupt:
    print("Interrupted by user.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()