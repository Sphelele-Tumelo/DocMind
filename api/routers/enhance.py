from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from supabase import Client
from fastapi.responses import StreamingResponse
from ..services.enhance_service import ESRGANEnhanceService
from ..data.database_supabase import get_db
from ..models.text_extraction_model import FixTextRequest
import io
from ..services.llm_service import LLMService
import openai
import logging
from datetime import datetime
import uuid
import traceback

router = APIRouter(prefix="/enhance", tags=["Enhancement"])
logging = logging.getLogger("enhance_router")

def get_enhance_service():
    return ESRGANEnhanceService()



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
        enhanced_bytes = await service.enhance_image(contents)
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
    try:
        db.table("scans").insert({
            "useruid": uuid.uuid4(),  # ← change to real user ID later
            "original_filename": file.filename,
            "original_url": original_path,            # ← save the path
            "enhanced_url": enhanced_path,            # ← save the path
            "status": "enhanced"         # or full public URL if needed
            # "ocr_text": None,                       # add once you have OCR
            # "ai_fixed_text": None,
        }).execute()
    except Exception as e:
        print("DB insert failed:\n", traceback.format_exc())
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
@router.get("/health")
async def health_check():
    return {"status": "healthy", "enhance_service": "available"}

@router.post("/test-llm")
async def test_llm(text:str, llm_service: LLMService = Depends(LLMService)):
    cleaned = await llm_service.clean_text(text)
    return {"cleaned": cleaned}
    