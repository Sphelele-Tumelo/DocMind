import torch
import numpy as np
from PIL import Image
from huggingface_hub import hf_hub_download
import torch.nn as nn

class ESRGANEnhancer:
    def __init__(self, model, device=None):
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model # Use the model passed from the loader
        self.model.to(self.device).eval()

    def process(self, pil_image):
        # 1. Pre-process & Normalize (The "Fix" for black images)
        # We convert to RGB to strip Alpha channels, then scale to 0-1
        img = np.array(pil_image.convert("RGB")).astype(np.float32) / 255.0
        
        # Convert to Tensor: [H, W, C] -> [1, C, H, W]
        img_tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(self.device)

        with torch.no_grad():
            # Run inference
            output_tensor = self.model(img_tensor)

        # 2. Post-process (The "Fix" for .astype error)
        # We move to CPU, clamp values to 0-1, and convert back to 0-255
        output = output_tensor.data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output, (1, 2, 0))
        
        # Convert back to standard 8-bit image format
        output_final = (output * 255.0).clip(0, 255).astype(np.uint8)
         
         
        return Image.fromarray(output_final)
        
 
    


      
      
