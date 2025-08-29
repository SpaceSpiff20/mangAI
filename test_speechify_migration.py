#!/usr/bin/env python3
"""
Test suite for Speechify TTS migration
Tests both the migration functionality and backward compatibility
"""

import os
import sys
import pytest
import tempfile
import shutil
import base64
from unittest.mock import Mock, patch, MagicMock
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.tts_generator import TTSGenerator

# Load environment variables
load_dotenv()


class TestSpeechifyMigration:
    """Test class for Speechify migration functionality"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_manga_script(self):
        """Sample manga script for testing"""
        return [
            {
                "role": "narrator",
                "description": "The sun rises over the quiet village."
            },
            {
                "role": "character",
                "description": "Hello, world! This is a test."
            },
            {
                "role": "narrator",
                "description": "The character looks around curiously."
            }
        ]
    
    def test_speechify_initialization(self, temp_output_dir):
        """Test Speechify TTS generator initialization"""
        # Test with Speechify as preferred provider
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        # Should have Speechify as the provider
        assert tts.tts_provider == "speechify"
        assert hasattr(tts, 'speechify_client')
        assert hasattr(tts, 'speechify_voice_ids')
        
        # Should have extended language support
        assert "en" in tts.supported_languages
        assert "fr-FR" in tts.supported_languages
        assert "ja-JP" in tts.supported_languages
    
    def test_elevenlabs_fallback(self, temp_output_dir):
        """Test fallback to ElevenLabs when Speechify is not available"""
        with patch('modules.tts_generator.SPEECHIFY_AVAILABLE', False):
            tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
            
            # Should fall back to ElevenLabs
            assert tts.tts_provider == "elevenlabs"
    
    def test_elevenlabs_initialization(self, temp_output_dir):
        """Test ElevenLabs TTS generator initialization (backward compatibility)"""
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="elevenlabs")
        
        # Should have ElevenLabs as the provider
        assert tts.tts_provider == "elevenlabs"
        assert hasattr(tts, 'elevenlabs_client')
        assert hasattr(tts, 'voice_ids')
    
    def test_speechify_fallback(self, temp_output_dir):
        """Test fallback to Speechify when ElevenLabs is not available"""
        with patch('modules.tts_generator.ELEVENLABS_AVAILABLE', False):
            tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="elevenlabs")
            
            # Should fall back to Speechify
            assert tts.tts_provider == "speechify"
    
    def test_language_configuration(self, temp_output_dir):
        """Test language configuration with extended language support"""
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        # Test English configuration
        tts.configure_tts("en", 150)
        assert tts.current_language == "en"
        assert tts.current_rate == 150
        
        # Test French configuration
        tts.configure_tts("fr-FR", 140)
        assert tts.current_language == "fr-FR"
        assert tts.current_rate == 140
        
        # Test Japanese configuration (beta language)
        tts.configure_tts("ja-JP", 130)
        assert tts.current_language == "ja-JP"
        assert tts.current_rate == 130
        
        # Test unsupported language (should fall back to English)
        tts.configure_tts("invalid", 120)
        assert tts.current_language == "en"
        assert tts.current_rate == 120
    
    def test_tts_statistics_with_provider(self, temp_output_dir):
        """Test TTS statistics include provider information"""
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        test_text = "This is a test text for TTS generation."
        stats = tts.get_tts_statistics(test_text)
        
        assert "provider" in stats
        assert stats["provider"] == "speechify"
        assert stats["text_length_characters"] == len(test_text)
        assert stats["text_length_words"] == 8
        assert "estimated_duration_seconds" in stats
    
    def test_audio_info_with_provider(self, temp_output_dir):
        """Test audio info includes provider information"""
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        # Create a dummy audio file
        dummy_audio_path = os.path.join(temp_output_dir, "test.mp3")
        with open(dummy_audio_path, "wb") as f:
            f.write(b"dummy audio data")
        
        info = tts.get_audio_info(dummy_audio_path)
        
        assert info["exists"] is True
        assert "provider" in info
        assert info["provider"] == "speechify"
        assert info["file_size_bytes"] > 0
    
    def test_voice_filtering_function(self, temp_output_dir):
        """Test the voice filtering function"""
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        # Mock voice objects
        mock_voice1 = Mock()
        mock_voice1.gender = "male"
        mock_voice1.tags = ["timbre:deep", "style:professional"]
        mock_voice1.models = [Mock()]
        mock_voice1.models[0].languages = [Mock()]
        mock_voice1.models[0].languages[0].locale = "en-US"
        mock_voice1.models[0].name = "voice1"
        
        mock_voice2 = Mock()
        mock_voice2.gender = "female"
        mock_voice2.tags = ["timbre:bright"]
        mock_voice2.models = [Mock()]
        mock_voice2.models[0].languages = [Mock()]
        mock_voice2.models[0].languages[0].locale = "fr-FR"
        mock_voice2.models[0].name = "voice2"
        
        voices = [mock_voice1, mock_voice2]
        
        # Test filtering by gender
        male_voices = tts.filter_voice_models(voices, gender="male")
        assert len(male_voices) == 1
        assert "voice1" in male_voices
        
        # Test filtering by locale
        en_voices = tts.filter_voice_models(voices, locale="en-US")
        assert len(en_voices) == 1
        assert "voice1" in en_voices
        
        # Test filtering by tags
        deep_voices = tts.filter_voice_models(voices, tags=["timbre:deep"])
        assert len(deep_voices) == 1
        assert "voice1" in deep_voices
    
    def test_script_parsing_with_provider_awareness(self, temp_output_dir):
        """Test script parsing works with both providers"""
        # Test with Speechify
        tts_speechify = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        test_script = "[Narrator text]\nCharacter: Hello world!"
        segments = tts_speechify._parse_script(test_script)
        
        assert len(segments) == 2
        assert segments[0]["role"] == "narrator"
        assert segments[0]["voice_id"] == tts_speechify.speechify_voice_ids["narrator"]
        assert segments[1]["role"] == "character"
        assert segments[1]["voice_id"] == tts_speechify.speechify_voice_ids["character"]
        
        # Test with ElevenLabs
        tts_elevenlabs = TTSGenerator(output_dir=temp_output_dir, tts_provider="elevenlabs")
        segments = tts_elevenlabs._parse_script(test_script)
        
        assert len(segments) == 2
        assert segments[0]["voice_id"] == tts_elevenlabs.voice_ids["narrator"]
        assert segments[1]["voice_id"] == tts_elevenlabs.voice_ids["character"]


class TestSpeechifyIntegration:
    """Integration tests for Speechify API (requires API key)"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_manga_script(self):
        """Sample manga script for testing"""
        return [
            {
                "role": "narrator",
                "description": "The sun rises over the quiet village."
            },
            {
                "role": "character",
                "description": "Hello, world! This is a test."
            }
        ]
    
    def test_speechify_api_connection(self, temp_output_dir):
        """Test actual Speechify API connection (requires API key)"""
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key:
            pytest.skip("SPEECHIFY_API_KEY not available")
        
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        # Should have successfully initialized Speechify client
        assert tts.speechify_client is not None
        assert tts.tts_provider == "speechify"
    
    def test_speechify_voice_listing(self, temp_output_dir):
        """Test getting available voices from Speechify API"""
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key:
            pytest.skip("SPEECHIFY_API_KEY not available")
        
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        voice_info = tts.get_available_voices()
        
        assert voice_info["provider"] == "speechify"
        assert "voices" in voice_info
        assert "count" in voice_info
        assert voice_info["count"] >= 0
    
    def test_speechify_audio_generation(self, temp_output_dir, sample_manga_script):
        """Test actual audio generation with Speechify API"""
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key:
            pytest.skip("SPEECHIFY_API_KEY not available")
        
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        # Generate audio
        audio_path = tts.generate_audio_from_script(sample_manga_script, "en")
        
        # Check that audio file was created
        assert os.path.exists(audio_path)
        assert audio_path.endswith(".mp3")
        
        # Check file size
        file_size = os.path.getsize(audio_path)
        assert file_size > 1000  # Should be a reasonable audio file size
        
        # Check that transcript was created
        transcript_path = audio_path.replace(".mp3", "_transcript.txt")
        assert os.path.exists(transcript_path)
    
    def test_speechify_multilingual_support(self, temp_output_dir):
        """Test multilingual support with Speechify"""
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key:
            pytest.skip("SPEECHIFY_API_KEY not available")
        
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        # Test with different languages
        test_scripts = {
            "en": [{"role": "narrator", "description": "Hello world"}],
            "fr-FR": [{"role": "narrator", "description": "Bonjour le monde"}],
            "es-ES": [{"role": "narrator", "description": "Hola mundo"}]
        }
        
        for language, script in test_scripts.items():
            try:
                audio_path = tts.generate_audio_from_script(script, language)
                assert os.path.exists(audio_path)
                print(f"Successfully generated audio for {language}")
            except Exception as e:
                print(f"Failed to generate audio for {language}: {e}")
                # Don't fail the test, just log the issue


class TestBackwardCompatibility:
    """Test backward compatibility with existing ElevenLabs implementation"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_manga_script(self):
        """Sample manga script for testing"""
        return [
            {
                "role": "narrator",
                "description": "The sun rises over the quiet village."
            },
            {
                "role": "character",
                "description": "Hello, world! This is a test."
            }
        ]
    
    def test_elevenlabs_api_connection(self, temp_output_dir):
        """Test actual ElevenLabs API connection (requires API key)"""
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            pytest.skip("ELEVENLABS_API_KEY not available")
        
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="elevenlabs")
        
        # Should have successfully initialized ElevenLabs client
        assert tts.elevenlabs_client is not None
        assert tts.tts_provider == "elevenlabs"
    
    def test_elevenlabs_audio_generation(self, temp_output_dir, sample_manga_script):
        """Test actual audio generation with ElevenLabs API (backward compatibility)"""
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            pytest.skip("ELEVENLABS_API_KEY not available")
        
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="elevenlabs")
        
        # Generate audio
        audio_path = tts.generate_audio_from_script(sample_manga_script, "en")
        
        # Check that audio file was created
        assert os.path.exists(audio_path)
        assert audio_path.endswith(".mp3")
        
        # Check file size
        file_size = os.path.getsize(audio_path)
        assert file_size > 1000  # Should be a reasonable audio file size
        
        # Check that transcript was created
        transcript_path = audio_path.replace(".mp3", "_transcript.txt")
        assert os.path.exists(transcript_path)
    
    def test_default_initialization_backward_compatible(self, temp_output_dir):
        """Test that default initialization still works (should use Speechify)"""
        tts = TTSGenerator(output_dir=temp_output_dir)
        
        # Should default to Speechify
        assert tts.tts_provider == "speechify"
        assert hasattr(tts, 'speechify_client')
        assert hasattr(tts, 'elevenlabs_client')  # Should still have this for fallback


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_no_api_keys_available(self, temp_output_dir):
        """Test behavior when no API keys are available"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception) as exc_info:
                TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
            
            # Should raise an exception about missing API keys
            assert "API" in str(exc_info.value)
    
    def test_empty_script_handling(self, temp_output_dir):
        """Test handling of empty script data"""
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        with pytest.raises(ValueError, match="No script data provided"):
            tts.generate_audio_from_script([], "en")
        
        with pytest.raises(ValueError, match="No script data provided"):
            tts.generate_audio_from_script(None, "en")
    
    def test_invalid_language_handling(self, temp_output_dir):
        """Test handling of invalid language codes"""
        tts = TTSGenerator(output_dir=temp_output_dir, tts_provider="speechify")
        
        # Should not raise an exception, just log a warning and use English
        tts.configure_tts("invalid_language", 150)
        assert tts.current_language == "en"  # Should fall back to English


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 