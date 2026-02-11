
import streamlit as st
from huggingface_hub import hf_hub_download
from basicsr.archs.rrdbnet_arch import RRDBNet
import torch


@st.cache_resource(show_spinner="Loading ESRGAN model from Hugging Face (one-time)...")
def load_esrgan_model(scale: int):
    """
    Load an ESRGAN model from Hugging Face Hub. This function is cached to avoid reloading on every call.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Example: using a pre-trained RRDBNet model for 4x super-resolution
    model = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        scale=scale
    ).to(device)
    
    # Load pre-trained weights from Hugging Face Hub
    weights_path = hf_hub_download(
        repo_id="NeoMelo/doc-mind-esrgan", 
        filename="RealESRGAN_x4plus.pth")
    
    # Load checkpoint and extract params_ema if present
    checkpoint = torch.load(weights_path, map_location=device)
    
    # Handle both direct state_dict and nested "params_ema" structure
    if isinstance(checkpoint, dict) and "params_ema" in checkpoint:
        state_dict = checkpoint["params_ema"]
    else:
        state_dict = checkpoint
    
    # Load with strict=False to allow for minor key mismatches
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return model