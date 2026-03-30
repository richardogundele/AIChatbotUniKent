"""
Azure Speech Services Integration
Provides Text-to-Speech and Speech-to-Text functionality
"""
import os
import azure.cognitiveservices.speech as speechsdk
from fastapi import UploadFile, HTTPException
import tempfile

def get_speech_config():
    """Initialize Azure Speech configuration"""
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION", "uksouth")
    
    if not speech_key:
        raise ValueError("AZURE_SPEECH_KEY not configured")
    
    return speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)

def text_to_speech(text: str) -> bytes:
    """Convert text to speech audio (returns WAV bytes)"""
    try:
        speech_config = get_speech_config()
        
        # Use a natural British English voice
        speech_config.speech_synthesis_voice_name = "en-GB-SoniaNeural"
        
        # Configure audio output to memory stream
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        else:
            raise Exception(f"Speech synthesis failed: {result.reason}")
            
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")

async def speech_to_text(audio_file: UploadFile) -> str:
    """Convert speech audio to text"""
    try:
        speech_config = get_speech_config()
        speech_config.speech_recognition_language = "en-GB"
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Configure audio input
        audio_config = speechsdk.audio.AudioConfig(filename=tmp_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        result = recognizer.recognize_once()
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            raise Exception("No speech could be recognized")
        else:
            raise Exception(f"Speech recognition failed: {result.reason}")
            
    except Exception as e:
        print(f"STT Error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")
