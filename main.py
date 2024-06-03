import gradio as gr
import os
import numpy as np
import matplotlib.pyplot as plt
from textblob import TextBlob
import nltk
from pydub import AudioSegment
import pyttsx3
from silero_tts import text_to_speech_silero, speakers
from text_to_ssml import TextToSSMLConverter

# Загрузка ресурсов NLTK
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

def get_wordnet_pos(word):
    """
    Map POS tag to first character lemmatize() accepts.
    """
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def text_to_speech_pyttsx3(ssml, language, speed, pitch):
    """
    Convert SSML text to speech using pyttsx3.
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    for voice in voices:
        if language in voice.languages:
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', int(engine.getProperty('rate') * speed))
    engine.setProperty('pitch', pitch)
    engine.save_to_file(ssml, 'output.wav')
    engine.runAndWait()
    
    sound = AudioSegment.from_file('output.wav', format='wav')
    sound.export('output.mp3', format='mp3')
    
    return 'output.mp3'

def plot_waveform(file_path):
    """
    Plot the waveform of an audio file.
    """
    sound = AudioSegment.from_file(file_path)
    samples = np.array(sound.get_array_of_samples())
    
    plt.figure(figsize=(10, 4))
    plt.plot(samples)
    plt.title('Waveform')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    
    waveform_path = 'waveform.png'
    plt.savefig(waveform_path)
    plt.close()
    
    return waveform_path

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        sentiment = 'Positive'
    elif polarity < 0:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    return sentiment

def update_speakers(language):
    """
    Update the list of available speakers for the given language.
    """
    return speakers.get(language, [])

def process_text(text, language, speaker, speed, pitch, tts_method):
    """
    Process the input text and generate speech, waveform, and sentiment analysis.
    """
    converter = TextToSSMLConverter()
    ssml_parts = converter.process_long_text(text)
    
    if tts_method == 'pyttsx3':
        audio_path = text_to_speech_pyttsx3(ssml_parts, language, speed, pitch)
    else:
        audio_path = text_to_speech_silero(ssml_parts, language, speaker)
    
    waveform_path = plot_waveform(audio_path)
    sentiment = analyze_sentiment(text)
    
    return audio_path, waveform_path, sentiment

def update_speakers_and_refresh(language):
    """
    Update speakers dropdown based on the selected language.
    """
    speakers = update_speakers(language)
    return gr.Dropdown(choices=speakers, value=speakers[0] if speakers else None)

# Создание интерфейса Gradio
with gr.Blocks() as iface:
    language_input = gr.Dropdown(choices=['en', 'ru', 'fr', 'de', 'es'], label='Выберите язык', value='en')
    speaker_input = gr.Dropdown(choices=update_speakers('en'), label='Выберите диктора')
    text_input = gr.Textbox(lines=2, placeholder='Введите текст здесь...')
    speed_input = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, label='Скорость')
    pitch_input = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, label='Высота голоса')
    tts_method_input = gr.Radio(choices=['pyttsx3', 'Silero'], label='Метод озвучивания', value='pyttsx3')

    language_input.change(fn=update_speakers_and_refresh, inputs=language_input, outputs=speaker_input)

    output_audio = gr.Audio(type='filepath')
    output_waveform = gr.Image(type='filepath', label='Визуализация звуковой волны')
    output_sentiment = gr.Textbox(label='Анализ тональности текста')

    submit_button = gr.Button("Преобразовать текст в речь")

    submit_button.click(
        fn=process_text,
        inputs=[text_input, language_input, speaker_input, speed_input, pitch_input, tts_method_input],
        outputs=[output_audio, output_waveform, output_sentiment]
    )

iface.launch(share=False)
