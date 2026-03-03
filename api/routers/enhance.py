from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from supabase import Client
from fastapi.responses import StreamingResponse
from ..services.enhance_service import ESRGANEnhanceService
from ..data.database_supabase import get_db
from ..models.text_extraction_model import FixTextRequest
import io
from ..services.llm_service import LLMService
from ..models.update_scan import UpdateScanRequest
import openai
import logging
from datetime import datetime
import uuid
import traceback

router = APIRouter(prefix="/enhance", tags=["Enhancement"])
logging = logging.getLogger("enhance_router")

def get_enhance_service():
    return ESRGANEnhanceService()




router = APIRouter(prefix="/scans", tags=["Scans"])

# GET all scans (for the current user)
@router.get("/")
async def get_all_scans(db: Client = Depends(get_db)):
    try:
        response = db.table("scans").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET one scan by ID
@router.get("/{scan_id}")
async def get_scan(scan_id: str, db: Client = Depends(get_db)):
    try:
        response = db.table("scans").select("*").eq("id", scan_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Scan not found")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fix-text")
async def fix_ocr_text(
    request: FixTextRequest,
    db: Client = Depends(get_db),
    # Add Pro check later
):
    # validate that the UUID passed is valid (pydantic already has done this),
    # but supabase/sql may still raise if the column type mismatches. wrap
    # the query so we can propagate a 400 instead of letting 500 bubble up.
    try:
        scan = db.table("scans").select("ocr_text").eq("id", str(request.scan_id)).single().execute()
    except Exception as e:
        logging.exception("database query failed")
        # most likely the user sent something that can't be compared to uuid
        raise HTTPException(status_code=400, detail="Invalid scan_id")

    if not scan.data:
        raise HTTPException(404, "Scan not found")

    raw_text = scan.data["ocr_text"]

    # LLM prompt (use openai or gemini)
    prompt = f"Clean this raw OCR text from a receipt/document: {raw_text}. Fix errors, format nicely (merchant, date, items, totals). Do NOT invent info."

    response = openai.ChatCompletion.create(  # or gemini/grok
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    cleaned = response.choices[0].message.content.strip()

    # Update scan in DB
    db.table("scans").update({
        "ai_fixed_text": cleaned,
        "status": "ai_fixed"
    }).eq("id", request.scan_id).execute()

    return {"status": "success", "cleaned_text": cleaned}

@router.post("/")
async def enhance_and_save(
    file: UploadFile = File(...),
    db: Client = Depends(get_db),
    service: ESRGANEnhanceService = Depends(get_enhance_service)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()

    # Enhance the image
    try:
        enhanced_bytes =  service.enhance_image(contents)
    except Exception as e:
        logging.exception("Enhancement failed")
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

    # Generate unique paths for storage
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
    original_path = f"originals/{uuid.uuid4()}.{file_ext}"
    enhanced_path = f"enhanced/{uuid.uuid4()}.png"

    # Upload original to Supabase Storage
    try:
        db.storage.from_("images").upload(
            path=original_path,
            file=contents,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        print("Original upload failed:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Original upload failed: {str(e)}")

    # Upload enhanced to Supabase Storage
    try:
        db.storage.from_("images").upload(
            path=enhanced_path,
            file=enhanced_bytes,
            file_options={"content-type": "image/png"}
        )
    except Exception as e:
        print("Enhanced upload failed:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Enhanced upload failed: {str(e)}")

    # Save metadata to scans table (using correct column names from your screenshot)
    # Inside your /enhance endpoint, after both uploads succeed
    try:
        insert_data = {
            "user_id": str(uuid.uuid4()),           # ← correct column name + real UUID
            "original_filename": file.filename,
            
            "status": "enhanced",
            "enhanced_url": enhanced_path,          # path in storage
            # "ocr_text": raw_ocr,                # add when you have OCR
            # "ai_fixed_text": None,
        }

        response = db.table("scans").insert(insert_data).execute()

        if not response.data:
            raise ValueError("Insert returned no data — something went wrong")
        
    except Exception as e:
      print(f"DB Insert Error: {str(e)}")   # print so you see it
      raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
          # Don't fail the whole request if DB insert fails (optional)

    # Return the enhanced image as stream (best for large images)
    enhanced_stream = io.BytesIO(enhanced_bytes)
    enhanced_stream.seek(0)

    return StreamingResponse(
        enhanced_stream,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=enhanced_{file.filename}"
        }
    )
    
@router.put("/{scan_id}")
async def update_scan(
    scan_id: str,
    update_data: UpdateScanRequest,
    db: Client = Depends(get_db)
):
    try:
        # Only update fields that were sent
        payload = update_data.dict(exclude_unset=True)
        if not payload:
            raise HTTPException(400, "No fields to update")

        response = db.table("scans").update(payload).eq("id", scan_id).execute()
        
        if not response.data:
            raise HTTPException(404, "Scan not found")

        return {"message": "Scan updated", "updated_scan": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-enhance")
async def test_enhance(service: ESRGANEnhanceService = Depends()):
    # This is just a test endpoint to verify the enhancement service is working
    try:
        with open("test_images/test_receipt.jpg", "rb") as f:
            contents = f.read()
        enhanced_bytes = await service.enhance_image(contents)
        return StreamingResponse(io.BytesIO(enhanced_bytes), media_type="image/png")
    except Exception as e:
        logging.exception("Test enhancement failed")
        raise HTTPException(status_code=500, detail=f"Test enhancement failed: {str(e)}")

@router.delete("/{scan_id}")
async def delete_scan(scan_id: str, db: Client = Depends(get_db)):
    try:
        response = db.table("scans").delete().eq("id", scan_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Scan not found or already deleted")

        return {"message": f"Scan {scan_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "enhance_service": "available"}


@router.post("/test-llm")
async def test_llm(text:str, llm_service: LLMService = Depends(LLMService)):
    cleaned = await llm_service.clean_text(text)
    return {"cleaned": cleaned}
    