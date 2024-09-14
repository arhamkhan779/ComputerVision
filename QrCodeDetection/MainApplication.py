import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode

# Function to convert OpenCV image to PIL image
def opencv_to_pil(image):
    if image is None or image.size == 0:
        return None
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

# Function to convert PIL image to OpenCV image
def pil_to_opencv(image):
    if image is None or image.size == 0:
        return None
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

# Function to resize image
def resize_image(image, width=400):  # Smaller width for better UI fit
    if image is None:
        return None
    height, original_width = image.shape[:2]
    aspect_ratio = height / original_width
    new_height = int(width * aspect_ratio)
    resized_image = cv2.resize(image, (width, new_height), interpolation=cv2.INTER_LINEAR)
    return resized_image

# Streamlit UI
st.set_page_config(page_title="QR Code Decoder", page_icon=":camera:", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stApp {
        background-color: #f9f7e9; /* Light yellow background */
    }
    .title {
        text-align: center;
        color: #f4a300; /* Dark yellow */
        font-size: 2.5em;
        margin-top: 1em;
    }
    .stFileUploader {
        text-align: center;
        margin-top: 1em;
    }
    .stImage {
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 100%;
        height: auto;
    }
    .data {
        font-size: 1.2em;
        color: #333;
        margin: 1em 0;
    }
    .container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
    }
    .image-container {
        flex: 1;
        max-width: 50%;
        margin: 1em;
    }
    .text-container {
        flex: 1;
        max-width: 50%;
        margin: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Title of the app
st.markdown('<div class="title">QR Code Decoder</div>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # Read and process the image
        image_pil = Image.open(uploaded_file).convert('RGB')  # Ensure the image is in RGB mode
        image_opencv = pil_to_opencv(image_pil)

        if image_opencv is None:
            st.error("Error converting PIL image to OpenCV format.")
        else:
            # Resize the image to a smaller width
            image_opencv_resized = resize_image(image_opencv, width=400)

            # Decode QR code
            decoded_objects = decode(image_opencv_resized)

            # Create a markdown string for decoded data
            decoded_text = ""
            for obj in decoded_objects:
                points = obj.polygon
                if len(points) == 4:
                    pts = np.array(points, dtype=np.int32)
                    cv2.polylines(image_opencv_resized, [pts], True, (0, 255, 0), 2)
                else:
                    hull = cv2.convexHull(np.array(points, dtype=np.float32))
                    cv2.polylines(image_opencv_resized, [np.array(hull, dtype=np.int32)], True, (0, 255, 0), 2)

                # Draw text
                data = obj.data.decode('utf-8')
                decoded_text += f"Decoded Data: {data}\n"
                cv2.putText(image_opencv_resized, data, (points[0].x, points[0].y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Convert back to PIL for displaying in Streamlit
            processed_image_pil = opencv_to_pil(image_opencv_resized)

            if processed_image_pil is None:
                st.error("Error converting processed image to PIL format.")
            else:
                # Display the image and text side-by-side
                col1, col2 = st.columns(2)
                with col1:
                    st.image(processed_image_pil, caption='Processed Image', use_column_width=True)
                with col2:
                    st.markdown(f'<div class="data">{decoded_text}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
