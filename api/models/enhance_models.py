from pydantic import BaseModel
from typing import Optional
import base64

class EnhanceResponse(BaseModel):
    status: str
    original_filename: str
    enhanced_image_base64: Optional[str] = None
    message: Optional[str] = None