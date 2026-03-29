 This project implements an AI-powered CCTV surveillance system that uses deep learning and computer vision techniques to monitor, detect, and analyze suspicious activities in real-time.
The system enhances traditional security by automatically identifying threats such as unauthorized access, unusual motion, or human presence, making it useful for homes, offices, and public spaces.

project structure:
ai-cctv-security/
│── dataset/
│── models/
│   └── detection_model.h5
│
│── src/
│   ├── camera.py
│   ├── detect.py
│   ├── alert.py
│   ├── utils.py
│
│── app/
│   └── app.py
│
│── outputs/
│   └── recordings/
│
│── requirements.txt
│── README.md


📊 Results
Real-time detection accuracy: ~XX%
Fast processing with optimized models
Works on live camera feed and recorded videos

📸 Sample Output
Input: Live CCTV footage
Output:
🟢 Normal Activity
🔴 Suspicious Activity Detected
🚨 Alert Triggered
