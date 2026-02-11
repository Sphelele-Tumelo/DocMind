from PIL import Image
from pathlib import Path
try:
	from super_resolution.esrgan import ESRGANEnhancer
except Exception:
	from esrgan import ESRGANEnhancer

upscaler = ESRGANEnhancer(weights_path="weights/RealESRGAN_x4plus.pth", scale=4)

image_path = Path(__file__).resolve().parents[1] / "images" / "low_res_image.jpeg"
img = Image.open(image_path)
out = upscaler.upscale(img)

print("Original size:", img.size)
print("Upscaled size:", out.size)

out.save("upscaled_image.jpg")