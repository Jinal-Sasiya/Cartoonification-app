import cv2
import numpy as np
from flask import Flask, render_template, request, send_file
import os
import io

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cartoonify(img):
    img = cv2.resize(img, (600, 600))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, 5)

    edges = cv2.adaptiveThreshold(
        gray_blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9, 9
    )

    color = cv2.bilateralFilter(img, 9, 250, 250)
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    return cartoon

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]

        if file.filename == "":
            return "No file uploaded"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        img = cv2.imread(filepath)

        if img is None:
            return "Error reading image"

        cartoon = cartoonify(img)

        # Convert to bytes (IMPORTANT FIX)
        _, buffer = cv2.imencode('.jpg', cartoon)
        io_buf = io.BytesIO(buffer)

        return send_file(
            io_buf,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='cartoon.jpg'
        )

    return render_template("index.html")


# REQUIRED FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
