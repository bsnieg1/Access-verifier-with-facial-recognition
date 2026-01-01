import qrcode
from pathlib import Path

QR_DIR = Path("data/qr_codes")


def generate_qr(data: str, filename: str = "qr.png"):
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
    return output_path
