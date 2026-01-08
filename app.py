from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

HTML = """
<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <title>Image Orbit Slideshow</title>
    <style>
        body {
            margin: 0;
            background: radial-gradient(circle, #111, #000);
            color: white;
            font-family: Arial, sans-serif;
            overflow: hidden;
        }

        .ui {
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.6);
            padding: 15px;
            border-radius: 10px;
            z-index: 10;
        }

        .ui input, .ui button {
            margin-top: 8px;
            width: 100%;
        }

        .scene {
            position: absolute;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .center-image {
            width: 220px;
            height: 220px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid white;
            z-index: 2;
            background: #222;
        }

        .orbit {
            position: absolute;
            width: 500px;
            height: 500px;
            border-radius: 50%;
        }

        .orbit img {
            position: absolute;
            width: 90px;
            height: 90px;
            object-fit: cover;
            border-radius: 50%;
            border: 2px solid white;
            top: 50%;
            left: 50%;
            transform-origin: -160px 0;
        }
    </style>
</head>
<body>

<div class="ui">
    <form method="POST" enctype="multipart/form-data">
        <label>Stredový obrázok</label>
        <input type="file" name="center" accept="image/*">

        <label>Obrázky okolo</label>
        <input type="file" name="orbit" accept="image/*" multiple>

        <button type="submit">Nahrať</button>
    </form>

    <label>Rýchlosť</label>
    <input type="range" min="1" max="100" value="30" id="speed">

    <button onclick="toggle()">Play / Pause</button>
</div>

<div class="scene">
    {% if center %}
        <img src="/uploads/{{ center }}" class="center-image">
    {% else %}
        <div class="center-image"></div>
    {% endif %}

    <div class="orbit" id="orbit">
        {% for img in orbit %}
            <img src="/uploads/{{ img }}">
        {% endfor %}
    </div>
</div>

<script>
let angle = 0;
let playing = true;

const orbit = document.getElementById("orbit");
const images = orbit.querySelectorAll("img");
const speedSlider = document.getElementById("speed");

function animate() {
    if (playing) {
        angle += speedSlider.value * 0.02;
        images.forEach((img, i) => {
            const step = 360 / images.length;
            img.style.transform =
                "rotate(" + (angle + i * step) + "deg) translate(200px) rotate(" + -(angle + i * step) + "deg)";
        });
    }
    requestAnimationFrame(animate);
}

function toggle() {
    playing = !playing;
}

animate();
</script>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    center_image = None
    orbit_images = []

    if request.method == "POST":
        if "center" in request.files:
            file = request.files["center"]
            if file.filename:
                filename = "center_" + secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))

        if "orbit" in request.files:
            files = request.files.getlist("orbit")
            for f in files:
                if f.filename:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(UPLOAD_FOLDER, filename))

        return redirect(url_for("index"))

    for f in os.listdir(UPLOAD_FOLDER):
        if f.startswith("center_"):
            center_image = f
        else:
            orbit_images.append(f)

    return render_template_string(
        HTML,
        center=center_image,
        orbit=orbit_images
    )

@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
