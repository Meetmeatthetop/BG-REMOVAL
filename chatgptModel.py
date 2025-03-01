import cv2
import numpy as np
from torchvision import transforms
from rembg import remove
from PIL import Image, ImageEnhance

# ---- Step 1: Preprocess Image ----
def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")

    # Enhance Contrast
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.5)  # Increase contrast

    # Sharpen Image
    sharpness = ImageEnhance.Sharpness(image)
    image = sharpness.enhance(2.0)  # Increase sharpness

    return image

# ---- Step 2: Background Removal Using MODNet or U2-Net ----
def remove_background(image, model="u2net_human_seg"):  
    return remove(image, model_name=model)

# ---- Step 3: Post-processing with OpenCV ----
def post_process(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Convert to grayscale and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

    # Create a transparent background (RGBA)
    b, g, r = cv2.split(image)
    rgba = [b, g, r, alpha]
    final_image = cv2.merge(rgba, 4)

    # Smooth edges using GaussianBlur
    blurred_alpha = cv2.GaussianBlur(alpha, (5, 5), 0)
    final_image[:, :, 3] = blurred_alpha  # Apply smoothed alpha mask

    return final_image

# ---- Run Workflow ----
image_path = "your_image.jpg"
processed_image = preprocess_image(image_path)  # Step 1
bg_removed = remove_background(processed_image, model="modnet")  # Step 2
bg_removed.save("output.png")  # Save before post-processing

# Apply Post-processing
final_result = post_process("output.png")
cv2.imwrite("final_output.png", final_result)

print("✅ Background removal completed with enhancements!")
