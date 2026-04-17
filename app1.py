import cv2
import numpy as np
from flask import Flask, render_template, request
import os
import time
from flask import redirect, url_for

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)


# 🎨 Cartoon Filter
def cartoonify(img):
    img = cv2.resize(img, (600, 600))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)

    edges = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9, 5
    )

    color = cv2.bilateralFilter(img, 7, 150, 150)

    return cv2.bitwise_and(color, color, mask=edges)


# ✏️ Sketch Filter
def sketchify(img):
    img = cv2.resize(img, (600, 600))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)

    sketch = cv2.divide(gray, blur, scale=256)

    return sketch


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        file = request.files.get("image")

        if not file or file.filename == "":
            return redirect(url_for("index"))

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        img = cv2.imread(filepath)

        filter_type = request.form.get("filter", "Cartoon")

        if filter_type == "Sketch":
            output = sketchify(img)
        else:
            output = cartoonify(img)

        # Save images
        timestamp = int(time.time())
        original_filename = f"original_{timestamp}.jpg"
        output_filename = f"output_{timestamp}.jpg"

        cv2.imwrite(os.path.join(STATIC_FOLDER, original_filename), img)
        cv2.imwrite(os.path.join(STATIC_FOLDER, output_filename), output)

        # ✅ Redirect WITH data
        return redirect(url_for(
            "index",
            original=original_filename,
            output=output_filename,
            filter=filter_type
        ))

    # ✅ GET request
    original_file = request.args.get("original")
    output_file = request.args.get("output")
    selected_filter = request.args.get("filter")

    return render_template(
        "index.html",
        original_file=original_file,
        output_file=output_file,
        selected_filter=selected_filter
    )

# Required for local + Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
