import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove
from skimage import exposure

def adaptive_contrast(image):
    """CLAHE-based contrast enhancement"""
    img_np = np.array(image)
    lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l_clahe = clahe.apply(l)
    lab = cv2.merge((l_clahe, a, b))
    return Image.fromarray(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB))

def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    
    # Noise reduction
    image = image.filter(ImageFilter.MedianFilter(3))
    
    # Adaptive contrast enhancement
    image = adaptive_contrast(image)
    
    # Smart sharpening using Unsharp Mask
    image = image.filter(ImageFilter.UnsharpMask(
        radius=2, 
        percent=150, 
        threshold=3
    ))
    
    return image

def remove_background(image):
    # Use session for better performance with MODNet
    from rembg.sessions import sessions
    session = sessions['modnet']
    return remove(
        image, 
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10
    )

def refine_alpha_mask(alpha):
    """Refine alpha mask using guided filtering"""
    alpha = alpha.astype(np.float32) / 255.0
    refined_alpha = cv2.ximgproc.guidedFilter(
        guide=alpha,
        src=alpha,
        radius=5,
        eps=0.01
    )
    return (refined_alpha * 255).astype(np.uint8)

def post_process(image):
    # Convert to OpenCV format and split channels
    img_np = np.array(image)
    if img_np.shape[-1] == 4:
        b, g, r, a = cv2.split(img_np)
    else:
        b, g, r = cv2.split(img_np)
        a = np.ones_like(b) * 255
    
    # Refine alpha mask
    a = refine_alpha_mask(a)
    
    # Edge-aware smoothing
    smooth_a = cv2.edgePreservingFilter(a, flags=cv2.RECURS_FILTER, sigma_s=10, sigma_r=0.05)
    
    # Combine channels
    return cv2.merge((b, g, r, smooth_a))

# ---- Optimized Workflow ----
image_path = "your_image.jpg"

# Preprocessing
processed_image = preprocess_image(image_path)

# Background removal
bg_removed = remove_background(processed_image)

# Post-processing
final_image = post_process(bg_removed)

# Save result
Image.fromarray(final_image).save("final_output.png", "PNG", quality=100)

print("✅ Enhanced background removal completed!")