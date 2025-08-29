"""
TTS Generator Module
Converts processed text into audio using text-to-speech technology
Supports both ElevenLabs (legacy) and Speechify APIs
"""

import os
import uuid
import time
import datetime
import base64
from typing import Dict, Any, Optional

from dotenv import load_dotenv

# Try to import ElevenLabs (legacy support)
try:
    from elevenlabs import ElevenLabs, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    print("Warning: ElevenLabs package not available")
    ElevenLabs = None
    VoiceSettings = None
    ELEVENLABS_AVAILABLE = False

# Try to import Speechify (new implementation)
try:
    from speechify import Speechify
    from speechify.tts import GetSpeechOptionsRequest
    SPEECHIFY_AVAILABLE = True
except ImportError:
    print("Warning: Speechify package not available. Please install: pip install speechify-api")
    Speechify = None
    GetSpeechOptionsRequest = None
    SPEECHIFY_AVAILABLE = False


class TTSGenerator:
    def __init__(self, output_dir: str = "./audio_output", tts_provider: str = "speechify"):
        """
        Initialize the TTS generator
        
        Args:
            output_dir: Directory to save audio files
            tts_provider: TTS provider to use ("speechify" or "elevenlabs")
        """
        self.supported_languages = {
            "en": {"voice": "en-US", "rate": 150},  # English only
            "fr-FR": {"voice": "fr-FR", "rate": 150},
            "de-DE": {"voice": "de-DE", "rate": 150},
            "es-ES": {"voice": "es-ES", "rate": 150},
            "pt-BR": {"voice": "pt-BR", "rate": 150},
            "pt-PT": {"voice": "pt-PT", "rate": 150},
            # Beta languages
            "ar-AE": {"voice": "ar-AE", "rate": 150},
            "da-DK": {"voice": "da-DK", "rate": 150},
            "nl-NL": {"voice": "nl-NL", "rate": 150},
            "et-EE": {"voice": "et-EE", "rate": 150},
            "fi-FI": {"voice": "fi-FI", "rate": 150},
            "el-GR": {"voice": "el-GR", "rate": 150},
            "he-IL": {"voice": "he-IL", "rate": 150},
            "hi-IN": {"voice": "hi-IN", "rate": 150},
            "it-IT": {"voice": "it-IT", "rate": 150},
            "ja-JP": {"voice": "ja-JP", "rate": 150},
            "nb-NO": {"voice": "nb-NO", "rate": 150},
            "pl-PL": {"voice": "pl-PL", "rate": 150},
            "ru-RU": {"voice": "ru-RU", "rate": 150},
            "sv-SE": {"voice": "sv-SE", "rate": 150},
            "tr-TR": {"voice": "tr-TR", "rate": 150},
            "uk-UA": {"voice": "uk-UA", "rate": 150},
            "vi-VN": {"voice": "vi-VN", "rate": 150}
        }
        
        self.current_language = "en"
        self.current_rate = 150
        self.output_dir = output_dir
        self.tts_provider = tts_provider.lower()
        
        # Load environment variables
        load_dotenv()
        
        # Initialize API keys
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.speechify_api_key = os.getenv("SPEECHIFY_API_KEY")
        
        # Voice configuration
        self.voice_ids = {
            "narrator": os.getenv("ELEVEN_NARRATOR_VOICE_ID", "pNInz6obpgDQGcFmaJgB"),  # Default Adam voice
            "character": os.getenv("ELEVEN_ACTOR_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"),  # Default Bella voice
            "default": "pNInz6obpgDQGcFmaJgB"  # Adam voice as fallback
        }
        
        # Speechify voice configuration
        self.speechify_voice_ids = {
            "narrator": os.getenv("SPEECHIFY_NARRATOR_VOICE_ID", "scott"),
            "character": os.getenv("SPEECHIFY_CHARACTER_VOICE_ID", "scott"),
            "default": "scott"
        }
        
        # Initialize clients
        self.elevenlabs_client = None
        self.speechify_client = None
        
        # Initialize based on provider preference
        if self.tts_provider == "speechify":
            self._initialize_speechify()
            if not self.speechify_client:
                print("Falling back to ElevenLabs...")
                self.tts_provider = "elevenlabs"
                self._initialize_elevenlabs()
        else:
            self._initialize_elevenlabs()
            if not self.elevenlabs_client:
                print("Falling back to Speechify...")
                self.tts_provider = "speechify"
                self._initialize_speechify()
        
        # Ensure audio output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _initialize_speechify(self):
        """Initialize Speechify client"""
        if not SPEECHIFY_AVAILABLE:
            print("Speechify package not available")
            return
        
        if not self.speechify_api_key:
            print("SPEECHIFY_API_KEY not found in environment variables")
            return
        
        try:
            self.speechify_client = Speechify(token=self.speechify_api_key)
            print("Speechify client initialized successfully")
        except Exception as e:
            print(f"Error: Could not initialize Speechify client: {e}")
    
    def _initialize_elevenlabs(self):
        """Initialize ElevenLabs client"""
        if not ELEVENLABS_AVAILABLE:
            print("ElevenLabs package not available")
            return
        
        if not self.elevenlabs_api_key:
            print("ELEVENLABS_API_KEY not found in environment variables")
            return
        
        try:
            self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)
            print("ElevenLabs client initialized successfully")
        except Exception as e:
            print(f"Error: Could not initialize ElevenLabs client: {e}")
    
    def set_output_directory(self, output_dir: str):
        """Set a new output directory for audio files"""
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Audio output directory set to: {output_dir}")
    
    def configure_tts(self, language: str, rate: int = 150):
        """Configure TTS settings"""
        if language in self.supported_languages:
            self.current_language = language
            self.current_rate = rate
        else:
            print(f"Warning: Language {language} not supported. Using English.")
            self.current_language = "en"
            self.current_rate = rate
    
    def generate_audio_from_script(self, manga_script: "list[dict]", language: str = "en") -> str:
        """
        Generate audio from structured manga script data
        
        Args:
            manga_script: List of dictionaries with 'role' and 'description' keys
            language: Language code
            
        Returns:
            Path to generated audio file
        """
        if not manga_script or len(manga_script) == 0:
            raise ValueError("No script data provided for audio generation")
        
        if self.tts_provider == "speechify":
            if not self.speechify_client:
                raise Exception("Speechify API is not configured. Please set SPEECHIFY_API_KEY environment variable.")
            return self._generate_speechify_audio(manga_script, language)
        else:
            if not self.elevenlabs_client:
                raise Exception("ElevenLabs API is not configured. Please set ELEVENLABS_API_KEY environment variable.")
            return self._generate_elevenlabs_audio(manga_script, language)
    
    def _generate_speechify_audio(self, manga_script: "list[dict]", language: str = "en") -> str:
        """Generate audio using Speechify API"""
        if not self.speechify_client:
            raise Exception("Speechify client not initialized")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"manga_speechify_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        print(f"Processing {len(manga_script)} structured script segments with Speechify...")
        
        # Combine text parts
        combined_text_parts = []
        
        for i, entry in enumerate(manga_script):
            role = entry.get('role', '').lower()
            description = entry.get('description', '').strip()
            
            print(f"Processing entry {i+1}/{len(manga_script)}: {role} - {description[:30]}...")
            
            if not description:
                print(f"  -> Skipping empty description")
                continue
            
            combined_text_parts.append(description)
        
        if not combined_text_parts:
            raise ValueError("No valid segments found in manga script")
        
        print(f"Combined {len(combined_text_parts)} text parts into single audio generation...")
        
        # Join with pauses for better flow
        combined_text = " ... ".join(combined_text_parts)
        
        # Determine voice ID based on language
        voice_id = self.speechify_voice_ids['narrator']
        
        # Determine model based on language
        if language == "en":
            model = "simba-english"
        else:
            model = "simba-multilingual"
        
        print(f"Generating Speechify audio with voice {voice_id}, model {model}...")
        print(f"Text length: {len(combined_text)} characters")
        
        try:
            audio_response = self.speechify_client.tts.audio.speech(
                audio_format="mp3",
                input=combined_text,
                language=language,
                model=model,
                options=GetSpeechOptionsRequest(
                    loudness_normalization=True,
                    text_normalization=True
                ),
                voice_id=voice_id
            )
            
            # Decode audio data
            audio_bytes = base64.b64decode(audio_response.audio_data)
            
            # Save the audio
            save_file_path = f"{self.output_dir}/{base_filename}.mp3"
            
            with open(save_file_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"Speechify audio saved at {save_file_path}")
            
            # Create transcript file
            self._create_transcript_file(base_filename, manga_script, combined_text, "Speechify")
            
            return save_file_path
            
        except Exception as e:
            print(f"Error generating Speechify audio: {e}")
            raise
    
    def _generate_elevenlabs_audio(self, manga_script: "list[dict]", language: str = "en") -> str:
        """Generate audio using ElevenLabs API (legacy method)"""
        if not self.elevenlabs_client or not ELEVENLABS_AVAILABLE or not VoiceSettings:
            raise Exception("ElevenLabs client not properly initialized for multi-voice")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"manga_elevenlabs_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        print(f"Processing {len(manga_script)} structured script segments with ElevenLabs...")
        
        # Combine text parts
        combined_text_parts = []
        
        for i, entry in enumerate(manga_script):
            role = entry.get('role', '').lower()
            description = entry.get('description', '').strip()
            
            print(f"Processing entry {i+1}/{len(manga_script)}: {role} - {description[:30]}...")
            
            if not description:
                print(f"  -> Skipping empty description")
                continue
            
            combined_text_parts.append(description)
        
        if not combined_text_parts:
            raise ValueError("No valid segments found in manga script")
        
        print(f"Combined {len(combined_text_parts)} text parts into single audio generation...")
        
        # Join with pauses for better flow
        combined_text = " ... ".join(combined_text_parts)
        
        print(f"Generating ElevenLabs audio with narrator voice...")
        print(f"Text length: {len(combined_text)} characters")
        
        response = self.elevenlabs_client.text_to_speech.convert(
            voice_id=self.voice_ids['narrator'],
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=combined_text,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=0.2,
                similarity_boost=0.8,
                style=0.4,
                use_speaker_boost=True,
            ),
        )
        
        # Save the audio
        save_file_path = f"{self.output_dir}/{base_filename}.mp3"
        
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        
        print(f"ElevenLabs audio saved at {save_file_path}")
        
        # Create transcript file
        self._create_transcript_file(base_filename, manga_script, combined_text, "ElevenLabs")
        
        return save_file_path
    
    def _create_transcript_file(self, base_filename: str, manga_script: "list[dict]", combined_text: str, provider: str):
        """Create a detailed transcript file"""
        transcript_path = f"{self.output_dir}/{base_filename}_transcript.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(f"STRUCTURED MULTI-VOICE MANGA AUDIO TRANSCRIPT ({provider})\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.datetime.now()}\n")
            f.write(f"Provider: {provider}\n")
            f.write(f"Script Segments: {len(manga_script)}\n")
            f.write(f"Language: {self.current_language}\n")
            f.write(f"Speech Rate: {self.current_rate} WPM\n\n")
            f.write(f"Combined Text ({len(combined_text)} chars):\n")
            f.write(f"{combined_text}\n\n")
            f.write("Original Structured Script:\n")
            
            for i, entry in enumerate(manga_script, 1):
                role = entry.get('role', 'unknown').upper()
                description = entry.get('description', '')
                f.write(f"{i}. [{role}]: {description}\n")
    
    def _has_voice_cues(self, text: str) -> bool:
        """Check if text contains narrator/character voice cues"""
        import re
        # Look for patterns like [narrator text], "Character: dialogue", etc.
        narrator_pattern = r'\[.*?\]'
        character_pattern = r'^[A-Z][a-zA-Z\s]*:\s+'
        
        has_narrator = bool(re.search(narrator_pattern, text))
        has_character = bool(re.search(character_pattern, text, re.MULTILINE))
        
        return has_narrator or has_character
    
    def _parse_script(self, text: str) -> "list[dict]":
        """
        Parse manga script into segments with role assignments.
        
        Args:
            text (str): The manga script text
            
        Returns:
            List of dictionaries with 'role', 'text', and 'voice_id' keys
        """
        import re
        
        segments = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for narrator text (enclosed in brackets)
            narrator_match = re.match(r'\[(.*?)\]', line)
            if narrator_match:
                segments.append({
                    'role': 'narrator',
                    'text': narrator_match.group(1).strip(),
                    'voice_id': self.voice_ids['narrator'] if self.tts_provider == "elevenlabs" else self.speechify_voice_ids['narrator']
                })
                continue
            
            # Check for character dialogue (Character: text)
            character_match = re.match(r'^([A-Z][a-zA-Z\s]*?):\s*(.+)$', line)
            if character_match:
                character_name = character_match.group(1).strip()
                dialogue = character_match.group(2).strip()
                segments.append({
                    'role': 'character',
                    'character_name': character_name,
                    'text': dialogue,
                    'voice_id': self.voice_ids['character'] if self.tts_provider == "elevenlabs" else self.speechify_voice_ids['character']
                })
                continue
            
            # Default: treat as narrator if no specific format
            segments.append({
                'role': 'narrator',
                'text': line,
                'voice_id': self.voice_ids['narrator'] if self.tts_provider == "elevenlabs" else self.speechify_voice_ids['narrator']
            })
        
        return segments
    
    def get_tts_statistics(self, text: str) -> Dict[str, Any]:
        """Get statistics about the text for TTS generation"""
        if not text:
            return {
                "text_length_characters": 0,
                "text_length_words": 0,
                "estimated_duration_seconds": 0,
                "provider": self.tts_provider
            }
        
        words = len(text.split())
        chars = len(text)
        estimated_duration = words / (self.current_rate / 60)  # Convert WPM to words per second
        
        return {
            "text_length_characters": chars,
            "text_length_words": words,
            "estimated_duration_seconds": round(estimated_duration, 1),
            "provider": self.tts_provider
        }
    
    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get information about generated audio file"""
        if not os.path.exists(audio_path):
            return {"exists": False}
        
        file_size = os.path.getsize(audio_path)
        
        return {
            "exists": True,
            "file_path": audio_path,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "type": "Real audio file (MP3)",
            "provider": self.tts_provider
        }
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old audio files from the output directory"""
        audio_dir = self.output_dir
        if not os.path.exists(audio_dir):
            return
        
        cutoff_time = time.time() - (max_age_hours * 3600)
        removed_files = 0
        
        for filename in os.listdir(audio_dir):
            file_path = os.path.join(audio_dir, filename)
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        removed_files += 1
                    except Exception as e:
                        print(f"Could not remove {file_path}: {e}")
        
        print(f"Cleaned up {removed_files} old audio files")
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get available voices for the current provider"""
        if self.tts_provider == "speechify" and self.speechify_client:
            try:
                voice_list = self.speechify_client.tts.voices.list()
                return {
                    "provider": "speechify",
                    "voices": voice_list,
                    "count": len(voice_list) if voice_list else 0
                }
            except Exception as e:
                print(f"Error getting Speechify voices: {e}")
                return {"provider": "speechify", "voices": [], "count": 0}
        else:
            return {
                "provider": "elevenlabs",
                "voices": self.voice_ids,
                "count": len(self.voice_ids)
            }
    
    def filter_voice_models(self, voices, *, gender=None, locale=None, tags=None):
        """
        Filter Speechify voices by gender, locale, and/or tags,
        and return the list of model IDs for matching voices.

        Args:
            voices (list): List of GetVoice objects.
            gender (str, optional): e.g. 'male', 'female'.
            locale (str, optional): e.g. 'en-US'.
            tags (list, optional): list of tags, e.g. ['timbre:deep'].

        Returns:
            list[str]: IDs of matching voice models.
        """
        if not voices:
            return []
            
        results = []

        for voice in voices:
            # gender filter
            if gender and voice.gender.lower() != gender.lower():
                continue

            # locale filter (check across models and languages)
            if locale:
                if not any(
                    any(lang.locale == locale for lang in model.languages)
                    for model in voice.models
                ):
                    continue

            # tags filter
            if tags:
                if not all(tag in voice.tags for tag in tags):
                    continue

            # If we got here, the voice matches -> collect model ids
            for model in voice.models:
                results.append(model.name)

        return results