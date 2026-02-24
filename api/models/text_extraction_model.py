from pydantic import BaseModel, UUID4

class FixTextRequest(BaseModel):
    # the request must carry a valid UUID for the scan. pydantic will
    # automatically reject anything that isn't a proper UUID string
    scan_id: UUID4  # UUID of the scan to fix
