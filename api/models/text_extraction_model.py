from pydantic  import BaseModel

class FixTextRequest(BaseModel):
    scan_id: str  # UUID of the scan to fix