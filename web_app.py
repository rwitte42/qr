from __future__ import annotations

import base64
import os
import re
import signal
import threading
from io import BytesIO
from typing import Final
from urllib.parse import quote, urlencode

import qrcode
from flask import Flask, abort, render_template, request

APP_PORT: Final[int] = 8000
APP_HOST: Final[str] = "127.0.0.1"

app = Flask(__name__)

_EMAIL_RE = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")


def _make_png_data_url(data: str) -> str:
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _mailto_uri(email: str, subject: str | None, body: str | None) -> str:
    params: dict[str, str] = {}
    if subject:
        params["subject"] = subject
    if body:
        params["body"] = body

    # Mailto format is: mailto:user@example.com?subject=...&body=...
    if params:
        return f"mailto:{email}?{urlencode(params, quote_via=quote)}"
    return f"mailto:{email}"


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/generate")
def generate():
    mode = (request.form.get("mode") or "url").strip().lower()

    error: str | None = None
    qr_value: str | None = None
    qr_data_url: str | None = None

    if mode == "url":
        url = (request.form.get("url") or "").strip()
        if not url:
            error = "URL is required."
        else:
            qr_value = url
    elif mode == "email":
        email = (request.form.get("email") or "").strip()
        subject = (request.form.get("subject") or "").strip() or None
        body = (request.form.get("body") or "").strip() or None

        if not email:
            error = "E-mail address is required."
        elif not _EMAIL_RE.match(email):
            error = "Please enter a valid e-mail address."
        else:
            qr_value = _mailto_uri(email=email, subject=subject, body=body)
    else:
        error = "Unknown mode."

    if qr_value and not error:
        qr_data_url = _make_png_data_url(qr_value)

    return render_template(
        "index.html",
        mode=mode,
        error=error,
        qr_value=qr_value,
        qr_data_url=qr_data_url,
        form={
            "url": request.form.get("url", ""),
            "email": request.form.get("email", ""),
            "subject": request.form.get("subject", ""),
            "body": request.form.get("body", ""),
        },
    )


@app.post("/shutdown")
def shutdown():
    # Only allow local shutdown (this is a local dev tool).
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        abort(403)

    # Werkzeug no longer exposes a stable "server.shutdown" hook; for a local dev tool
    # it's fine to stop by signaling the current process.
    pid = os.getpid()

    def _stop():
        try:
            os.kill(pid, signal.SIGINT)
        except Exception:
            os._exit(0)

    # Trigger shutdown after we send the response back to the browser.
    threading.Timer(0.2, _stop).start()
    return render_template("shutdown.html")


if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, debug=False)



