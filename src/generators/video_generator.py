import os
import tempfile
import time
import logging
from pathlib import Path
from typing import Optional
import ffmpeg
from PIL import Image

from ..models import Quote, GeneratedVideo, VideoSpecs, VideoSettings
from .slide_renderer import SlideRenderer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.renderer = SlideRenderer()
        self.specs = VideoSpecs()
        self.settings = VideoSettings()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Resource paths - resolve absolute paths
        base_dir = Path.cwd()
        self.background_1_path = str(base_dir / "data/backgrounds/background_1.jpg")
        self.background_2_path = str(base_dir / "data/backgrounds/background_2.jpg")
        self.lotus_icon_path = str(base_dir / "data/icons/lotus.png")
        self.meditation_icon_path = str(base_dir / "data/icons/meditation.png")
        self.background_music_path = str(base_dir / "data/audio/background-music-1.mp3")
    
    def create_video(self, quote: Quote) -> GeneratedVideo:
        """Create a complete video from a quote."""
        start_time = time.time()
        logger.info(f"Starting video generation for quote: {quote.quote[:50]}...")
        
        # Generate filename
        quote_snippet = quote.quote[:30].replace(" ", "_").replace(",", "").replace(".", "")
        filename = f"{quote_snippet}_{int(time.time())}.mp4"
        output_path = self.output_dir / filename
        logger.info(f"Output path: {output_path}")
        
        # Check if background images exist
        logger.info(f"Checking background 1: {self.background_1_path} - exists: {os.path.exists(self.background_1_path)}")
        logger.info(f"Checking background 2: {self.background_2_path} - exists: {os.path.exists(self.background_2_path)}")
        logger.info(f"Checking lotus icon: {self.lotus_icon_path} - exists: {os.path.exists(self.lotus_icon_path)}")
        logger.info(f"Checking meditation icon: {self.meditation_icon_path} - exists: {os.path.exists(self.meditation_icon_path)}")
        logger.info(f"Checking background music: {self.background_music_path} - exists: {os.path.exists(self.background_music_path)}")
        
        try:
            # Create temporary directory for slides
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                logger.info(f"Created temp directory: {temp_path}")
                
                # Render slides
                logger.info("Rendering slide 1...")
                slide_1 = self.renderer.render_slide_1(
                    quote.quote, 
                    quote.author, 
                    self.background_1_path,
                    self.lotus_icon_path if os.path.exists(self.lotus_icon_path) else None
                )
                slide_1 = self.renderer.add_watermark(slide_1)
                slide_1_path = temp_path / "slide_1.png"
                slide_1.save(slide_1_path)
                logger.info(f"Slide 1 saved: {slide_1_path} (size: {slide_1.size})")
                
                logger.info("Rendering slide 2...")
                slide_2 = self.renderer.render_slide_2(
                    quote.reflection,
                    self.background_2_path,
                    self.meditation_icon_path if os.path.exists(self.meditation_icon_path) else None
                )
                slide_2 = self.renderer.add_watermark(slide_2)
                slide_2_path = temp_path / "slide_2.png"
                slide_2.save(slide_2_path)
                logger.info(f"Slide 2 saved: {slide_2_path} (size: {slide_2.size})")
                
                # Create video with FFmpeg
                logger.info("Creating video with FFmpeg...")
                self._create_video_with_ffmpeg(
                    slide_1_path, 
                    slide_2_path, 
                    output_path
                )
                
                # Verify output file
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    logger.info(f"Video created successfully: {output_path} (size: {file_size} bytes)")
                else:
                    logger.error("Video file was not created!")
                    raise Exception("Output video file does not exist")
            
            generation_time = time.time() - start_time
            logger.info(f"Video generation completed in {generation_time:.2f} seconds")
            
            return GeneratedVideo(
                quote=quote,
                file_path=str(output_path),
                generation_time=generation_time,
                specs=self.specs,
                settings=self.settings
            )
            
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            raise Exception(f"Video generation failed: {str(e)}")
    
    def _create_video_with_ffmpeg(self, slide_1_path: Path, slide_2_path: Path, output_path: Path):
        """Create video using FFmpeg with slides and smooth cross-fade transition."""
        logger.info(f"FFmpeg creating video from {slide_1_path} and {slide_2_path}")
        logger.info(f"Slide 1 exists: {slide_1_path.exists()}, Slide 2 exists: {slide_2_path.exists()}")
        
        try:
            # Calculate timing for cross-fade
            # With xfade, total duration = slide1_duration + slide2_duration - transition_duration
            # So to get 12s total, we need: slide1_duration + slide2_duration - 1.0 = 12
            # Therefore: slide1_duration + slide2_duration = 13
            slide_1_duration = 6.5  # First slide slightly longer
            slide_2_duration = 6.5  # Second slide slightly longer
            transition_start = slide_1_duration - self.specs.transition_duration
            
            # Create input streams
            logger.info(f"Creating input streams with cross-fade transition")
            slide_1_input = ffmpeg.input(str(slide_1_path), loop=1, t=slide_1_duration)
            slide_2_input = ffmpeg.input(str(slide_2_path), loop=1, t=slide_2_duration)
            
            # Create cross-fade effect using xfade filter
            logger.info(f"Applying cross-fade transition (duration: {self.specs.transition_duration}s)")
            video = ffmpeg.filter(
                [slide_1_input, slide_2_input], 
                'xfade', 
                transition='fade',
                duration=self.specs.transition_duration,
                offset=transition_start
            )
            
            # Add background music if available
            if os.path.exists(self.background_music_path):
                logger.info(f"Adding background music from {self.background_music_path}")
                audio = ffmpeg.input(self.background_music_path)
                audio = audio.filter('volume', 0.3)  # Lower volume
                audio = audio.filter('atrim', duration=self.specs.duration)
                # Add fade in and fade out effects
                audio = audio.filter('afade', t='in', st=0, d=1.0)  # 1 second fade in
                audio = audio.filter('afade', t='out', st=self.specs.duration - 1.0, d=1.0)  # 1 second fade out
                
                # Combine video and audio
                output = ffmpeg.output(
                    video, audio,
                    str(output_path),
                    vcodec='libx264',
                    acodec='aac',
                    r=self.specs.fps,
                    s=f'{self.specs.width}x{self.specs.height}',
                    pix_fmt='yuv420p',
                    movflags='faststart',
                    shortest=None
                )
            else:
                logger.info("No background music found, creating video-only output")
                # Video only (no audio)
                output = ffmpeg.output(
                    video,
                    str(output_path),
                    vcodec='libx264',
                    r=self.specs.fps,
                    s=f'{self.specs.width}x{self.specs.height}',
                    pix_fmt='yuv420p',
                    movflags='faststart'
                )
            
            # Run FFmpeg with verbose output for debugging
            logger.info("Running FFmpeg command...")
            ffmpeg.run(output, overwrite_output=True, quiet=False)
            logger.info("FFmpeg command completed")
            
        except ffmpeg.Error as e:
            error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Video creation error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_video_info(self, video_path: str) -> dict:
        """Get information about generated video."""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            return {
                'duration': float(probe['format']['duration']),
                'width': int(video_stream['width']) if video_stream else None,
                'height': int(video_stream['height']) if video_stream else None,
                'fps': eval(video_stream['r_frame_rate']) if video_stream else None,
                'has_audio': audio_stream is not None,
                'file_size': int(probe['format']['size'])
            }
        except Exception as e:
            return {'error': str(e)}