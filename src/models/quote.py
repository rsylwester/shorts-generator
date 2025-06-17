from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class QuoteStatus(str, Enum):
    UNUSED = "unused"
    USED = "used"

class Quote(BaseModel):
    id: Optional[int] = None
    quote: str = Field(..., max_length=220, description="Quote text (max 220 chars)")
    author: str = Field(..., description="Quote author")
    reflection: str = Field(..., max_length=220, description="Reflection text (max 220 chars)")
    social_media_post: str = Field(..., description="Ready social media post text")
    status: QuoteStatus = QuoteStatus.UNUSED
    
    class Config:
        use_enum_values = True