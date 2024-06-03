import torch
import soundfile as sf
from pydub import AudioSegment
import xml.etree.ElementTree as ET

# Загрузка моделей для разных языков и дикторов
models = {
    'ru': 'v3_1_ru',
    'en': 'v3_en',
    'de': 'v3_de',
    'es': 'v3_es',
    'fr': 'v3_fr'
}

speakers = {
    'ru': ['baya', 'aidar', 'xenia', 'eugene'],
    'en': ['lj', 'blizzard_fls'],
    'de': ['thorsten'],
    'es': ['tux'],
    'fr': ['gilles']
}

def text_to_speech_silero(ssml_parts, language, speaker):
    """
    Convert SSML text to speech using Silero TTS.
    """
    model_id = models[language]
    model, _ = torch.hub.load('snakers4/silero-models', 'silero_tts', language=language, speaker=model_id)
    model.to(torch.device('cpu'))

    audio_segments = []
    print(f"Processing SSML parts: {ssml_parts}")

    if isinstance(ssml_parts, list):
        for part in ssml_parts:
            print(f"Processing part: {part}")
            if not is_valid_xml(part):
                raise ValueError(f"Invalid XML format in SSML part: {part}")

            try:
                audio = model.apply_tts(ssml_text=part, sample_rate=48000, speaker=speaker)
                audio_np = audio.cpu().numpy()
                sf.write('output_part.wav', audio_np, 48000)
                sound = AudioSegment.from_file('output_part.wav', format='wav')
                audio_segments.append(sound)
            except Exception as e:
                print(f"Error processing SSML part: {part}\nError: {e}")

        if audio_segments:
            combined_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                combined_audio += segment
            combined_audio.export('output.mp3', format='mp3')
        else:
            raise ValueError("No valid audio segments generated")
        return 'output.mp3'
    elif isinstance(ssml_parts, str):
        part = ssml_parts
        if not is_valid_xml(part):
            raise ValueError(f"Invalid XML format in SSML part: {part}")
        try:
            audio = model.apply_tts(ssml_text=part, sample_rate=48000, speaker=speaker)
            audio_np = audio.cpu().numpy()
            sf.write('output_part.wav', audio_np, 48000)
            sound = AudioSegment.from_file('output_part.wav', format='wav')
            sound.export('output.mp3', format='mp3')
        except Exception as e:
            print(f"Error processing SSML part: {part}\nError: {e}")
    else:
        raise ValueError("Invalid type for ssml_parts")
    return 'output.mp3'

def is_valid_xml(xml):
    """
    Check if the provided string is a valid XML.
    """
    try:
        ET.fromstring(xml)
        return True
    except ET.ParseError:
        return False
