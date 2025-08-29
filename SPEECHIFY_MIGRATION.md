# Speechify TTS Migration Documentation

## Overview

This document describes the migration from ElevenLabs to Speechify API for text-to-speech functionality in the MangAI application. The migration maintains backward compatibility while adding support for multiple languages and improved voice quality.

## Migration Features

### ✅ What's New
- **Multi-language Support**: Support for 20+ languages including English, French, German, Spanish, Japanese, and more
- **Improved Voice Quality**: Speechify's advanced TTS models provide better audio quality
- **Automatic Language Detection**: Speechify can automatically detect and handle mixed-language content
- **Backward Compatibility**: Existing ElevenLabs functionality is preserved
- **Fallback Mechanism**: Automatic fallback between providers if one is unavailable

### 🔄 Backward Compatibility
- All existing ElevenLabs functionality remains intact
- Existing API calls work without modification
- Environment variables for ElevenLabs are still supported
- Gradual migration path available

## Installation

### 1. Install Speechify API
```bash
pip install speechify-api
```

### 2. Update Requirements
The `requirements.txt` file has been updated to include:
```txt
speechify-api
```

### 3. Set Environment Variables
Add your Speechify API key to your environment:
```bash
export SPEECHIFY_API_KEY="your_speechify_api_key_here"
```

Or add to your `.env` file:
```env
SPEECHIFY_API_KEY=your_speechify_api_key_here
```

### 4. Optional Configuration
You can configure which TTS provider to use:
```bash
export TTS_PROVIDER="speechify"  # or "elevenlabs"
```

## Supported Languages

### Fully Supported Languages
| Language              | Code  | Status |
|-----------------------|-------|--------|
| English               | en    | ✅     |
| French                | fr-FR | ✅     |
| German                | de-DE | ✅     |
| Spanish               | es-ES | ✅     |
| Portuguese (Brazil)   | pt-BR | ✅     |
| Portuguese (Portugal) | pt-PT | ✅     |

### Beta Languages
| Language   | Code  | Status |
|------------|-------|--------|
| Arabic     | ar-AE | 🧪     |
| Danish     | da-DK | 🧪     |
| Dutch      | nl-NL | 🧪     |
| Estonian   | et-EE | 🧪     |
| Finnish    | fi-FI | 🧪     |
| Greek      | el-GR | 🧪     |
| Hebrew     | he-IL | 🧪     |
| Hindi      | hi-IN | 🧪     |
| Italian    | it-IT | 🧪     |
| Japanese   | ja-JP | 🧪     |
| Norwegian  | nb-NO | 🧪     |
| Polish     | pl-PL | 🧪     |
| Russian    | ru-RU | 🧪     |
| Swedish    | sv-SE | 🧪     |
| Turkish    | tr-TR | 🧪     |
| Ukrainian  | uk-UA | 🧪     |
| Vietnamese | vi-VN | 🧪     |

## Usage Examples

### Basic Usage (No Changes Required)
```python
from modules.tts_generator import TTSGenerator

# Initialize with default provider (Speechify)
tts = TTSGenerator()

# Generate audio (works exactly as before)
manga_script = [
    {"role": "narrator", "description": "The sun rises over the village."},
    {"role": "character", "description": "Hello, world!"}
]

audio_path = tts.generate_audio_from_script(manga_script, "en")
```

### Explicit Provider Selection
```python
# Use Speechify explicitly
tts = TTSGenerator(tts_provider="speechify")

# Use ElevenLabs (backward compatibility)
tts = TTSGenerator(tts_provider="elevenlabs")
```

### Multi-language Support
```python
# English
tts.configure_tts("en", 150)
audio_path = tts.generate_audio_from_script(script, "en")

# French
tts.configure_tts("fr-FR", 140)
audio_path = tts.generate_audio_from_script(script, "fr-FR")

# Japanese
tts.configure_tts("ja-JP", 130)
audio_path = tts.generate_audio_from_script(script, "ja-JP")
```

### Voice Management
```python
# Get available voices
voice_info = tts.get_available_voices()
print(f"Provider: {voice_info['provider']}")
print(f"Available voices: {voice_info['count']}")

# Filter voices (Speechify only)
if tts.tts_provider == "speechify":
    voices = voice_info['voices']
    male_voices = tts.filter_voice_models(voices, gender="male")
    en_voices = tts.filter_voice_models(voices, locale="en-US")
```

## Configuration

### Environment Variables
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SPEECHIFY_API_KEY` | Speechify API key | None | Yes (for Speechify) |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | None | Yes (for ElevenLabs) |
| `TTS_PROVIDER` | Preferred TTS provider | "speechify" | No |
| `SPEECHIFY_NARRATOR_VOICE_ID` | Narrator voice ID | "scott" | No |
| `SPEECHIFY_CHARACTER_VOICE_ID` | Character voice ID | "scott" | No |

### Configuration File
The `config.py` file has been updated with:
- Extended language support
- TTS provider configuration
- Backward compatibility settings

## Testing

### Run Simple Test
```bash
python test_speechify_simple.py
```

### Run Comprehensive Tests
```bash
pytest test_speechify_migration.py -v
```

### Test Specific Functionality
```bash
# Test Speechify only
python -c "
from modules.tts_generator import TTSGenerator
tts = TTSGenerator(tts_provider='speechify')
print(f'Provider: {tts.tts_provider}')
print(f'Languages: {len(tts.supported_languages)}')
"

# Test ElevenLabs only
python -c "
from modules.tts_generator import TTSGenerator
tts = TTSGenerator(tts_provider='elevenlabs')
print(f'Provider: {tts.tts_provider}')
"
```

## Migration Checklist

### ✅ Completed
- [x] Speechify API integration
- [x] Backward compatibility with ElevenLabs
- [x] Multi-language support
- [x] Automatic fallback mechanism
- [x] Comprehensive test suite
- [x] Documentation updates
- [x] Configuration updates

### 🔄 Migration Steps
1. **Install Speechify API**: `pip install speechify-api`
2. **Set API Key**: Add `SPEECHIFY_API_KEY` to environment
3. **Test Migration**: Run `python test_speechify_simple.py`
4. **Update Configuration**: Set `TTS_PROVIDER="speechify"` (optional)
5. **Verify Functionality**: Test with your existing workflows

## Troubleshooting

### Common Issues

#### 1. Speechify Package Not Found
```
ImportError: No module named 'speechify'
```
**Solution**: Install the package
```bash
pip install speechify-api
```

#### 2. API Key Not Found
```
SPEECHIFY_API_KEY not found in environment variables
```
**Solution**: Set the environment variable
```bash
export SPEECHIFY_API_KEY="your_key_here"
```

#### 3. Fallback to ElevenLabs
```
Falling back to ElevenLabs...
```
**Solution**: This is normal behavior when Speechify is not available. Check your API key and internet connection.

#### 4. Language Not Supported
```
Warning: Language invalid not supported. Using English.
```
**Solution**: Use one of the supported language codes listed above.

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Speechify package not available` | Package not installed | `pip install speechify-api` |
| `SPEECHIFY_API_KEY not found` | Missing API key | Set environment variable |
| `Could not initialize Speechify client` | Invalid API key or network issue | Check API key and internet |
| `No script data provided` | Empty script passed | Provide valid script data |

## Performance Comparison

### Speechify vs ElevenLabs

| Feature | Speechify | ElevenLabs |
|---------|-----------|------------|
| Language Support | 20+ languages | Limited |
| Voice Quality | High | High |
| API Response Time | Fast | Fast |
| Cost | Competitive | Competitive |
| Automatic Language Detection | ✅ | ❌ |
| Multi-language Support | ✅ | Limited |

## API Reference

### TTSGenerator Class

#### Constructor
```python
TTSGenerator(output_dir="./audio_output", tts_provider="speechify")
```

#### Methods
- `configure_tts(language, rate)`: Configure language and speech rate
- `generate_audio_from_script(script, language)`: Generate audio from script
- `get_tts_statistics(text)`: Get text statistics
- `get_audio_info(audio_path)`: Get audio file information
- `get_available_voices()`: Get available voices
- `filter_voice_models(voices, **filters)`: Filter voices by criteria

## Support

### Getting Help
1. Check this documentation
2. Run the test suite: `python test_speechify_simple.py`
3. Check environment variables
4. Verify API key validity

### API Key Registration
Get your Speechify API key at: https://console.sws.speechify.com/signup

### Reporting Issues
When reporting issues, please include:
- Error message
- Environment variables (without sensitive data)
- Test output
- Python version
- Operating system

## Changelog

### Version 1.1.0 (Migration)
- ✅ Added Speechify API support
- ✅ Extended language support (20+ languages)
- ✅ Backward compatibility with ElevenLabs
- ✅ Automatic fallback mechanism
- ✅ Comprehensive test suite
- ✅ Updated documentation

### Version 1.0.0 (Original)
- ✅ ElevenLabs TTS integration
- ✅ English language support
- ✅ Basic voice configuration 