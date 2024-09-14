import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from pyzbar.pyzbar import decode
import numpy as np

# Function to resize image
def resize_image(image, width=400):
    if image is None:
        return None
    aspect_ratio = image.height / image.width
    new_height = int(width * aspect_ratio)
    resized_image = image.resize((width, new_height), Image.LANCZOS)
    return resized_image

# Function to draw bounding boxes and text on image
def draw_boxes_and_text(image, decoded_objects):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()  # Use a default font

    for obj in decoded_objects:
        points = obj.polygon
        if len(points) == 4:
            pts = [(point.x, point.y) for point in points]
        else:
            # If the polygon is not a rectangle, we calculate the convex hull manually
            hull = np.array([point for point in points], dtype=np.float32)
            hull = np.vstack((hull, hull[0]))  # close the polygon
            pts = [(int(point[0]), int(point[1])) for point in hull]

        # Draw bounding box
        draw.line(pts + [pts[0]], fill="green", width=2)

        # Draw text
        data = obj.data.decode('utf-8')
        text_position = (pts[0][0], pts[0][1] - 10)
        draw.text(text_position, data, fill="red", font=font)

    return image

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

        if image_pil is None:
            st.error("Error opening the image file.")
        else:
            # Resize the image to a smaller width
            image_pil_resized = resize_image(image_pil, width=400)

            # Decode QR code
            decoded_objects = decode(np.array(image_pil_resized))

            # Draw boxes and text
            processed_image_pil = draw_boxes_and_text(image_pil_resized, decoded_objects)

            if processed_image_pil is None:
                st.error("Error processing the image.")
            else:
                # Display the image and text side-by-side
                decoded_text = "\n".join([obj.data.decode('utf-8') for obj in decoded_objects])
                col1, col2 = st.columns(2)
                with col1:
                    st.image(processed_image_pil, caption='Processed Image', use_column_width=True)
                with col2:
                    st.markdown(f'<div class="data">{decoded_text}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
