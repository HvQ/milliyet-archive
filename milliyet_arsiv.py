import requests
import re
import os
import img2pdf
import datetime
import concurrent.futures
import logging
import sys
from pathlib import Path
from tqdm import tqdm

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # For older Python versions
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class MilliyetArchiveDownloader:
    def __init__(self):
        self.base_url = "https://gazetearsivi.milliyet.com.tr"
        self.api_url = "https://gazetearsivi-api.milliyet.com.tr/api/v1"
        self.headers = {
            'authority': 'gazetearsivi.milliyet.com.tr',
            'accept': '*/*',
            'accept-language': 'de-DE,de;q=0.9,tr-TR;q=0.8,tr;q=0.7,en-US;q=0.6,en;q=0.5',
            'cookie': '.DM.SharedCookie={"access_token":"AE653A5343D05242AB352379D55536D0DB81D4AAD00E4F566435C6F3DAD7FB32","expires_in":31536000,"token_type":"Bearer","scope":"api1 offline_access openid profile"}',
            'dnt': '1',
            'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
            'next-url': '/',
            'referer': 'https://gazetearsivi.milliyet.com.tr/',
            'rsc': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.access_token = self.headers['cookie'].split('access_token":"')[1].split('"')[0]
        self.image_headers = {'Authorization': self.access_token}
        
        self.images_dir = Path('images')
        self.pdfs_dir = Path('pdfs')
        self.images_dir.mkdir(exist_ok=True)
        self.pdfs_dir.mkdir(exist_ok=True)

    def validate_date(self, date_str):
        """Validate the date format."""
        try:
            return datetime.datetime.strptime(date_str, '%Y.%m.%d')
        except ValueError:
            logger.error("Invalid date format. Please use YYYY.MM.DD format.")
            return None

    def sanitize_filename(self, filename):
        """Sanitize filename to remove illegal characters."""
        # Replace any characters that might cause issues in filenames
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        return filename

    def get_newspaper_info(self, date_str):
        """Get newspaper information for a specific date."""
        url = f"{self.base_url}/liste?tarih={date_str}"
        logger.info(f"Getting newspaper list for date: {date_str}")
        
        response = requests.get(url, headers=self.headers)
        response.encoding = 'utf-8'  # Ensure UTF-8 encoding
        
        if response.status_code != 200:
            logger.error(f"Failed to get newspaper list: Status code {response.status_code}")
            return []

        virtual_copy_ids = re.findall(r'"virtualCopyId"\s*:\s*"([^"]*)"', response.text)
        broadcast_names = re.findall(r'"broadcastName"\s*:\s*"([^"]*)"', response.text)
        
        # Fix encoding if needed
        broadcast_names = [name.encode('latin1').decode('utf-8') if '%' in name else name for name in broadcast_names]
        
        if not virtual_copy_ids:
            logger.warning(f"No newspapers found for date {date_str}")
            return []
        
        logger.info(f"Found {len(virtual_copy_ids)} newspapers")
        return list(zip(virtual_copy_ids, broadcast_names))

    def download_page(self, image_url, page_no):
        """Download a single newspaper page."""
        try:
            response = requests.get(image_url, headers=self.image_headers)
            if response.status_code == 200:
                file_path = self.images_dir / f"page_{page_no}.jpg"
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return file_path
            else:
                logger.error(f"Failed to download page {page_no}: Status code {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error downloading page {page_no}: {e}")
            return None

    def download_newspaper(self, virtual_copy_id, broadcast_name, date_str):
        """Download all pages of a newspaper and create PDF."""
        logger.info(f"Processing: {broadcast_name} (ID: {virtual_copy_id})")
        
        # Clear any existing images from previous runs
        for file in self.images_dir.glob("*.jpg"):
            file.unlink()
        
        # Get newspaper pages
        url = f"{self.api_url}/Newspaper/GetNewspaperPages/{virtual_copy_id}"
        response = requests.get(url, headers=self.headers)
        response.encoding = 'utf-8'  # Ensure UTF-8 encoding
        
        if response.status_code != 200:
            logger.error(f"Failed to get newspaper pages: Status code {response.status_code}")
            return None
        
        response_json = response.json()
        if response_json.get('hasError'):
            logger.error(f"API returned error: {response_json.get('message', 'Unknown error')}")
            return None
        
        pages = response_json['result']['virtualPages']
        logger.info(f"Downloading {len(pages)} pages for {broadcast_name}")
        
        # Download pages in parallel
        successful_downloads = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Create a dictionary to keep track of futures and their page numbers
            future_to_page = {}
            
            for page in pages:
                image_url = f"{self.api_url}/NewspaperImage{page['pageFileOrjUrl']}"
                future = executor.submit(self.download_page, image_url, page['pageNo'])
                future_to_page[future] = page['pageNo']
            
            # Process results with a progress bar
            for future in tqdm(concurrent.futures.as_completed(future_to_page), total=len(pages), desc="Downloading pages"):
                page_no = future_to_page[future]
                try:
                    file_path = future.result()
                    if file_path:
                        successful_downloads.append((page_no, file_path))
                except Exception as e:
                    logger.error(f"Error processing download for page {page_no}: {e}")
        
        # Create PDF if we have any successful downloads
        if successful_downloads:
            # Sort by page number
            successful_downloads.sort(key=lambda x: x[0])
            
            # Sanitize the broadcast name for the filename
            safe_name = self.sanitize_filename(broadcast_name)
            pdf_path = self.pdfs_dir / f"{safe_name}_{date_str}.pdf"
            logger.info(f"Creating PDF: {pdf_path}")
            
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert([str(path) for _, path in successful_downloads]))
            
            logger.info(f"PDF successfully created: {pdf_path}")
            return pdf_path
        else:
            logger.error("No pages were downloaded successfully. Cannot create PDF.")
            return None

    def process_date(self, date_str):
        """Process all newspapers for a specific date."""
        if not self.validate_date(date_str):
            return []
        
        newspapers = self.get_newspaper_info(date_str)
        if not newspapers:
            logger.warning(f"No newspapers found for date {date_str}")
            return []
        
        results = []
        for virtual_copy_id, broadcast_name in newspapers:
            pdf_path = self.download_newspaper(virtual_copy_id, broadcast_name, date_str)
            if pdf_path:
                results.append((broadcast_name, date_str, pdf_path))
        
        return results


def main():
    date_input = input("Gazete tarihini YYYY.MM.DD formatinda gir: ")
    
    downloader = MilliyetArchiveDownloader()
    results = downloader.process_date(date_input)
    
    if results:
        logger.info("Download summary:")
        for broadcast_name, date_str, pdf_path in results:
            logger.info(f"• {broadcast_name} ({date_str}): {pdf_path}")
    else:
        logger.warning("No newspapers were downloaded successfully")
        logger.info("Note: Try a different date if the archive doesn't have newspapers for this period.")


if __name__ == '__main__':
    main()
