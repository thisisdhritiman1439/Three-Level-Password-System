# Three-Level-Password-System

# 🔐 Three-Factor Authentication System

A secure **Three-Factor Authentication System** built using **Python** and **Streamlit**, designed for both local and cloud (Streamlit Cloud) deployment.

This system authenticates users in **three layers**:
1. **Something You Have** – Email & Password
2. **Something You Know** – QR Code Verification (User scans a QR to reveal a code they must input)
3. **Something You Are** – Face Recognition (via image upload for compatibility with Streamlit Cloud)

---

## 🚀 Features

- 📧 Email and Password Login
- 🧠 QR Code-based Secret Code Verification
- 🖼️ Facial Recognition via Image Matching *(compatible with Streamlit Cloud)*
- 🗃️ Secure access to uploaded files upon successful authentication
- 📝 Records login attempts with time and user ID into a CSV log
- 🧭 Clean UI with navigation: Register | Login | Logout
- 💾 Backend file storage with user-wise directories

---

## 📁 Project Structure

```

three-factor-auth/
│
├── app.py                 # Main Streamlit app
├── users.json             # Stores user registration data
├── login\_log.csv          # Logs successful login attempts
├── face\_data/             # Stores uploaded reference face images
├── secure\_files/          # Stores user-uploaded private files
└── requirements.txt       # Python dependencies

````

---

## ⚙️ Setup Instructions

### ✅ 1. Clone the repository
```bash
git clone https://github.com/your-username/three-factor-auth.git
cd three-factor-auth
````

### ✅ 2. Install dependencies

```bash
pip install -r requirements.txt
```

### ✅ 3. Run the app locally

```bash
streamlit run app.py
```

> 💡 Note: To use webcam-based face recognition, install `opencv-python` and run locally. For Streamlit Cloud, use **image upload** method.

---

## 🌐 Deployment on Streamlit Cloud

### ✅ Steps:

1. Push your code to a **public GitHub repository**
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Click **“New app”**, link to your GitHub repository
4. Select `app.py` as the entry point
5. Include a `requirements.txt` file with these packages:

```txt
streamlit
Pillow
face_recognition
pyqrcode
pypng
```

6. **Do not include `opencv-python`** if using image upload for facial verification (as `cv2` causes issues on Streamlit Cloud)

---

## 🔐 Authentication Flow

1. **Registration**

   * Name, Email, Password (8+ chars, alphanumeric/symbols)
   * Face Image Upload
2. **Login**

   * Step 1: Email & Password
   * Step 2: QR Scan to get 6-digit code → User inputs code
   * Step 3: Upload a face image → Match with registered image
3. ✅ Access to secure uploaded file

---

## 🧾 Logging

Each successful login is stored in `login_log.csv`:

* Email
* Login Timestamp

---

## 🛡️ Security Measures

* Passwords hashed using SHA-256
* QR code generated with random 6-digit value
* Face matching with `face_recognition`'s encoding comparator
* All uploaded files and images stored user-wise and isolated

---

## 👨‍💻 Author

**Dhritiman Bera**
Project Lead & Developer
🔗 GitHub: [thisisdhritiman1439](https://github.com/thisisdhritiman1439)

---

## 📄 License

This project is licensed under the **MIT License**.

```


