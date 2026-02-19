from PIL import Image
import io
from main.super_resolution.esrgan import ESRGANEnhancer  # Adjust path if needed
import main.super_resolution.esrgan_loader as _loader  # ← your model loader

class ESRGANEnhanceService:
    def __init__(self):
        model_stucture = _loader.load_esrgan_model(scale =4)  # ← your model loading function
        self.enhancer = ESRGANEnhancer(model = model_stucture)

    def enhance_image(self, image_bytes: bytes) -> bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            enhanced = self.enhancer.process(image)
            
            output = io.BytesIO()
            enhanced.save(output, format='PNG')
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            raise ValueError(f"Image enhancement failed: {str(e)}")
        
    def extract_ocr_text(self, image_bytes: bytes) -> str:
        result = self.ocr.ocr(image_bytes)
        if result:
            text = "\n".join([line[1][0] for res in result for line in res])
            return text
        return "No text found"
            