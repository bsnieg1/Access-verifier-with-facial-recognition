import qrcode
from pathlib import Path

QR_DIR = Path("data/qr_codes")


def generate_qr(data: str, user_id: int):

    QR_DIR.mkdir(parents=True, exist_ok=True)

    filename: str = f"user_{user_id}.png"
    output_path = QR_DIR / filename

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)

    print(f"QR zapisany do: {output_path}")
    return f"data/qr_codes/user_{user_id}.png"

# def has_qr(user_id: int):

#     qr_path = QR_DIR / f"user_{user_id}.png"
#     return qr_path.exists()

# def get_qr_path(user_id: int):

#     qr_path = QR_DIR / f"user_{user_id}.png"
#     return qr_path if qr_path.exists() else None