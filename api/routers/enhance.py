from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from supabase import Client
from fastapi.responses import StreamingResponse
from ..services.enhance_service import ESRGANEnhanceService
from ..data.database_supabase import get_db
import io


router = APIRouter(prefix = "/enhance", tags=["Enhance"])


def get_enhance_service():
    return ESRGANEnhanceService()

@router.post("/")
async def enhance_image(
    file: UploadFile = File(...),
    service: ESRGANEnhanceService = Depends(get_enhance_service),
    db: Client = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    try:
        enhanced_bytes = service.enhance_image(contents)
        
        db.table("scans").insert({
            "user_id": "example_user_id",  # Replace with actual user ID from auth
            "original_filename": file.filename,
            "status": "enhanced",
            "created_at": "now()"  # Use actual timestamp in production
        }).execute()
        
        return StreamingResponse(
            io.BytesIO(enhanced_bytes),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=enhanced_{file.filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        print(f"DB Error: {str(e)}")  # Log DB errors for debugging

@router.get("/health")
async def health_check():
    return {"status": "healthy", "enhance_service": "available"}