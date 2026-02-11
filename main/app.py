from PIL import ImageOps
import warnings
warnings.filterwarnings("ignore")
import torch
from super_resolution.esrgan import ESRGANEnhancer
import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import cv2
from pdf2image import convert_from_bytes
import io
import super_resolution.esrgan_loader as _loader

st.title("DocMind - OCR Test")

uploaded_file = st.file_uploader("Upload image or PDF receipt", type=["png", "jpg", "jpeg", "pdf"])


#def enhance_with_edsr(image, scale=4, model_path= r"C:\Users\Lihle\Downloads\EDSR_x4.pb"):
#    try:
#        sr = cv2.dnn_superres.DnnSuperResImpl_create()
#        sr.readModel(model_path)
#        sr.setModel("edsr", scale)
#        sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
#        sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)  # GPU if you have it later
#
#        # Convert PIL to OpenCV
#        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#        upscaled = sr.upsample(cv_image)
#        # Back to PIL
#        enhanced_pil = Image.fromarray(cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB))
#        return enhanced_pil
#    except Exception as e:
#        st.error(f"Super-resolution failed: {e}")
#        return image  # fallback to original

##esrgan_enhancer = ESRGANEnhancer(scale=4)
    
def preprocess_image(img):
    max_size = 1024
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
    return img

#def preprocess_image(image):    # Convert to OpenCV format
#    cv_image = np.array(image)
#    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
#    
#    # Grayscale + adaptive threshold (makes text pop)
#    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
#    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
#    
#    # Sharpen with kernel (boost edges)
#    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
#    sharpened = cv2.filter2D(thresh, -1, kernel)
#    
#    # Denoise (reduce noise)
#    denoised = cv2.medianBlur(sharpened, 3)
#    
#    # Back to PIL for OCR
#    enhanced = Image.fromarray(denoised)
#    return enhanced
#
def is_blurry(image, threshold=100):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold  # Low variance = blurry

if uploaded_file is not None:
    file_type = uploaded_file.type
    all_text = []

    try:
        # --- OPTIMIZATION: Load reader once, not in the loop ---
        with st.spinner("Initializing OCR Engine..."):
            reader = easyocr.Reader(['en']) 

        if file_type == "application/pdf":
            # Convert PDF
            images = convert_from_bytes(uploaded_file.read())
            st.subheader(f"Processing {len(images)} pages...")
            progress_bar = st.progress(0)
            for i, page_image in enumerate(images):
                
                # Update progress bar
                progress_bar.progress((i + 1) / len(images))
                # Preprocess this page image
                processed_image = preprocess_image(page_image)
                #use_super_res = st.checkbox("Use Super Resolution (Pro feature - enhances low-res images)", value=False)

                #if use_super_res:
                #        with st.spinner("Enhancing image with EDSR..."):
                #            page_image = enhance_with_edsr(page_image)
                #        st.image(page_image, caption=f"Enhanced Page {i+1} (EDSR ×4)", width=True)
                #else:
                #       st.image(page_image, caption=f"Original Page {i+1}", width=True)
            
                use_enhancement = st.checkbox("Enhance image for better quality (fix blurry/low-res)", value=False)     
               #Apply enhancement if toggled
                if use_enhancement:
                     page_image = preprocess_image(page_image)
                     st.image(page_image, caption=f"Enhanced Page {i+1}", width=True)
                else:
                 st.image(page_image, caption=f"Original Page {i+1}", width=True)
                
                
                 use_esrgan = st.checkbox("Use ESRGAN Enhancement (Pro feature)", value=False)
               # if use_esrgan:
               #     with st.spinner("Enhancing image with ESRGAN..."):
               #         image = enhance_with_esrgan(image)
               #     st.image(image, caption="Enhanced Image (ESRGAN ×4)", width=True)
               # else:
               #     st.image(image, caption="Uploaded Image", width=True)
            
                
                # Use a status container to show progress
                with st.status(f"Processing Page {i+1}...", expanded=True) as status:
                    st.image(page_image, caption=f"Page {i+1}", width=500)
                    
                    # Convert PIL to format EasyOCR likes
                    img_array = np.array(page_image)
                    result = reader.readtext(np.array(processed_image))
                    
                    # Run OCR
                    result = reader.readtext(img_array)
                    page_lines = []
                    for detection in result:
                        bbox, text, conf = detection
                        color = "green" if (conf is not None and conf > 0.9) else "orange" if (conf is not None and conf > 0.7) else "red"
                        if conf is None:
                            conf_str = "N/A"
                        else:
                            try:
                                conf_str = f"{conf:.2f}"
                            except Exception:
                                conf_str = str(conf)
                        page_lines.append(f"<span style='color:{color}'>[{conf_str}] {text}</span>")
                    page_text = "\n".join(page_lines)
                    # page_text = "\n".join([text for (_, text, _) in result])
                    all_text.append(f"--- Page {i+1} ---\n{page_text}")
                    if page_image.width < 800 or page_image.height < 600:
                       st.warning("Image looks low-resolution. Enhance with Pro for better accuracy? (Coming soon)")
                    
                    ## Add slider for max pages
                    max_pages = st.slider("Max pages to process at once", 1, 10, 5)
                    # then slice your pages list
                    pages = pages[:max_pages]
                    
                    # Show preview in the status box
                    st.markdown(f"**Extracted Text - Page {i+1} (with confidence scores):**", unsafe_allow_html=True)
                    st.text_area("Live Output", "\n".join(page_lines), height=100, key=f"preview_{i}")
                    status.update(label=f"Page {i+1} Complete!", state="complete", expanded=False)
                    if is_blurry(processed_image):
                       st.warning(f"Page {i+1} looks blurry — enhancement recommended for better accuracy.")
                
                
        else:
            # Handle single images
            image = Image.open(uploaded_file).convert("RGB")
            processed_image = preprocess_image(image)
            page_image = preprocess_image(image)
           
            # Then run OCR on processed_image as before
            ## st.image(processed_image, caption="Processed Image (sharpened)", use_column_width=True)
           # use_super_res = st.checkbox("Use Super Resolution (Pro feature - enhances low-res images)", value=False)
           # if use_super_res:
           #     with st.spinner("Enhancing image with EDSR..."):
           #         image = enhance_with_edsr(image)
           #     st.image(image, caption="Enhanced Image (EDSR ×4)", width=800)
            
            esrgan = st.checkbox("Use ESRGAN Enhancement (Pro feature)", value=False)
            if st.button("Enhance with ESRGAN"):
                model_structure = _loader.load_esrgan_model(scale=4) 
                with st.spinner("Upscaling via HuggingFace Weights..."):
                        try:
                         # Initialize the engine
                         # 2. Pass that working model into your Enhancer class
                         enhancer = ESRGANEnhancer(model=model_structure)
                         
                         # 3. Run your process
                         upscaled_image = enhancer.process(image)
                         
                         st.image(upscaled_image, caption="Enhanced via ESRGAN", use_column_width=True)
                        except Exception as e:
                            st.error(f"Inference Error: {str(e)}")
                            st.info("Check if model weights match the input dimension")

            # apply enhancement if toggled
            use_enhancement = st.checkbox("Enhance image for better quality (fix blurry/low-res)", value=False)
            st.image(image, caption="Uploaded Image", width=600)
            with st.spinner("Scanning image..."):
                result = reader.readtext(np.array(processed_image))
                page_lines = []
                for bbox, text, conf in result:
                    page_lines.append(text)
                   # color = "green" if (conf is not None and conf > 0.9) else "orange" if (conf is not None and conf > 0.7) else "red"
                   # if conf is None:
                   #     conf_str = "N/A"
                   # else:
                   #     try:
                   #         conf_str = f"{conf:.2f}"
                   #     except Exception:
                   #         conf_str = str(conf)
                   
                page_text = "\n".join(page_lines)
                #all_text.append(page_text)
                st.markdown(page_text)
                st.text_area("Live Output", "\n".join(page_lines), height=300)
                
                
            if page_lines:
                st.subheader("Text Extraction Complete!")
                
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Open in an editable page", use_container_width=True):
                        # store the session so we can show it on next rerun
                        st.session_state['show_editor'] = True
                        st.session_state['ocr_text'] = page_lines
                        st.rerun()
              
                with col2:
                    if st.button("Copy to Clipboard", use_container_width=True):
                        # Copy to clipboard
                        st.write("Text copied to clipboard!")
                        st.session_state['clipboard_text'] = page_lines
                        
            if st.session_state.get('show_editor', False):
                st.markdown("### Editable Text below")
                edited_text = st.text_area(
                    "Full Extracted Text(Edit as needed)",
                    value=st.session_state['ocr_text'],
                    height=400,
                    key="editor_area"
                )
                col_save, col_save2 = st.columns(2)
                with col_save:
                    if st.button("Save as .txt"):
                        st.download_button(
                            label="Download Edited Text",
                            data=edited_text,
                            file_name="edited_ocr_result.txt",
                            mime="text/plain"
                        )
                with col_save2:
                    if st.button("Copy edited text"):
                        st.write("Edited text copied to clipboard!")
                        
                if st.button("<- Back to main view"):
                    st.session_state['show_editor'] = False
                    st.rerun()
                        
            if image.width < 800 or image.height < 600:
               st.warning("Image looks low-resolution. Enhance with Pro for better accuracy? (Coming soon)")    
       
       

        # --- FINAL OUTPUT ---
      ##  if all_text:
      ##      st.divider()
      ##      st.subheader("Final Results")
      ##      extracted_text = "\n\n".join(all_text)
      ##      st.text_area("All Extracted Content", extracted_text, height=400)
      ##      
      ##      st.download_button("Download Text", extracted_text, file_name="ocr_result.txt")
          
        
    except Exception as e:
        st.error(f"Error: {str(e)}")