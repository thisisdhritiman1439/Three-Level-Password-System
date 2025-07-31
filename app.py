import streamlit as st
import os
import hashlib
import json
import pyqrcode
import random
import tempfile
from PIL import Image
import imagehash

# ----------------- Setup -----------------
st.set_page_config("🔐 3-Level Auth System", layout="centered")
st.title("🔐 Welcome To Three-Level Password Authentication System")

# Create user data folder
if not os.path.exists("user_data"):
    os.makedirs("user_data")

# ----------------- Utility Functions -----------------
def hash_password(password):
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

    return True, "Registration successful."

def authenticate_user(email, password):
    user_dir = f"user_data/{email}"
    meta_path = f"{user_dir}/meta.json"
    if not os.path.exists(meta_path):
        return False, "User not found."
    with open(meta_path) as f:
        meta = json.load(f)
    if hash_password(password) != meta["password"]:
        return False, "Incorrect password."
    return True, user_dir

def generate_qr_code():
    code = str(random.randint(100000, 999999))
    qr = pyqrcode.create(code)
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    qr.png(path, scale=6)
    return code, path

def verify_qr_code(user_input, actual_code):
    return user_input == actual_code

def verify_image(uploaded_image, stored_image_path):
    uploaded_hash = imagehash.average_hash(Image.open(uploaded_image))
    stored_hash = imagehash.average_hash(Image.open(stored_image_path))
    return uploaded_hash - stored_hash < 5

# ----------------- Session Defaults -----------------
for key in ["stage", "email", "user_dir", "qr_code", "qr_path"]:
    if key not in st.session_state:
        st.session_state[key] = "start" if key == "stage" else None

# ----------------- Navigation -----------------
menu = st.sidebar.radio("Navigation", ["Register", "Login", "Reset"])

# ----------------- Register -----------------
if menu == "Register":
    st.subheader("📝 User Registration")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    image = st.file_uploader("Upload Face Image (JPG)", type=["jpg"])
    file = st.file_uploader("Upload File to Secure")

    if st.button("Register"):
        if email and password and image and file:
            success, msg = register_user(email, password, image, file)
            if success:
                st.success(msg)
            else:
                st.error(msg)
        else:
            st.warning("Please fill in all fields to register.")

# ----------------- Login Flow -----------------
elif menu == "Login":
    stage = st.session_state.stage

    # Step 1: Email + Password
    if stage == "start":
        st.subheader("🔑 Step 1: Login Credentials")
        email = st.text_input("Login Email")
        password = st.text_input("Login Password", type="password")
        if st.button("Login"):
            success, result = authenticate_user(email, password)
            if success:
                st.session_state.email = email
                st.session_state.user_dir = result
                qr_code, qr_path = generate_qr_code()
                st.session_state.qr_code = qr_code
                st.session_state.qr_path = qr_path
                st.session_state.stage = "qr"
            else:
                st.error(result)

    # Step 2: QR Code
    elif stage == "qr":
        st.subheader("📷 Step 2: QR Code Verification")
        st.image(st.session_state.qr_path, caption="Scan this QR Code to get 6-digit code")
        user_input = st.text_input("Enter 6-digit code from QR")
        if st.button("Verify Code"):
            if verify_qr_code(user_input, st.session_state.qr_code):
                st.success("✅ Code verified. Proceed to face verification.")
                st.session_state.stage = "face"
            else:
                st.error("❌ Incorrect code. Restarting login.")
                st.session_state.stage = "start"

    # Step 3: Face Image
    elif stage == "face":
        st.subheader("🖼️ Step 3: Face Verification")
        image = st.file_uploader("Upload the same face image again", type=["jpg"])
        if st.button("Verify Image"):
            if image:
                stored_path = f"{st.session_state.user_dir}/image.jpg"
                if verify_image(image, stored_path):
                    st.success("🎉 Login Successful!")
                    st.session_state.stage = "access"
                else:
                    st.error("❌ Face did not match. Restarting.")
                    st.session_state.stage = "start"
            else:
                st.warning("Please upload an image to verify.")

    # Final Access
    elif stage == "access":
        st.subheader("🔓 Access Granted")
        file_path = f"{st.session_state.user_dir}/secure_file"
        with open(file_path, "rb") as f:
            st.download_button("📥 Download Your File", f, file_name="your_file")
        if st.button("Logout"):
            st.session_state.stage = "start"
            st.session_state.email = None
            st.session_state.user_dir = None
            st.success("Logged out.")

# ----------------- Reset -----------------
elif menu == "Reset":
    st.session_state.stage = "start"
    st.session_state.email = None
    st.session_state.user_dir = None
    st.success("Session has been reset.")
