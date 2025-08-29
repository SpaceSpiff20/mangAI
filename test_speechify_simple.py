#!/usr/bin/env python3
"""
Simple test script for Speechify TTS migration
This script can be run to test the migration without requiring pytest
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.tts_generator import TTSGenerator

# Load environment variables
load_dotenv()


def test_speechify_migration():
    """Test the Speechify migration functionality"""
    print("🧪 Testing Speechify TTS Migration")
    print("=" * 50)
    
    # Test 1: Check if Speechify package is available
    try:
        from speechify import Speechify
        from speechify.tts import GetSpeechOptionsRequest
        print("✅ Speechify package is available")
    except ImportError as e:
        print(f"❌ Speechify package not available: {e}")
        print("Please install with: pip install speechify-api")
        return False
    
    # Test 2: Check API key availability
    speechify_api_key = os.getenv("SPEECHIFY_API_KEY")
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    
    print(f"🔑 Speechify API Key: {'✅ Available' if speechify_api_key else '❌ Not found'}")
    print(f"🔑 ElevenLabs API Key: {'✅ Available' if elevenlabs_api_key else '❌ Not found'}")
    
    if not speechify_api_key and not elevenlabs_api_key:
        print("❌ No API keys available. Please set SPEECHIFY_API_KEY or ELEVENLABS_API_KEY")
        return False
    
    # Test 3: Initialize TTS Generator
    try:
        print("\n🔧 Initializing TTS Generator...")
        tts = TTSGenerator(tts_provider="speechify")
        print(f"✅ TTS Generator initialized with provider: {tts.tts_provider}")
        print(f"✅ Supported languages: {len(tts.supported_languages)}")
        print(f"✅ Current language: {tts.current_language}")
    except Exception as e:
        print(f"❌ Failed to initialize TTS Generator: {e}")
        return False
    
    # Test 4: Test language configuration
    try:
        print("\n🌍 Testing language configuration...")
        tts.configure_tts("en", 150)
        print(f"✅ English configured: {tts.current_language}, rate: {tts.current_rate}")
        
        tts.configure_tts("fr-FR", 140)
        print(f"✅ French configured: {tts.current_language}, rate: {tts.current_rate}")
        
        tts.configure_tts("ja-JP", 130)
        print(f"✅ Japanese configured: {tts.current_language}, rate: {tts.current_rate}")
    except Exception as e:
        print(f"❌ Language configuration failed: {e}")
        return False
    
    # Test 5: Test TTS statistics
    try:
        print("\n📊 Testing TTS statistics...")
        test_text = "This is a test text for TTS generation."
        stats = tts.get_tts_statistics(test_text)
        print(f"✅ TTS Statistics: {stats}")
    except Exception as e:
        print(f"❌ TTS statistics failed: {e}")
        return False
    
    # Test 6: Test script parsing
    try:
        print("\n📝 Testing script parsing...")
        test_script = "[Narrator text]\nCharacter: Hello world!"
        segments = tts._parse_script(test_script)
        print(f"✅ Parsed {len(segments)} script segments")
        for i, segment in enumerate(segments):
            print(f"   {i+1}. {segment['role']}: {segment['text'][:30]}...")
    except Exception as e:
        print(f"❌ Script parsing failed: {e}")
        return False
    
    # Test 7: Test voice availability (if API key is available)
    if speechify_api_key:
        try:
            print("\n🎭 Testing voice availability...")
            voice_info = tts.get_available_voices()
            print(f"✅ Voice info: {voice_info}")
        except Exception as e:
            print(f"⚠️  Voice availability test failed: {e}")
    
    # Test 8: Test audio generation (if API key is available)
    if speechify_api_key:
        try:
            print("\n🎵 Testing audio generation...")
            sample_script = [
                {
                    "role": "narrator",
                    "description": "The sun rises over the quiet village."
                },
                {
                    "role": "character",
                    "description": "Hello, world! This is a test."
                }
            ]
            
            audio_path = tts.generate_audio_from_script(sample_script, "en")
            print(f"✅ Audio generated: {audio_path}")
            
            # Check file info
            audio_info = tts.get_audio_info(audio_path)
            print(f"✅ Audio info: {audio_info}")
            
        except Exception as e:
            print(f"❌ Audio generation failed: {e}")
            return False
    
    print("\n🎉 All tests completed successfully!")
    return True


def test_backward_compatibility():
    """Test backward compatibility with ElevenLabs"""
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 50)
    
    # Test 1: Check if ElevenLabs package is available
    try:
        from elevenlabs import ElevenLabs, VoiceSettings
        print("✅ ElevenLabs package is available")
    except ImportError as e:
        print(f"❌ ElevenLabs package not available: {e}")
        return False
    
    # Test 2: Initialize with ElevenLabs provider
    try:
        print("\n🔧 Initializing TTS Generator with ElevenLabs...")
        tts = TTSGenerator(tts_provider="elevenlabs")
        print(f"✅ TTS Generator initialized with provider: {tts.tts_provider}")
    except Exception as e:
        print(f"❌ Failed to initialize TTS Generator with ElevenLabs: {e}")
        return False
    
    # Test 3: Test audio generation with ElevenLabs (if API key is available)
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    if elevenlabs_api_key:
        try:
            print("\n🎵 Testing ElevenLabs audio generation...")
            sample_script = [
                {
                    "role": "narrator",
                    "description": "The sun rises over the quiet village."
                },
                {
                    "role": "character",
                    "description": "Hello, world! This is a test."
                }
            ]
            
            audio_path = tts.generate_audio_from_script(sample_script, "en")
            print(f"✅ ElevenLabs audio generated: {audio_path}")
            
        except Exception as e:
            print(f"❌ ElevenLabs audio generation failed: {e}")
            return False
    
    print("\n🎉 Backward compatibility tests completed successfully!")
    return True


def main():
    """Main test function"""
    print("🚀 Speechify TTS Migration Test Suite")
    print("=" * 60)
    
    # Test Speechify migration
    speechify_success = test_speechify_migration()
    
    # Test backward compatibility
    compatibility_success = test_backward_compatibility()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"Speechify Migration: {'✅ PASSED' if speechify_success else '❌ FAILED'}")
    print(f"Backward Compatibility: {'✅ PASSED' if compatibility_success else '❌ FAILED'}")
    
    if speechify_success and compatibility_success:
        print("\n🎉 All tests passed! Migration is successful.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main()) 