import streamlit as st
import os
import hashlib
import json
import pyqrcode
import random
import tempfile
from PIL import Image
import imagehash

# --------------------------- Utilities ---------------------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password, image, file):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    user_dir = f"user_data/{email}"
    os.makedirs(user_dir, exist_ok=True)

    with open(f"{user_dir}/image.jpg", "wb") as f:
        f.write(image.getbuffer())
    with open(f"{user_dir}/secure_file", "wb") as f:
        f.write(file.getbuffer())

    meta = {"password": hash_password(password)}
    with open(f"{user_dir}/meta.json", "w") as f:
        json.dump(meta, f)

    return True, "✅ Registration successful."

def authenticate_user(email, password):
    user_dir = f"user_data/{email}"
    meta_path = os.path.join(user_dir, "meta.json")
    if not os.path.exists(meta_path):
        return False, "User not found."

    with open(meta_path, "r") as f:
        meta = json.load(f)

    if hash_password(password) != meta["password"]:
        return False, "Incorrect password."

    return True, user_dir

def generate_qr_code():
    code = str(random.randint(100000, 999999))
    qr = pyqrcode.create(code)
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    qr.png(temp_path, scale=6)
    return code, temp_path

def verify_qr_code(user_input, actual_code):
    return user_input == actual_code

def verify_image(uploaded_image, stored_image_path):
    uploaded_hash = imagehash.average_hash(Image.open(uploaded_image))
    stored_hash = imagehash.average_hash(Image.open(stored_image_path))
    return uploaded_hash - stored_hash < 5

# --------------------------- Streamlit App ---------------------------

st.set_page_config("Three-Level Password System", layout="centered")
st.title("🔐 Three-Level Password Authentication System")

# Session management
if "stage" not in st.session_state:
    st.session_state.stage = "register"

# --------------------------- Registration ---------------------------
if st.session_state.stage == "register":
    st.subheader("📝 Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    image = st.file_uploader("Upload Face Image (JPG only)", type=["jpg"])
    file = st.file_uploader("Upload File to Secure", type=None)

    if st.button("Register"):
        if email and password and image and file:
            success, msg = register_user(email, password, image, file)
            st.success(msg) if success else st.error(msg)
            if success:
                st.session_state.stage = "login"
        else:
            st.warning("Please fill all fields to register.")

# --------------------------- Login Step 1 ---------------------------
elif st.session_state.stage == "login":
    st.subheader("🔐 Login - Step 1")
    email = st.text_input("Login Email")
    password = st.text_input("Login Password", type="password")

    if st.button("Login"):
        success, result = authenticate_user(email, password)
        if success:
            st.session_state.user_dir = result
            st.session_state.email = email
            st.session_state.qr_code, st.session_state.qr_path = generate_qr_code()
            st.session_state.stage = "factor2"
        else:
            st.error(result)

# --------------------------- Login Step 2 ---------------------------
elif st.session_state.stage == "factor2":
    st.subheader("📷 Step 2: QR Code Verification")
    st.image(st.session_state.qr_path, caption="Scan this QR Code to get your 6-digit code")
    input_code = st.text_input("Enter 6-digit code from scanned QR")

    if st.button("Verify Code"):
        if verify_qr_code(input_code, st.session_state.qr_code):
            st.success("✅ Code verified.")
            st.session_state.stage = "factor3"
        else:
            st.error("❌ Incorrect code. Restarting login.")
            st.session_state.stage = "login"

# --------------------------- Login Step 3 ---------------------------
elif st.session_state.stage == "factor3":
    st.subheader("🖼️ Step 3: Face Image Verification")
    uploaded_image = st.file_uploader("Upload the same face image again", type=["jpg"])

    if st.button("Verify Image"):
        if uploaded_image:
            stored_image_path = os.path.join(st.session_state.user_dir, "image.jpg")
            if verify_image(uploaded_image, stored_image_path):
                st.success("✅ Image matched. Login successful!")
                st.session_state.stage = "access"
            else:
                st.error("❌ Image did not match. Restarting login.")
                st.session_state.stage = "login"
        else:
            st.warning("Please upload an image to verify.")

# --------------------------- Access File ---------------------------
elif st.session_state.stage == "access":
    st.subheader("🎉 Access Granted")
    secure_file_path = os.path.join(st.session_state.user_dir, "secure_file")

    with open(secure_file_path, "rb") as f:
        st.download_button("📥 Download Secured File", f, file_name="your_secure_file")

    if st.button("Logout"):
        st.session_state.stage = "login"
