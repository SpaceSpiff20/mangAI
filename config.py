"""
Configuration module for MangAI application
"""

import os
from typing import Dict, Any, Optional


class Config:
    """Application configuration"""
    
    # Application settings
    APP_NAME = "MangAI"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Model paths
    MODEL_PATHS = {
        "frame": "./models/yolo8l_50epochs_frame/best.pt",
        "panel": "./models/yolo8l_50epochs/best.pt",
        "text-frame": "./models/yolo8l_50epochs/best.pt"
    }
    
    # Supported languages (extended for Speechify)
    SUPPORTED_LANGUAGES = {
        "en": {"name": "English", "ocr": "eng", "tts": "en-US"},
        "fr-FR": {"name": "French", "ocr": "fra", "tts": "fr-FR"},
        "de-DE": {"name": "German", "ocr": "deu", "tts": "de-DE"},
        "es-ES": {"name": "Spanish", "ocr": "spa", "tts": "es-ES"},
        "pt-BR": {"name": "Portuguese (Brazil)", "ocr": "por", "tts": "pt-BR"},
        "pt-PT": {"name": "Portuguese (Portugal)", "ocr": "por", "tts": "pt-PT"},
        "ja-JP": {"name": "Japanese", "ocr": "jpn", "tts": "ja-JP"},
        "it-IT": {"name": "Italian", "ocr": "ita", "tts": "it-IT"},
        "ru-RU": {"name": "Russian", "ocr": "rus", "tts": "ru-RU"},
        "zh-CN": {"name": "Chinese (Simplified)", "ocr": "chi_sim", "tts": "zh-CN"}
    }
    
    # Default settings
    DEFAULT_LANGUAGE = "en"  # English only
    DEFAULT_YOLO_MODEL = os.getenv("DEFAULT_YOLO_MODEL", "frame")
    TTS_SPEECH_RATE = int(os.getenv("TTS_SPEECH_RATE", "150"))
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "speechify")  # speechify or elevenlabs
    
    # Confidence thresholds
    YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.25"))
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.3"))
    
    # File settings
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["png", "jpg", "jpeg"]
    AUDIO_OUTPUT_DIR = "./audio_output"
    MAX_AUDIO_FILE_AGE_HOURS = int(os.getenv("MAX_AUDIO_FILE_AGE_HOURS", "24"))
    
    # OCR settings (English only)
    TESSERACT_CONFIG = os.getenv("TESSERACT_CONFIG", "--psm 6")
    
    @classmethod
    def get_model_path(cls, model_type: str) -> str:
        """Get the path for a specific model type"""
        path = cls.MODEL_PATHS.get(model_type)
        if path is None:
            raise ValueError(f"Model type '{model_type}' not found")
        return path
    
    @classmethod
    def get_language_config(cls, language: str) -> Dict[str, Any]:
        """Get configuration for a specific language"""
        return cls.SUPPORTED_LANGUAGES.get(language, cls.SUPPORTED_LANGUAGES[cls.DEFAULT_LANGUAGE])
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate configuration and return status"""
        validation = {}
        
        # Check model files
        for model_type, path in cls.MODEL_PATHS.items():
            validation[f"model_{model_type}"] = os.path.exists(path)
        
        # Check directories
        validation["audio_output_dir"] = os.path.exists(cls.AUDIO_OUTPUT_DIR) or cls._create_dir(cls.AUDIO_OUTPUT_DIR)
        
        return validation
    
    @classmethod
    def _create_dir(cls, path: str) -> bool:
        """Create directory if it doesn't exist"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False
    
    @classmethod
    def create_processing_directory(cls, timestamp: Optional[str] = None) -> Dict[str, str]:
        """
        Create a structured processing directory with subfolders
        
        Args:
            timestamp: Custom timestamp string, if None uses current time
            
        Returns:
            Dictionary with paths to each subfolder
        """
        from datetime import datetime
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        base_dir = f"processed_{timestamp}"
        
        structure = {
            'base': base_dir,
            'frames': os.path.join(base_dir, 'frames'),
            'ocr': os.path.join(base_dir, 'ocr'), 
            'audio': os.path.join(base_dir, 'audio'),
            'timestamp': timestamp
        }
        
        # Create all directories
        for path in structure.values():
            if isinstance(path, str) and path != timestamp:
                cls._create_dir(path)
        
        return structure
