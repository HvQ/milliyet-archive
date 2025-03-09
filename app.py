from flask import Flask, request, jsonify
from flask_cors import CORS
from milliyet_archive import MilliyetArchiveDownloader
import os
import base64

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Configure for Render.com
if os.environ.get('RENDER'):
    # Configure for production
    pass

@app.route('/api/search', methods=['POST'])
def search_newspapers():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        date_str = data.get('date')
        
        if not date_str:
            return jsonify({"error": "Date is required in YYYY.MM.DD format"}), 400
        
        print(f"Searching for newspapers on date: {date_str}")
        downloader = MilliyetArchiveDownloader()
        newspapers = downloader.get_newspaper_info(date_str)
        
        print(f"Found {len(newspapers)} newspapers")
        
        return jsonify({
            "date": date_str,
            "newspapers": [{"id": id, "name": name} for id, name in newspapers]
        })
    except Exception as e:
        print(f"Error in search_newspapers: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/download', methods=['POST'])
def download_newspaper():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        date_str = data.get('date')
        virtual_copy_id = data.get('id')
        broadcast_name = data.get('name')
        
        if not all([date_str, virtual_copy_id, broadcast_name]):
            return jsonify({"error": "Date, ID and name are required"}), 400
        
        print(f"Downloading newspaper: {broadcast_name} for date {date_str}")
        downloader = MilliyetArchiveDownloader()
        pdf_path = downloader.download_newspaper(virtual_copy_id, broadcast_name, date_str)
        
        if pdf_path:
            print(f"Successfully downloaded PDF to {pdf_path}")
            # Read the PDF and encode as base64
            with open(pdf_path, 'rb') as pdf_file:
                encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
            
            return jsonify({
                "success": True,
                "filename": pdf_path.name,
                "pdf_data": encoded_pdf
            })
        else:
            print(f"Failed to download newspaper {broadcast_name}")
            return jsonify({"error": "Failed to download newspaper"}), 500
    except Exception as e:
        print(f"Error in download_newspaper: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})
    
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Milliyet Archive API is running",
        "endpoints": [
            {"path": "/api/search", "method": "POST", "description": "Search for newspapers by date"},
            {"path": "/api/download", "method": "POST", "description": "Download a newspaper"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/test-search/<date>", "method": "GET", "description": "Test search by date (GET method)"}
        ]
    })
    
@app.route('/test-search/<date>', methods=['GET'])
def test_search(date):
    """Test endpoint for direct GET requests to search newspapers."""
    try:
        print(f"Testing search for newspapers on date: {date}")
        downloader = MilliyetArchiveDownloader()
        newspapers = downloader.get_newspaper_info(date)
        
        print(f"Found {len(newspapers)} newspapers")
        
        return jsonify({
            "date": date,
            "newspapers": [{"id": id, "name": name} for id, name in newspapers]
        })
    except Exception as e:
        print(f"Error in test_search: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)