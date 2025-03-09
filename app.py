from flask import Flask, request, jsonify
from milliyet_archive import MilliyetArchiveDownloader
import os
import base64

app = Flask(__name__)

# Configure for Render.com
if os.environ.get('RENDER'):
    # Configure for production
    pass

@app.route('/api/search', methods=['POST'])
def search_newspapers():
    data = request.get_json()
    date_str = data.get('date')
    
    if not date_str:
        return jsonify({"error": "Date is required in YYYY.MM.DD format"}), 400
    
    downloader = MilliyetArchiveDownloader()
    newspapers = downloader.get_newspaper_info(date_str)
    
    return jsonify({
        "date": date_str,
        "newspapers": [{"id": id, "name": name} for id, name in newspapers]
    })

@app.route('/api/download', methods=['POST'])
def download_newspaper():
    data = request.get_json()
    date_str = data.get('date')
    virtual_copy_id = data.get('id')
    broadcast_name = data.get('name')
    
    if not all([date_str, virtual_copy_id, broadcast_name]):
        return jsonify({"error": "Date, ID and name are required"}), 400
    
    downloader = MilliyetArchiveDownloader()
    pdf_path = downloader.download_newspaper(virtual_copy_id, broadcast_name, date_str)
    
    if pdf_path:
        # Read the PDF and encode as base64
        with open(pdf_path, 'rb') as pdf_file:
            encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        
        return jsonify({
            "success": True,
            "filename": pdf_path.name,
            "pdf_data": encoded_pdf
        })
    else:
        return jsonify({"error": "Failed to download newspaper"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)