# Milliyet Archive Application

This project provides a web application for searching and downloading newspapers from the Milliyet newspaper archive.

## Project Structure

- `milliyet_archive.py` - Core functionality for interacting with the Milliyet archive
- `app.py` - Flask API for serving the backend
- `frontend/` - SvelteKit frontend application

## Backend Setup

1.  Install dependencies:

    pip install -r requirements.txt

2.  Run the Flask development server:

    python app.py

## Frontend Setup

1.  Navigate to the frontend directory:

    cd frontend

2.  Install dependencies:

    npm install

3.  Run the development server:

    npm run dev

## Deployment

### Backend (Render.com)

1.  Connect your GitHub repository to Render.com
2.  Create a new Web Service
3.  Select the Python environment
4.  Use the settings defined in `render.yaml`

### Frontend (Vercel/Netlify)

1.  Build the frontend for production:

    cd frontend
    npm run build

2.  Deploy the `frontend/build` directory to your preferred static hosting provider

## Configuration

The application uses environment variables for configuration:

-   `PORT` - Port to run the server on (default: 5000)
-   `RENDER` - Set by Render.com in production

## API Endpoints

-   `POST /api/search` - Search for newspapers by date
-   `POST /api/download` - Download a specific newspaper
-   `GET /health` - Health check endpoint
