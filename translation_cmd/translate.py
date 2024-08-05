import tempfile
import os

from transformers import MarianMTModel, MarianTokenizer
from TTS.api import TTS
import whisper
from pydub import AudioSegment

# UI Elements for file selection
import tkinter as tk
from tkinter import filedialog

# Create temp dir
temp_dir = tempfile.TemporaryDirectory()

### Language Mapping
nlp_codes = {
  'English': 'en',
  'Spanish': 'es',
  'French': 'fr',
  'Italian': 'it',
  'German': 'de',
  'Arabic': 'ar',
  'Chinese': 'zh',
  'Hindi': 'hi',
  'Russian': 'ru',
  'Japanese': 'ja',
}

### Non-Standard Model Names:
# es-zh, fr-it, en-ja tatoeba
# zh-ja uses tc-big
nlp_nonstandard = {
  ('es', 'zh'): 'Helsinki-NLP/opus-tatoeba',
  ('fr', 'it'): 'Helsinki-NLP/opus-tatoeba',
  ('en', 'ja'): 'Helsinki-NLP/opus-tatoeba',
  ('zj', 'ja'): 'Helsinki-NLP/opus-mt-tc-big',
}

### Unavailable
# es-hi, es-ja
# fr-zh, fr-hi, fr-ja
# it-zh, it-hi, it-ru, it-ja
# de-hi, de-ru, de-ja
# ar-zh, ar-hi, ar-ja
# zh-es, zh-fr, zh-ar, zh-hi, zh-ru
# hi-es, hi-fr, hi-it, hi-de, hi-ar, hi-zh, hi-ru, hi-ja
# ru-it, ru-de, ru-zh, ru-hi, ru-ja
# ja-zh, ja-hi
nlp_unavail = {
  ('es', 'hi'), ('es', 'ja'),
  ('fr', 'zh'), ('fr', 'hi'), ('fr', 'ja'),
  ('it', 'zh'), ('it', 'hi'), ('it', 'ru'), ('it', 'ja'),
  ('de', 'hi'), ('de', 'ru'), ('de', 'ja'),
  ('ar', 'zh'), ('ar', 'hi'), ('ar', 'ja'),
  ('zh', 'es'), ('zh', 'fr'), ('zh', 'ar'), ('zh', 'hi'), ('zh', 'ru'),
  ('hi', 'es'), ('hi', 'fr'), ('hi', 'it'), ('hi', 'de'), ('hi', 'ar'), ('hi', 'zh'), ('hi', 'ru'), ('hi', 'ja'),
  ('ru', 'it'), ('ru', 'de'), ('ru', 'zh'), ('ru', 'hi'), ('ru', 'ja'),
  ('ja', 'zh'), ('ja', 'hi')
}

### Change audio format to wav if not already
def convert_wav(audio):
  # Set path
  dir, filename = os.path.split(audio)
  base_filename, ext = os.path.splitext(filename)

  wav_path = os.path.join(dir, base_filename + '.wav')

  # Check if already wav file
  if ext.lower() == '.wav':
    return audio

  # If not wav file
  raw = AudioSegment.from_file(audio)
  raw.export(wav_path, format='wav')

  # Remove original
  os.remove(audio)

  return wav_path

### Audio transcription function
def transcribe(audio, model_type = 'base', dir = temp_dir.name):
  base_filename = os.path.splitext(os.path.basename(audio))[0]
  transcribed_filename = os.path.join(dir, base_filename + '.txt')

  # Assignments
  whisper_model = whisper.load_model(model_type, device="cuda")
  transcribed = whisper_model.transcribe(audio)

  with open(transcribed_filename, 'w') as file:
    for segment in transcribed['segments']:
      start = segment['start']
      end = segment['end']
      text = segment['text']
      file.write(f"[{start:.2f}-{end:.2f}] {text}\n")

  #print(transcribed['text'])

  return transcribed_filename

### Merge timestamps & lines into single line w/ only text
def merge_lines(transcribed):

  # Get lines from file & merge
  with open(transcribed, 'r') as file:
    lines = file.readlines()
    merged = ' '.join([line.split('] ')[1].strip() for line in lines if '] ' in line])

  # Write merged line to file
  with open(transcribed, 'w') as file:
    file.write(merged)

### Define Model Paths
def model_name(init_lang, target_lang):
  if (init_lang, target_lang) in nlp_nonstandard:
    base_model = nlp_nonstandard[(init_lang, target_lang)]
    nlp_model = f'{base_model}-{init_lang}-{target_lang}'
    return nlp_model

  # No direct translation
  elif (init_lang, target_lang) in nlp_unavail:
    # Check if initial language -> English uses non-standard model name
    if (init_lang, 'en') in nlp_nonstandard:
      base_model_1 = nlp_nonstandard[(init_lang, 'en')]
      nlp_model_1 = f'{base_model_1}-{init_lang}-en'
    else:
      nlp_model_1 = f'Helsinki-NLP/opus-mt-{init_lang}-en'

    # Check if English -> translated language uses non-standard model name
    if ('en', target_lang) in nlp_nonstandard:
      base_model_2 = nlp_nonstandard[('en', target_lang)]
      nlp_model_2 = f'{base_model_2}-en-{target_lang}'
    else:
      nlp_model_2 = f'Helsinki-NLP/opus-mt-en-{target_lang}'

    return (nlp_model_1, nlp_model_2)

  # Direct translation
  else:
    nlp_model = f'Helsinki-NLP/opus-mt-{init_lang}-{target_lang}'
    return nlp_model

### Load Model & Tokenizer
def model_init(nlp_model):
  # If not direct path
  if isinstance(nlp_model, tuple):
    tokenizer1 = MarianTokenizer.from_pretrained(nlp_model[0])
    model1 = MarianMTModel.from_pretrained(nlp_model[0])

    tokenizer2 = MarianTokenizer.from_pretrained(nlp_model[1])
    model2 = MarianMTModel.from_pretrained(nlp_model[1])

    return [(tokenizer1, model1), (tokenizer2, model2)]

  # Direct path
  else:
    tokenizer = MarianTokenizer.from_pretrained(nlp_model)
    model = MarianMTModel.from_pretrained(nlp_model)

    return [(tokenizer, model)]

### Translate txt file to selected language
def translate_text(transcribed, tokenizer, model, dir = temp_dir.name):

  with open(transcribed, "r") as file:
    text = file.read()

  # Translate text
  model_inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="longest")
  translated = model.generate(**model_inputs)
  translated_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

  # Create translated txt file
  name, ext = os.path.splitext(transcribed)
  translated_filename = f"{name}-Translation{ext}"
  translated = os.path.join(dir, translated_filename)

  with open(translated, 'w', encoding='utf-8') as file:
    file.write(translated_text)

  print(translated_text)

  return translated

# Generate translated & cloned speech
def generate_speech(translated_text, audio, target_lang):

  # Set to 'saved' folder

  saved_folder = os.path.join("./", "saved")

  if not os.path.exists(saved_folder):
    os.makedirs(saved_folder)

  # Create translated wav file
  name, ext = os.path.splitext(os.path.basename(audio))
  translated_audio_filename = f"{name}-Translation{ext}"
  print(translated_audio_filename)
  translated_audio = os.path.join(saved_folder, translated_audio_filename)

  with open(translated_text, "r", encoding='utf-8') as file:
    text = file.read()

  # Initialize model
  tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")

  # Translate text
  tts.tts_to_file(text=text,
    file_path=translated_audio,
    speaker_wav=audio,
    language=target_lang
  )

  return translated_audio

def main():
    # Print available languages
    print("Select the initial language:")
    for idx, lang in enumerate(nlp_codes.keys(), start=1):
        print(f"{idx}. {lang}")

    # Get initial language selection from the user
    init_lang_idx = int(input("Enter the number for the initial language: ")) - 1
    init_lang = list(nlp_codes.keys())[init_lang_idx]

    # Print available languages again for target selection
    print("\nSelect the target language:")
    for idx, lang in enumerate(nlp_codes.keys(), start=1):
        print(f"{idx}. {lang}")

    # Get target language selection from the user
    target_lang_idx = int(input("Enter the number for the target language: ")) - 1
    target_lang = list(nlp_codes.keys())[target_lang_idx]
    print("\n")

    # Get input audio file path from the user
    #input_audio = input("Enter the path to the input audio file: ")
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    input_audio = filedialog.askopenfilename(title="Select the input audio file")
    print(f"Input audio file: {input_audio}\n")

    # Ensure audio is wav format
    input_audio = convert_wav(input_audio)

    # Transcribe audio
    transcribed = transcribe(input_audio)

    # Merge lines in transcribed text
    merge_lines(transcribed)

    # Get model name(s) from direct / indirect path
    nlp_model = model_name(nlp_codes[init_lang], nlp_codes[target_lang])

    init_results = model_init(nlp_model)

    # Check if direct / indirect path & translate accordingly
    # Direct path
    if len(init_results) == 1:
        tokenizer, model = init_results[0]
        translated_text = translate_text(transcribed, tokenizer, model)
    # Indirect path
    else:
        tokenizer1, model1 = init_results[0]
        intermediate_text = translate_text(transcribed, tokenizer1, model1)

        tokenizer2, model2 = init_results[1]
        translated_text = translate_text(intermediate_text, tokenizer2, model2)

    # Generate translated speech
    translated_audio = generate_speech(translated_text, input_audio, nlp_codes[target_lang])

    print(f"Translated audio saved to: {translated_audio}")

    # Open Saved Folder
    os.startfile(translated_audio)

if __name__ == '__main__':
  main()