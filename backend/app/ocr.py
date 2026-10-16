import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
from PIL import Image, ImageOps

def orient_image(image: Image.Image, rotation: int = 0) -> Image.Image:
    """Correct EXIF orientation and apply the selected rotation."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    return image.rotate(rotation, expand=True)


def run_ocr_multi(
    image: Image.Image,
    preferred_page_mode: int = 6,
) -> str:
    """Run whole-image OCR with a few layouts and contrast variants."""
    gray = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2GRAY)

    enlarged = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC,
    )

    enhanced = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    ).apply(enlarged)

    variants = [enlarged, enhanced]
    page_modes = list(dict.fromkeys([preferred_page_mode, 4, 6, 11]))
    results = []

    for variant in variants:
        for mode in page_modes:
            text = pytesseract.image_to_string(
                Image.fromarray(variant),
                config=f"--oem 3 --psm {mode}",
            ).strip()

            if text and text not in results:
                results.append(text)

    return results[0] if results else ""
