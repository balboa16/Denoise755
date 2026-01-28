"""
Video Noise Reduction Bot handlers using aiogram 3.
Processes videos to remove noise using DeepFilterNet technology.
"""

import logging
import os
import tempfile
import asyncio
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, FSInputFile

from moviepy import VideoFileClip
try:
    from moviepy.audio.io.AudioFileClip import AudioFileClip
except ImportError:
    from moviepy.audio.AudioClip import AudioFileClip

# DeepFilterNet import - handle potential import errors gracefully
try:
    from df import enhance, init_df
    import soundfile as sf
    DEEPFILTERNET_AVAILABLE = True
except ImportError:
    DEEPFILTERNET_AVAILABLE = False
    enhance = None
    init_df = None
    sf = None
    logging.warning("DeepFilterNet not available. Install with: pip install deepfilternet")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router instance
router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    """
    Handle /start command.
    Send welcome message to user.
    """
    await message.answer(
        "🎬 Video Noise Reduction Bot\n\n"
        "Send me a video and I'll remove noise from its audio "
        "using DeepFilterNet technology."
    )


@router.message(F.video)
async def process_video(message: Message):
    """
    Handle video messages.
    Download video, extract audio, apply noise reduction,
    merge audio back, and send processed video.
    """
    if not DEEPFILTERNET_AVAILABLE:
        await message.answer(
            "❌ DeepFilterNet is not installed.\n\n"
            "Please install it with: pip install deepfilternet"
        )
        return

    # Get video file info
    video = message.video
    video_file_id = video.file_id
    video_name = video.file_name or "video.mp4"

    # Create temporary directory for processing
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, f"input_{video_file_id}.mp4")
    audio_path = os.path.join(temp_dir, f"audio_{video_file_id}.wav")
    enhanced_audio_path = os.path.join(temp_dir, f"enhanced_{video_file_id}.wav")
    output_path = os.path.join(temp_dir, f"output_{video_file_id}.mp4")

    try:
        # Inform user about download starting
        await message.answer("⬇️ Downloading video...")
        logger.info(f"Downloading video {video_file_id}")

        # Download video file
        await message.bot.download(file=video_file_id, destination=input_path)
        logger.info(f"Video downloaded to {input_path}")

        # Inform user about processing
        await message.answer("🔊 Extracting and processing audio...")
        logger.info("Processing audio with DeepFilterNet")

        # Show processing status to user
        await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
        clip = VideoFileClip(input_path)
        original_audio = clip.audio
        original_audio.write_audiofile(audio_path, fps=48000, codec='pcm_s16le', verbose=False, logger=None)
        clip.close()

        logger.info(f"Audio extracted to {audio_path}")

        # Apply DeepFilterNet noise reduction
        await message.answer("🎧 Applying DeepFilterNet noise reduction...")
        logger.info("Initializing DeepFilterNet model")

        # Initialize DeepFilterNet model
        def init_and_process():
            # Initialize model
            model, df_state, sr = init_df()

            # Load audio at 48kHz
            audio_array, _ = sf.read(audio_path)
            if audio_array.ndim > 1:
                audio_array = audio_array.mean(axis=1)  # Convert to mono

            # Apply enhancement
            enhanced = enhance(model, df_state, audio_array)

            # Save enhanced audio
            sf.write(enhanced_audio_path, enhanced, sr)

            return enhanced_audio_path

        # Run processing in thread to avoid blocking
        await asyncio.to_thread(init_and_process)
        logger.info(f"Enhanced audio saved to {enhanced_audio_path}")

        # Inform user about merging
        await message.answer("🎬 Merging enhanced audio with video...")
        logger.info("Merging audio back to video")

        # Load video and enhanced audio, then merge
        final_clip = VideoFileClip(input_path)
        enhanced_audio = None
        try:
            enhanced_audio = AudioFileClip(enhanced_audio_path)
            # Set the new audio on the video clip
            final_clip = final_clip.set_audio(enhanced_audio)
            # Write the final video with new audio
            final_clip.write_videofile(
                output_path,
                verbose=False,
                logger=None,
                codec='libx264',
                audio_codec='aac'
            )
        finally:
            # Cleanup resources
            if enhanced_audio:
                enhanced_audio.close()
            final_clip.close()

        logger.info(f"Final video saved to {output_path}")

        # Inform user about completion
        await message.answer("✅ Video processing complete! Sending...")
        logger.info("Sending processed video to user")

        # Send processed video
        await message.answer_video(
            video=FSInputFile(output_path),
            caption="✨ Your video with noise-reduced audio is ready!"
        )

        logger.info(f"Processed video sent to user {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        await message.answer(
            "❌ An error occurred while processing your video.\n\n"
            "Please try again or send a different video."
        )

    finally:
        # Clean up temporary files
        await message.answer("🧹 Cleaning up temporary files...")
        cleanup_files = [input_path, audio_path, enhanced_audio_path, output_path]

        for file_path in cleanup_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {e}")

        # Remove temp directory
        try:
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                logger.info(f"Removed temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")
