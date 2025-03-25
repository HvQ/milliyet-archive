# Milliyet Archive Application

This project provides a web application for searching and downloading newspapers from the Milliyet newspaper archive.

## Project Structure

- `milliyet_archive.py` - Core functionality for interacting with the Milliyet archive
- `app.py` - Flask API for serving the backend
- `frontend/` - SvelteKit frontend application

## API Endpoints

- `POST /api/search` - Search for newspapers by date
- `POST /api/download` - Download a specific newspaper
- `GET /health` - Health check endpoint
