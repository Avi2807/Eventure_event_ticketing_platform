import qrcode
import io
import base64
from PIL import Image

def generate_qr_code(data):
    """Generate QR code for ticket"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 string
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

def generate_ticket_qr_code(ticket_number, ticket_id):
    """Generate QR code for a specific ticket"""
    data = f"TICKET:{ticket_number}:{ticket_id}"
    return generate_qr_code(data)

