import os
import streamlit as st
from PIL import Image
import tempfile
import segno
import base64
import io
from pyzxing import BarCodeReader

# Function to generate QR code for the image path or URL
def generate_qr(data):
    try:
        qr = segno.make(data)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr.save(temp_file.name, scale=6)
        return temp_file.name
    except Exception as e:
        return f"QR code generation failed: {e}"

# Function to decode a QR code from an uploaded image
def decode_qr(image):
    reader = BarCodeReader()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    image.save(temp_file.name)
    result = reader.decode(temp_file.name)
    os.unlink(temp_file.name)
    if result and "parsed" in result[0]:
        return result[0]["parsed"]
    else:
        return "No QR code detected"

# Streamlit App UI
st.title("QR Code Generator and Decoder")

# Tabs for switching between Image to QR Code and QR Code to Image
option = st.radio("Choose a Function", ["Image to QR Code", "QR Code to Image"])

if option == "Image to QR Code":
    st.header("Upload an Image to Generate QR Code")
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.write("Generating QR Code...")

        # Generate QR Code for the image path
        temp_dir = tempfile.mkdtemp()
        image_path = os.path.join(temp_dir, "image.png")
        image.save(image_path)
        qr_image_path = generate_qr(image_path)

        if "failed" in qr_image_path:
            st.error(qr_image_path)
        else:
            qr_image = Image.open(qr_image_path)
            st.image(qr_image, caption="Generated QR Code", use_column_width=True)

elif option == "QR Code to Image":
    st.header("Upload a QR Code Image to Decode")
    uploaded_qr_image = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])

    if uploaded_qr_image:
        qr_image = Image.open(uploaded_qr_image)
        st.image(qr_image, caption="Uploaded QR Code", use_column_width=True)
        st.write("Decoding QR Code...")

        decoded_data = decode_qr(qr_image)

        if "No QR code detected" in decoded_data:
            st.error(decoded_data)
        else:
            st.write(f"Decoded Data: {decoded_data}")

            # Check if the decoded data is a file path or base64 image
            if os.path.exists(decoded_data):
                img = Image.open(decoded_data)
                st.image(img, caption="Decoded Image", use_column_width=True)
            else:
                try:
                    img_data = base64.b64decode(decoded_data)
                    img = Image.open(io.BytesIO(img_data))
                    st.image(img, caption="Decoded Image", use_column_width=True)
                except Exception as e:
                    st.error(f"Error decoding image from QR code: {e}")
