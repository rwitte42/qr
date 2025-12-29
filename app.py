from __future__ import annotations

import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote, urlencode

import qrcode
from PIL import Image, ImageTk

APP_TITLE = "QR Code Generator"

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _mailto_uri(email: str, subject: str | None, body: str | None) -> str:
    params: dict[str, str] = {}
    if subject:
        params["subject"] = subject
    if body:
        params["body"] = body
    if params:
        return f"mailto:{email}?{urlencode(params, quote_via=quote)}"
    return f"mailto:{email}"


def _make_qr_image(data: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # qrcode returns a PIL image-like object; normalize to PIL.Image.Image
    if not isinstance(img, Image.Image):
        img = img.get_image()
    return img


class QrApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(640, 520)

        self.mode = tk.StringVar(value="url")

        self.url_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.subject_var = tk.StringVar()

        self._qr_photo: ImageTk.PhotoImage | None = None
        self._qr_image: Image.Image | None = None
        self._is_resetting = False

        self._build_ui()
        self._wire_events()
        self._sync_mode()
        self._sync_buttons()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=14)
        outer.pack(fill="both", expand=True)

        title = ttk.Label(outer, text=APP_TITLE, font=("SF Pro Text", 18, "bold"))
        title.pack(anchor="w")

        mode_row = ttk.Frame(outer, padding=(0, 10, 0, 0))
        mode_row.pack(fill="x")

        ttk.Radiobutton(mode_row, text="URL", value="url", variable=self.mode).pack(
            side="left", padx=(0, 12)
        )
        ttk.Radiobutton(
            mode_row, text="E-mail", value="email", variable=self.mode
        ).pack(side="left")

        self.url_frame = ttk.LabelFrame(outer, text="URL", padding=10)
        self.url_frame.pack(fill="x", pady=(12, 0))

        ttk.Label(self.url_frame, text="URL (required)").pack(anchor="w")
        self.url_entry = ttk.Entry(self.url_frame, textvariable=self.url_var)
        self.url_entry.pack(fill="x", pady=(6, 0))

        self.email_frame = ttk.LabelFrame(outer, text="E-mail", padding=10)
        self.email_frame.pack(fill="x", pady=(12, 0))

        ttk.Label(self.email_frame, text="E-mail address (required)").pack(anchor="w")
        self.email_entry = ttk.Entry(self.email_frame, textvariable=self.email_var)
        self.email_entry.pack(fill="x", pady=(6, 8))

        ttk.Label(self.email_frame, text="Subject (optional)").pack(anchor="w")
        self.subject_entry = ttk.Entry(self.email_frame, textvariable=self.subject_var)
        self.subject_entry.pack(fill="x", pady=(6, 8))

        ttk.Label(self.email_frame, text="Body (optional)").pack(anchor="w")
        self.body_text = tk.Text(self.email_frame, height=5, wrap="word")
        self.body_text.pack(fill="x", pady=(6, 0))

        actions = ttk.Frame(outer, padding=(0, 14, 0, 0))
        actions.pack(fill="x")

        self.generate_btn = ttk.Button(actions, text="Generate QR", command=self._on_generate)
        self.generate_btn.pack(side="left")

        self.save_btn = ttk.Button(actions, text="Save PNG…", command=self._on_save)
        self.save_btn.pack(side="left", padx=(10, 0))

        self.reset_btn = ttk.Button(actions, text="Reset", command=self._reset)
        self.reset_btn.pack(side="left", padx=(10, 0))

        self.quit_btn = ttk.Button(actions, text="Quit", command=self.destroy)
        self.quit_btn.pack(side="left", padx=(10, 0))

        result = ttk.LabelFrame(outer, text="Result", padding=10)
        result.pack(fill="both", expand=True, pady=(14, 0))

        self.value_label = ttk.Label(result, text="Encoded value will appear here.")
        self.value_label.pack(anchor="w")

        self.qr_label = ttk.Label(result)
        self.qr_label.pack(pady=(12, 0))

    def _wire_events(self) -> None:
        self.mode.trace_add("write", lambda *_: self._on_mode_change())
        self.email_var.trace_add("write", lambda *_: self._sync_buttons())
        self.url_var.trace_add("write", lambda *_: self._sync_buttons())

        # Body text doesn't have a StringVar; listen for changes.
        self.body_text.bind("<KeyRelease>", lambda _e: self._sync_buttons())

    def _on_mode_change(self) -> None:
        # Requirement: toggling URL/E-mail should clear the QR + fields.
        if self._is_resetting:
            return
        self._reset()
        self._sync_mode()
        self._sync_buttons()

    def _sync_mode(self) -> None:
        is_email = self.mode.get() == "email"

        if is_email:
            self.url_frame.pack_forget()
            self.email_frame.pack(fill="x", pady=(12, 0))
            self.email_entry.focus_set()
        else:
            self.email_frame.pack_forget()
            self.url_frame.pack(fill="x", pady=(12, 0))
            self.url_entry.focus_set()

    def _sync_buttons(self) -> None:
        if self.mode.get() == "email":
            self.generate_btn.state(["!disabled"] if self.email_var.get().strip() else ["disabled"])
        else:
            self.generate_btn.state(["!disabled"] if self.url_var.get().strip() else ["disabled"])

        self.save_btn.state(["!disabled"] if self._qr_image is not None else ["disabled"])

    def _on_generate(self) -> None:
        mode = self.mode.get()
        value: str | None = None

        if mode == "url":
            url = self.url_var.get().strip()
            if not url:
                messagebox.showerror(APP_TITLE, "URL is required.")
                return
            value = url
        else:
            email = self.email_var.get().strip()
            subject = self.subject_var.get().strip() or None
            body = self.body_text.get("1.0", "end").strip() or None

            if not email:
                messagebox.showerror(APP_TITLE, "E-mail address is required.")
                return
            if not _EMAIL_RE.match(email):
                messagebox.showerror(APP_TITLE, "Please enter a valid e-mail address.")
                return
            value = _mailto_uri(email=email, subject=subject, body=body)

        img = _make_qr_image(value)
        self._qr_image = img

        # Resize for display (keep it crisp-ish)
        img = img.resize((320, 320), resample=Image.NEAREST)

        self._qr_photo = ImageTk.PhotoImage(img)
        self.qr_label.configure(image=self._qr_photo)
        self.value_label.configure(text=value)
        self._sync_buttons()

    def _reset(self) -> None:
        # Clear fields + QR preview/value, keep current mode selected.
        self._is_resetting = True
        try:
            self.url_var.set("")
            self.email_var.set("")
            self.subject_var.set("")
            self.body_text.delete("1.0", "end")

            self._qr_image = None
            self._qr_photo = None
            self.qr_label.configure(image="")
            self.value_label.configure(text="Encoded value will appear here.")
        finally:
            self._is_resetting = False
        self._sync_buttons()

    def _on_save(self) -> None:
        if self._qr_image is None:
            return

        path = filedialog.asksaveasfilename(
            title="Save QR Code",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile="qr.png",
        )
        if not path:
            return

        try:
            self._qr_image.save(path, format="PNG")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to save PNG:\n{e}")
            return

        messagebox.showinfo(APP_TITLE, "Saved.")


def main() -> None:
    # Tk themed widgets look better on macOS.
    app = QrApp()
    app.mainloop()


if __name__ == "__main__":
    main()




