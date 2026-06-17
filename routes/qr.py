import qrcode
import io
from flask import Blueprint, send_file, render_template
from flask_login import login_required, current_user
from functools import wraps
from flask import abort

qr_bp = Blueprint('qr', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Generate QR code image for a table ──
@qr_bp.route('/qr/<int:table_number>')
def generate_qr(table_number):
    # URL the QR code will open when scanned
    url = f'http://127.0.0.1:5000/login?table={table_number}'

    # Generate QR code
    qr = qrcode.QRCode(
        version        = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size       = 10,
        border         = 4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='#c9a84c', back_color='#0d0d0d')

    # Send as PNG image
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png',
                     download_name=f'table_{table_number}_qr.png')


# ── QR Codes page — shows all tables ──
@qr_bp.route('/admin/qr-codes')
@login_required
@admin_required
def qr_codes():
    return render_template('admin/qr_codes.html')