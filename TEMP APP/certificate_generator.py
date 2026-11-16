"""
certificate_generator.py
Handles certificate database storage, verification lookups, QR code generation,
and high-resolution certificate rendering with Pillow.
"""

import os
import io
import uuid
import sqlite3
import datetime
import socket
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_H

# Default DB Path
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certificates.db")


def get_local_ip() -> str:
    """Detect the local LAN IP address of the machine for network QR scanning."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Does not actually connect, just identifies routing interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initialize the SQLite database schema and insert demo certificates if empty."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            email TEXT,
            issue_date TEXT NOT NULL,
            grade TEXT,
            issuer TEXT NOT NULL,
            qr_data TEXT NOT NULL,
            status TEXT DEFAULT 'VERIFIED',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()

    # Check if empty, add sample certificate
    cursor.execute("SELECT COUNT(*) FROM certificates")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_id = "1STOP-2026-DEMO01"
        sample_url = f"http://localhost:8501/?cert_id={sample_id}"
        cursor.execute("""
            INSERT INTO certificates (
                id, name, course, email, issue_date, grade, issuer, qr_data, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sample_id,
            "Demo Student",
            "Full Stack Web Development & AI",
            "demo.student@onestoptech.org",
            datetime.date.today().strftime("%B %d, %Y"),
            "Grade A+ (Distinction)",
            "1stop Keep Growing",
            sample_url,
            "VERIFIED",
            datetime.datetime.now().isoformat()
        ))
        conn.commit()

    conn.close()


def generate_unique_cert_id(prefix: str = "1STOP") -> str:
    """Generate a clean, professional, unique certificate verification ID."""
    current_year = datetime.datetime.now().year
    random_part = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{current_year}-{random_part}"


def add_certificate(
    name: str,
    course: str,
    email: str = "",
    issue_date: Optional[str] = None,
    grade: str = "Completed with Distinction",
    issuer: str = "1stop Keep Growing",
    base_url: str = "http://localhost:8501",
    custom_id: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Create and persist a new certificate record in the database."""
    init_db(db_path)

    cert_id = custom_id.strip() if custom_id and custom_id.strip() else generate_unique_cert_id()
    if not issue_date:
        issue_date = datetime.date.today().strftime("%B %d, %Y")

    # Clean base url
    clean_base = base_url.rstrip("/")
    qr_data = f"{clean_base}/?cert_id={cert_id}"
    created_at = datetime.datetime.now().isoformat()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO certificates (
            id, name, course, email, issue_date, grade, issuer, qr_data, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cert_id,
        name.strip(),
        course.strip(),
        email.strip().lower() if email else "",
        issue_date,
        grade.strip() if grade else "Completed",
        issuer.strip(),
        qr_data,
        "VERIFIED",
        created_at
    ))
    conn.commit()
    conn.close()

    return {
        "id": cert_id,
        "name": name.strip(),
        "course": course.strip(),
        "email": email.strip().lower() if email else "",
        "issue_date": issue_date,
        "grade": grade.strip() if grade else "Completed",
        "issuer": issuer.strip(),
        "qr_data": qr_data,
        "status": "VERIFIED",
        "created_at": created_at
    }


def get_certificate_by_id(cert_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Lookup certificate by its exact ID."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM certificates WHERE id = ?", (cert_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def search_certificates(query_str: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Search certificates by ID, email address, or student name."""
    init_db(db_path)
    query = query_str.strip().lower()
    if not query:
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM certificates 
        WHERE LOWER(id) = ? 
           OR LOWER(email) = ? 
           OR LOWER(name) LIKE ? 
           OR LOWER(course) LIKE ?
        ORDER BY created_at DESC
    """, (query, query, f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_certificates(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve all certificates from the database."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM certificates ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def generate_qr_code(
    data: str,
    box_size: int = 10,
    border: int = 2,
    fill_color: str = "#0b2e59",
    back_color: str = "#ffffff"
) -> Image.Image:
    """Generate a high-res PIL Image of the verification QR code."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
    return img


def get_image_bytes(img: Image.Image, format: str = "PNG") -> bytes:
    """Convert PIL image to bytes."""
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def _get_font(font_name: str, size: int) -> ImageFont.ImageFont:
    """Helper to load a system TTF font with fallback to default PIL font."""
    font_paths = [
        os.path.join(r"C:\Windows\Fonts", font_name),
        os.path.join(r"C:\Windows\Fonts", font_name.lower()),
        os.path.join(r"C:\Windows\Fonts", "arial.ttf"),
        os.path.join(r"C:\Windows\Fonts", "times.ttf"),
        os.path.join(r"C:\Windows\Fonts", "georgia.ttf"),
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_certificate_image(cert_data: Dict[str, Any]) -> Image.Image:
    """
    Renders an official, high-resolution certificate image (1600 x 1130 px)
    matching 1stop branding with embedded QR code, gold/navy borders, and seals.
    """
    width, height = 1600, 1130
    # Background: crisp ivory/parchment
    bg_color = (253, 252, 248)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Palette
    navy = (14, 47, 86)          # Primary Deep Blue #0E2F56
    bright_blue = (0, 122, 255)   # #007AFF
    gold = (212, 175, 55)        # Metallic Gold
    orange = (245, 130, 32)      # 1stop Orange #F58220
    dark_gray = (55, 65, 81)     # Charcoal text
    light_gray = (156, 163, 175)

    # 1. Outer Ornate Double Border
    margin = 40
    # Outer navy rectangle
    draw.rectangle(
        [(margin, margin), (width - margin, height - margin)],
        outline=navy,
        width=6
    )
    # Inner gold border
    inner_margin = 52
    draw.rectangle(
        [(inner_margin, inner_margin), (width - inner_margin, height - inner_margin)],
        outline=gold,
        width=3
    )
    # Thin secondary line
    thin_margin = 60
    draw.rectangle(
        [(thin_margin, thin_margin), (width - thin_margin, height - thin_margin)],
        outline=(230, 230, 230),
        width=1
    )

    # Corner Corner Accents (Decorative corner squares)
    corner_size = 28
    corners = [
        (inner_margin, inner_margin),
        (width - inner_margin - corner_size, inner_margin),
        (inner_margin, height - inner_margin - corner_size),
        (width - inner_margin - corner_size, height - inner_margin - corner_size)
    ]
    for cx, cy in corners:
        draw.rectangle([(cx, cy), (cx + corner_size, cy + corner_size)], fill=navy, outline=gold, width=2)

    # 2. Top Header Branding: 1stop Keep Growing
    # Hexagon / Badge representation for 1stop logo
    logo_center_x = width // 2
    logo_y = 100

    font_brand = _get_font("georgia.ttf", 36)
    font_slogan = _get_font("arial.ttf", 15)

    # Draw Brand Title: "1stop" with "Keep Growing"
    brand_text = "1stop"
    slogan_text = "KEEP GROWING"
    
    # Orange "1" icon box
    box_w, box_h = 36, 42
    bx0, by0 = logo_center_x - 110, logo_y - 28
    draw.rounded_rectangle([(bx0, by0), (bx0 + box_w, by0 + box_h)], radius=6, fill=orange)
    draw.text((bx0 + 12, by0 + 8), "1", fill=(255, 255, 255), font=_get_font("arialbd.ttf", 24))

    draw.text((bx0 + 46, by0 + 2), brand_text, fill=navy, font=_get_font("arialbd.ttf", 34))
    draw.text((bx0 + 48, by0 + 38), slogan_text, fill=navy, font=font_slogan)

    # Orange accent curve / pill below brand
    accent_w, accent_h = 140, 6
    draw.rounded_rectangle(
        [(logo_center_x - accent_w // 2, logo_y + 40), (logo_center_x + accent_w // 2, logo_y + 40 + accent_h)],
        radius=3,
        fill=orange
    )

    # 3. Certificate Title
    font_title = _get_font("timesbd.ttf", 44)
    title_text = "CERTIFICATE OF COMPLETION"
    draw.text((logo_center_x, 210), title_text, fill=navy, font=font_title, anchor="mm")

    # Subtitle
    font_sub = _get_font("georgia.ttf", 19)
    draw.text((logo_center_x, 260), "THIS IS PROUDLY PRESENTED TO", fill=gold, font=font_sub, anchor="mm")

    # 4. Student Name (Large Serif)
    font_name = _get_font("georgia.ttf", 52)
    student_name = cert_data.get("name", "Student Name").upper()
    draw.text((logo_center_x, 340), student_name, fill=navy, font=font_name, anchor="mm")

    # Underline under student name
    name_line_w = 560
    draw.line(
        [(logo_center_x - name_line_w // 2, 385), (logo_center_x + name_line_w // 2, 385)],
        fill=gold,
        width=2
    )

    # 5. Presentation Text & Course Name
    font_body = _get_font("georgia.ttf", 20)
    body_text = "for successfully completing the prescribed industry certification program in"
    draw.text((logo_center_x, 435), body_text, fill=dark_gray, font=font_body, anchor="mm")

    # Course Name
    font_course = _get_font("arialbd.ttf", 36)
    course_name = cert_data.get("course", "Course Name")
    draw.text((logo_center_x, 495), course_name, fill=navy, font=font_course, anchor="mm")

    # Grade / Distinction if any
    grade_text = cert_data.get("grade", "")
    if grade_text:
        font_grade = _get_font("georgia.ttf", 18)
        draw.text((logo_center_x, 545), f"Demonstrating Excellence — {grade_text}", fill=orange, font=font_grade, anchor="mm")

    # Verification summary line
    cert_id = cert_data.get("id", "1STOP-CERT")
    issue_date = cert_data.get("issue_date", "")
    font_meta = _get_font("arial.ttf", 16)
    meta_text = f"Certificate Verification ID: {cert_id}   |   Issued on: {issue_date}   |   Status: Authenticated & Verified"
    draw.text((logo_center_x, 610), meta_text, fill=dark_gray, font=font_meta, anchor="mm")

    # 6. Bottom Section: Signatures, Seal & QR Code
    bottom_y = 920

    # (A) Left: Director Signature Line
    sig_line_len = 220
    sig_left_x = 260
    draw.line([(sig_left_x - sig_line_len // 2, bottom_y - 20), (sig_left_x + sig_line_len // 2, bottom_y - 20)], fill=dark_gray, width=2)
    # Simulated signature calligraphy
    font_sig = _get_font("georgia.ttf", 26)
    draw.text((sig_left_x, bottom_y - 50), "Aditya Sharma", fill=navy, font=font_sig, anchor="mm")
    draw.text((sig_left_x, bottom_y + 5), "Academic Director", fill=navy, font=_get_font("arialbd.ttf", 16), anchor="mm")
    draw.text((sig_left_x, bottom_y + 28), "1stop Education Platform", fill=light_gray, font=_get_font("arial.ttf", 14), anchor="mm")

    # (B) Center: Golden Authenticated Stamp / Seal
    seal_x = width // 2
    seal_y = bottom_y - 10
    seal_radius = 65
    draw.ellipse(
        [(seal_x - seal_radius, seal_y - seal_radius), (seal_x + seal_radius, seal_y + seal_radius)],
        outline=gold,
        width=4,
        fill=(254, 250, 240)
    )
    draw.ellipse(
        [(seal_x - seal_radius + 6, seal_y - seal_radius + 6), (seal_x + seal_radius - 6, seal_y + seal_radius - 6)],
        outline=orange,
        width=1
    )
    draw.text((seal_x, seal_y - 24), "★ ★ ★", fill=gold, font=_get_font("arial.ttf", 16), anchor="mm")
    draw.text((seal_x, seal_y - 4), "OFFICIALLY", fill=navy, font=_get_font("arialbd.ttf", 13), anchor="mm")
    draw.text((seal_x, seal_y + 12), "VERIFIED", fill=orange, font=_get_font("arialbd.ttf", 14), anchor="mm")
    draw.text((seal_x, seal_y + 28), "1STOP TECH", fill=gold, font=_get_font("arialbd.ttf", 11), anchor="mm")

    # (C) Right: Official Embedded QR Code
    qr_data = cert_data.get("qr_data", f"http://localhost:8501/?cert_id={cert_id}")
    qr_img = generate_qr_code(qr_data, box_size=5, border=2, fill_color="#0E2F56")
    qr_size = 140
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    qr_pos_x = width - 360
    qr_pos_y = bottom_y - 95
    img.paste(qr_img, (qr_pos_x, qr_pos_y))
    # Border around QR
    draw.rectangle(
        [(qr_pos_x - 4, qr_pos_y - 4), (qr_pos_x + qr_size + 4, qr_pos_y + qr_size + 4)],
        outline=gold,
        width=2
    )
    # Caption under QR
    draw.text(
        (qr_pos_x + qr_size // 2, qr_pos_y + qr_size + 18),
        "Scan to Verify Online",
        fill=navy,
        font=_get_font("arialbd.ttf", 13),
        anchor="mm"
    )
    draw.text(
        (qr_pos_x + qr_size // 2, qr_pos_y + qr_size + 34),
        cert_id,
        fill=orange,
        font=_get_font("arial.ttf", 12),
        anchor="mm"
    )

    return img
