from pydantic import BaseModel
from typing import Optional
from .quote import Quote

class VideoSpecs(BaseModel):
    width: int = 1080
    height: int = 1920
    duration: float = 12.0
    fps: int = 30
    slide_duration: float = 6.0
    transition_duration: float = 1.0
    
class VideoSettings(BaseModel):
    font_family: str = "Roboto Serif"
    main_text_color: str = "#3D3D3D"
    author_text_color: str = "#7B7B7B"
    author_opacity: float = 0.7
    min_font_size: int = 60
    max_font_size: int = 90
    watermark_text: str = "jakmedytowac.pl"
    
class GeneratedVideo(BaseModel):
    quote: Quote
    file_path: Optional[str] = None
    generation_time: Optional[float] = None
    specs: VideoSpecs = VideoSpecs()
    settings: VideoSettings = VideoSettings()