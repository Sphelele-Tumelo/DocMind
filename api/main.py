from .routers import enhance   # Import the router for enhancement endpoints
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .models.enhance_models import EnhanceResponse
import io
import base64
from PIL import Image
import numpy as np


# Import your enhancer (adjust path if needed)
from main.super_resolution.esrgan import ESRGANEnhancer  # ← your class

app = FastAPI(
    title="DocMind API",
    description="AI-powered receipt/document enhancement & OCR",
    version="0.1.0"
)

# Allow frontend (React/Vite etc.) to call this API from localhost or deployed domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load enhancer once at startup (no reload every request)
#model_stucture = _loader.load_esrgan_model(scale =4)  # ← your model loading function
#enhancer = ESRGANEnhancer(model = model_stucture)
#
#@app.get("/")
#async def root():
#    return {
#        "message": "DocMind API is live 🚀",
#        "endpoints": ["/enhance (POST)"]
#    }
#
#@app.post("/enhance", response_model=EnhanceResponse)
#async def enhance_image(
#    file: UploadFile = File(...),
#    # Later: add pro check here with Depends(user_is_pro)
#):
#    if not file.content_type.startswith("image/"):
#        raise HTTPException(status_code=400, detail="File must be an image")
#
#    try:
#        # Read uploaded file
#        contents = await file.read()
#        image = Image.open(io.BytesIO(contents))
#
#        # Enhance
#        enhanced = enhancer.process(image)
#        print(f"Enhanced image size: {enhanced.size}, mode: {enhanced.mode}") # Debugging info
#        enhanced.save("debug_enhanced.png") # Save for debugging (remove in production)
#        print("Image enhancement successful") # Debugging info
#
#        # Convert enhanced image to bytes for response
#        img_byte_arr = io.BytesIO()
#        enhanced.save(img_byte_arr, format="PNG")
#        img_byte_arr.seek(0)
#
#        # Option 1: Stream image directly (best for large files)
#        # return StreamingResponse(img_byte_arr, media_type="image/png")
#
#        # Option 2: Return base64 (easier for React to show preview)
#        base64_img = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
#
#        return EnhanceResponse(
#            status="success",
#            original_filename=file.filename,
#            enhanced_image_base64=f"data:image/png;base64,{base64_img}",
#            message="Image enhanced successfully"
#        )
#
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

# Health check (good for monitoring)
app.include_router(enhance.router)  # Include the enhance router
@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": True}