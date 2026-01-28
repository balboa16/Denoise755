"""Video denoising module using DeepFilterNet."""
import os
import asyncio
import logging
import datetime
import tempfile
from typing import Optional, Callable, Tuple, Union

import numpy as np
import librosa
from moviepy import VideoFileClip
from moviepy.audio.io import AudioFileClip

try:
    from df import enhance, init_df
except ImportError:
    enhance = None
    init_df = None

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_DURATION = 300  # 5 minutes in seconds
PROCESSING_TIMEOUT = 300  # 5 minutes timeout
PROGRESS_INTERVAL = 30  # seconds


class VideoProcessingError(Exception):
    """Custom exception for video processing errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# Global model initialization
_model = None
_df_state = None
_sr = None


def get_model() -> Tuple:
    """Initialize and return the DeepFilterNet model.
    
    Returns:
        Tuple of (model, df_state)
        
    Raises:
        VideoProcessingError: If model initialization fails
    """
    global _model, _df_state, _sr
    if _model is not None:
        return _model, _df_state
    
    if init_df is None:
        error_msg = "DeepFilterNet (df) is not installed. Please install it with: pip install DeepFilterNet"
        logger.error(error_msg)
        raise VideoProcessingError(error_msg)
    
    try:
        logger.info(f"{datetime.datetime.now()} - INFO - Initializing DeepFilterNet model...")
        _model, _df_state, _sr = init_df()
        logger.info(f"{datetime.datetime.now()} - INFO - DeepFilterNet model initialized successfully")
        return _model, _df_state
    except Exception as e:
        error_msg = f"Failed to initialize DeepFilterNet model: {str(e)}"
        logger.error(f"{datetime.datetime.now()} - ERROR - {error_msg}")
        raise VideoProcessingError(error_msg)


async def denoise_video(
    input_path: str, 
    output_path: str, 
    progress_callback: Optional[Callable[[float], None]] = None
) -> Tuple[Union[str, None], Union[str, None]]:
    """Denoise a video using DeepFilterNet audio enhancement.
    
    Args:
        input_path: Path to the input video file
        output_path: Path to save the denoised video file
        progress_callback: Optional callback function for progress updates (0.0 to 1.0)
        
    Returns:
        Tuple of (output_path, None) on success, or (None, error_message) on failure
    """
    temp_files = []
    video = None
    enhanced_audio = None
    
    try:
        # File size validation
        if not os.path.exists(input_path):
            error_msg = f"Input file not found: {input_path}"
            logger.error(f"{datetime.datetime.now()} - ERROR - {error_msg}")
            return None, error_msg
        
        file_size = os.path.getsize(input_path)
        if file_size > MAX_FILE_SIZE:
            error_msg = f"File too large: maximum 50MB allowed (file is {file_size / (1024*1024):.2f}MB)"
            logger.error(f"{datetime.datetime.now()} - ERROR - {error_msg}")
            raise VideoProcessingError(error_msg)
        
        logger.info(f"{datetime.datetime.now()} - INFO - Starting video processing: {input_path} ({file_size / (1024*1024):.2f}MB)")
        
        # Load video
        video = VideoFileClip(input_path)
        
        # Video duration check
        if video.duration > MAX_DURATION:
            logger.warning(
                f"{datetime.datetime.now()} - WARNING - Long video detected ({video.duration:.1f}s), "
                f"processing may take several minutes"
            )
        
        # Validate audio track
        if video.audio is None:
            error_msg = "No audio track found in video"
            logger.error(f"{datetime.datetime.now()} - ERROR - {error_msg}")
            raise VideoProcessingError(error_msg)
        
        logger.info(f"{datetime.datetime.now()} - INFO - Video loaded: duration={video.duration:.2f}s")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        temp_files.append(temp_dir)
        
        # Extract audio and write to temp WAV at 48kHz (required by DeepFilterNet)
        temp_audio_path = os.path.join(temp_dir, "audio.wav")
        temp_files.append(temp_audio_path)
        
        original_audio = video.audio
        original_audio.write_audiofile(
            temp_audio_path,
            fps=48000,
            codec='pcm_s16le',
            logger=None
        )
        
        logger.info(f"{datetime.datetime.now()} - INFO - Audio extracted to temp file")
        
        # Initialize model (with timeout protection)
        async def init_model():
            return get_model()
        
        try:
            model, df_state = await asyncio.wait_for(init_model(), timeout=60)
        except asyncio.TimeoutError:
            error_msg = "Model initialization timeout"
            logger.error(f"{datetime.datetime.now()} - ERROR - {error_msg}")
            raise VideoProcessingError(error_msg)
        
        logger.info(f"{datetime.datetime.now()} - INFO - DeepFilterNet initialized")
        
        # Load audio at 48kHz
        audio_array, sr = librosa.load(temp_audio_path, sr=48000)
        
        # Apply enhancement using DeepFilterNet (with timeout)
        async def apply_enhancement():
            return enhance(model, df_state, audio_array)
        
        try:
            enhanced = await asyncio.wait_for(apply_enhancement(), timeout=PROCESSING_TIMEOUT)
        except asyncio.TimeoutError:
            error_msg = "Processing timeout: video too long or system overloaded"
            logger.error(f"{datetime.datetime.now()} - ERROR - {error_msg}")
            raise VideoProcessingError(error_msg)
        
        logger.info(f"{datetime.datetime.now()} - INFO - Audio enhancement applied")
        
        # Save enhanced audio to new WAV file
        enhanced_audio_path = os.path.join(temp_dir, "enhanced.wav")
        temp_files.append(enhanced_audio_path)
        
        # Convert to 16-bit PCM for moviepy compatibility
        enhanced_int16 = (enhanced * 32767).astype(np.int16)
        librosa.output.write_wav(enhanced_audio_path, enhanced_int16, sr=48000)
        
        # Load enhanced audio
        enhanced_audio = AudioFileClip(enhanced_audio_path)
        
        # Set enhanced audio on video
        result = video.set_audio(enhanced_audio)
        
        # Write output video with progress callback
        def update_progress(msg):
            if progress_callback and "Progress" in msg:
                # Extract progress percentage if available
                try:
                    # Moviepy progress format: "Progress: 50%"
                    if "%" in msg:
                        pct = float(msg.split(":")[1].strip().replace("%", "")) / 100
                        progress_callback(pct)
                except (ValueError, IndexError):
                    pass
        
        logger.info(f"{datetime.datetime.now()} - INFO - Writing output video...")
        
        result.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        if progress_callback:
            progress_callback(1.0)
        
        logger.info(f"{datetime.datetime.now()} - INFO - Video processing completed: {output_path}")
        
        return output_path, None
        
    except VideoProcessingError:
        # Re-raise our custom exceptions
        raise
    except asyncio.TimeoutError:
        error_msg = "Processing timeout: video too long or system overloaded"
        logger.error(f"{datetime.datetime.now()} - ERROR - {error_msg}")
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error during video processing: {str(e)}"
        logger.error(f"{datetime.datetime.now()} - ERROR - {error_msg}")
        return None, error_msg
    
    finally:
        # Clean up resources
        if video is not None:
            try:
                video.close()
            except Exception:
                pass
        if enhanced_audio is not None:
            try:
                enhanced_audio.close()
            except Exception:
                pass
        
        # Remove temp files securely
        for temp_file in temp_files:
            try:
                if temp_file and os.path.exists(temp_file):
                    if os.path.isdir(temp_file):
                        os.rmdir(temp_file)
                    else:
                        os.remove(temp_file)
            except OSError:
                pass
