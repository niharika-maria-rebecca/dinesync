
import qrcode
import os

# Create folder for QR images
os.makedirs('static/qr', exist_ok=True)

for i in range(1, 11):
    url = f'http://172.20.10.9:5000/login?table={i}'

    qr = qrcode.QRCode(
        version          = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size         = 10,
        border           = 4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    img.save(f'static/qr/table_{i}.png')
    print(f'✅ QR generated for Table {i}')

print('\n🎉 All 10 QR codes saved in static/qr/ folder!')