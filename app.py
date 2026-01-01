from flask import Flask, render_template, request, jsonify, send_file
import qrcode
import io
import base64
from PIL import Image

app = Flask(__name__)

# Store saved QR codes in memory (in production, use a database)
saved_qr_codes = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get('url', '')
    qr_id = data.get('id', None)
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Save to memory if id provided
    if qr_id:
        saved_qr_codes[qr_id] = {'url': url, 'image': img_base64}
    else:
        # Generate new id
        qr_id = str(len(saved_qr_codes) + 1)
        saved_qr_codes[qr_id] = {'url': url, 'image': img_base64}
    
    return jsonify({
        'success': True,
        'image': f'data:image/png;base64,{img_base64}',
        'id': qr_id,
        'url': url
    })

@app.route('/saved', methods=['GET'])
def get_saved():
    result = []
    for qr_id, data in saved_qr_codes.items():
        result.append({
            'id': qr_id,
            'url': data['url'],
            'image': f"data:image/png;base64,{data['image']}"
        })
    return jsonify(result)

@app.route('/delete/<qr_id>', methods=['DELETE'])
def delete_qr(qr_id):
    if qr_id in saved_qr_codes:
        del saved_qr_codes[qr_id]
        return jsonify({'success': True})
    return jsonify({'error': 'QR code not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
