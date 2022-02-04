import logging
import os
import tempfile
from uuid import uuid4
import cv2
import numpy as np

import PyPDF2
from PIL import Image
from pdf2image import convert_from_path
from pytesseract import image_to_string, TesseractError

# large images within PDFs cause a decompression bomb error (a form of protection from abuse)
# this setting allows the user to configure how large an image they are comfortable processing
# The tradeoff to a large max size here is memory consumption, which the user can self-regulate
# using this setting.  If they do not set the variable, it remains at the default for PIL.

MAX_IMAGE_PIXELS = os.environ.get('MAX_IMAGE_PIXELS', 178956970)  # this is the default PIL max size
Image.MAX_IMAGE_PIXELS = int(MAX_IMAGE_PIXELS)


class FileOcrResult:
    def __init__(self, pages):
        self.pages = pages


def __get_pdf_file_reader(file):
    try:
        return PyPDF2.PdfFileReader(file, strict=False)
    except PyPDF2.utils.PdfReadError as e:
        logging.warning(f"Error reading PDF: {str(e)}")
        return None
    except ValueError as e:
        logging.warning(f"Error reading PDF - {e.args}")
        return None


def pdf_page_as_image(filename, page_num=0, is_preview=False):
    if not is_preview:
        # high dpi and grayscale for the best OCR result
        pages = convert_from_path(filename, dpi=600, grayscale=True)
    else:
        pages = convert_from_path(filename)
    temp_file = f"{tempfile.gettempdir()}/{uuid4()}.png"
    pages[page_num].save(temp_file, format="PNG")
    return temp_file


def __get_image(filename):
    try:
        return Image.open(filename)
    except OSError:
        print(f"Error reading image: {filename}")
        return None


def __rotate_image(filename):
    """
     Tries to deskew the image; will not rotate it more than 90 degrees
    :param filename:
    :return: rotated file
    """
    # Inspired by https://www.pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/
    image = cv2.imread(filename, cv2.IMREAD_COLOR) # Initially decode as color
    if image is None:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    threshold = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coordinates = np.column_stack(np.where(threshold > 0))
    angle = cv2.minAreaRect(coordinates)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (height, width) = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, matrix, (width, height),
                                   flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    temp_file = f"{tempfile.gettempdir()}/{uuid4()}.png"
    cv2.imwrite(temp_file, rotated_image)
    return temp_file


def extract_text_from_pdf(filename, language="eng"):
    with open(filename, "rb") as file:
        pdf_reader = __get_pdf_file_reader(file)
        if pdf_reader is None:
            return None
        if pdf_reader.isEncrypted:
            print('    --NOTICE: This file is encrypted and cannot be read by Joplin OCR\n')
            return None
        text = list()
        preview_file = None
        for i in range(pdf_reader.numPages):
            page = pdf_reader.getPage(i)
            extracted_image = pdf_page_as_image(filename, i)
            extracted_text_list = extract_text_from_image(extracted_image, language=language)
            os.remove(extracted_image)
            if extracted_text_list is not None:
                extracted_text = "".join(extracted_text_list.pages)
                print(f"Page {i + 1} of {pdf_reader.numPages} processed successfully.")
            else:
                extracted_text = ""
                print(f"Page {i + 1} of {pdf_reader.numPages} processed with no text recognized.")
            embedded_text = "" + page.extractText()
            if len(embedded_text) > len(extracted_text):
                selected_text = embedded_text
            else:
                selected_text = extracted_text
            selected_text = selected_text.strip()
            # 10 or fewer characters is probably just garbage
            if len(selected_text) > 10:
                text.extend([selected_text])
        return FileOcrResult(text)


def extract_text_from_image(filename, auto_rotate=False, language="eng"):
    try:
        img = __get_image(filename)
        text = image_to_string(img, lang=language)
        if auto_rotate:
            rotated_image = __rotate_image(filename)
            if rotated_image is None:
                return None
            result = extract_text_from_image(filename, auto_rotate=False, language=language)
            os.remove(rotated_image)
            if result is None:
                return None
            text = result.pages[0]
        # 10 or fewer characters is probably just garbage
        if len(text.strip()) > 10:
            return FileOcrResult([text.strip()])
        else:
            return None
    except TesseractError as e:
        print(f"TesseractError {e.message}")
        return None
