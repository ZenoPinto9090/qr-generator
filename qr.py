import base64
import io

import qrcode
from flask import Flask, render_template_string, request

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QR code maker</title>
<style>
  :root { --bg:#eef2f7; --ink:#14213d; --accent:#2a4fd6; --card:#ffffff; --line:#c9d3e3; }
  * { box-sizing: border-box; }
  body { margin:0; min-height:100vh; display:grid; place-items:center; padding:24px;
         background:var(--bg); color:var(--ink); font-family: Georgia, "Times New Roman", serif; }
  main { width:100%; max-width:460px; background:var(--card); border:2px solid var(--ink);
         padding:28px; box-shadow:8px 8px 0 var(--ink); }
  h1 { margin:0 0 6px; font-size:1.8rem; }
  p.sub { margin:0 0 20px; color:#4a5670; }
  label { display:block; margin:14px 0 6px; font-weight:bold; }
  input { width:100%; padding:11px; font-size:1rem; border:2px solid var(--line); font-family:inherit; }
  input:focus-visible, button:focus-visible, a:focus-visible { outline:3px solid var(--accent); outline-offset:2px; }
  button { margin-top:20px; width:100%; padding:13px; font-size:1.05rem; font-family:inherit;
           background:var(--accent); color:#fff; border:2px solid var(--ink); cursor:pointer; }
  button:hover { background:#1c3aa8; }
  .result { margin-top:26px; text-align:center; }
  .result img { width:100%; max-width:300px; image-rendering:pixelated; border:2px solid var(--ink); }
  .download { display:inline-block; margin-top:12px; color:var(--accent); font-weight:bold; }
  .error { margin-top:16px; color:#b00020; }
</style>
</head>
<body>
<main>
  <h1>QR code maker</h1>
  <p class="sub">Type a link or any text and get a QR code you can download.</p>

  <form method="post">
    <label for="data">Text or link</label>
    <input id="data" name="data" value="{{ data or '' }}" placeholder="https://example.com" required>

    <label for="filename">File name</label>
    <input id="filename" name="filename" value="{{ filename or 'qrcode' }}" required>

    <button type="submit">Generate QR code</button>
  </form>

  {% if error %}<p class="error">{{ error }}</p>{% endif %}

  {% if img %}
  <div class="result">
    <img src="data:image/png;base64,{{ img }}" alt="QR code for {{ data }}">
    <br>
    <a class="download" href="data:image/png;base64,{{ img }}" download="{{ filename }}.png">Download PNG</a>
  </div>
  {% endif %}
</main>
</body>
</html>
"""


def make_qr_base64(data):
    # Same settings as your original qr.py
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    image = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


@app.route("/", methods=["GET", "POST"])
def index():
    data = filename = img = error = None

    if request.method == "POST":
        data = request.form.get("data", "").strip()
        filename = request.form.get("filename", "").strip() or "qrcode"
        # keep the file name safe
        filename = "".join(c for c in filename if c.isalnum() or c in "-_") or "qrcode"

        if not data:
            error = "Enter some text or a link first."
        else:
            try:
                img = make_qr_base64(data)
            except Exception:
                error = "That text is too long for a QR code. Try something shorter."

    return render_template_string(PAGE, data=data, filename=filename, img=img, error=error)


if __name__ == "__main__":
    app.run(debug=True)
