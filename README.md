# ImageFeed Protocol

ImageFeed Protocolis a lightweight image subscription service that allows users to create and share image collections through one-time subscription links.

## Features

### MVP (Current)
- Create image feeds with unique access tokens
- Upload and manage images in feeds
- Access feeds via one-time subscription links
- Basic image preview and metadata support

### Planned
- Image optimization and thumbnails
- Access control and permissions
- Content moderation
- Analytics and usage tracking

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis (optional, for caching)

### Installation

1. Clone the repository
```bash
git clone https://github.com/Brandon-c-tech/ImageFeed_Protocol.git
cd imagefeed
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database
```bash
alembic upgrade head
```

6. Run the development server
```bash
uvicorn app.main:app --reload
```

## Basic Usage

### Creating a Feed
```bash
curl -X POST "http://localhost:8000/api/v1/feeds" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Photos", "description": "My personal photo collection"}'
```

### Uploading an Image
```bash
curl -X POST "http://localhost:8000/api/v1/feeds/{feed_id}/images" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@photo.jpg"
```

### Accessing a Feed
```
http://localhost:8000/api/v1/feeds/{feed_id}?token={access_token}
```

## API Documentation

After starting the server, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure
```
imagefeed/
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration
│   ├── models.py        # Database models
│   └── api/             # API endpoints
├── alembic/             # Database migrations
└── tests/               # Test cases
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
