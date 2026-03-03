from pydantic import BaseModel 

class UpdateScanRequest(BaseModel):
    scan_id: str | None = None
    ocr_text: str | None = None
    ai_fixed_text: str | None = None
    status: str | None = None