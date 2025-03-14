# Hauts de Seine Backend

Hauts de Seine Backend is a FastAPI-based project designed for efficient and scalable API development. It includes database integration, testing, and containerized deployment options using Podman or Docker.

## Prerequisites

- **Python**: Version ≤ 3.12
- **Podman** or **Docker** for containerized deployment
- **PostgreSQL** (if using a local database)

## Local Development Installation

1. **Start the development database**
   ```sh
   podman compose up -d
   ```

2. **Create a Python virtual environment**
   ```sh
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   ```sh
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

## Running the Application

To run the application locally:
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Access the API at: [http://localhost:8000](http://localhost:8000)

## Building for Staging or Production with Podman/Docker

### Build and Run the Image
```sh
podman build -t pcc:latest .
podman run --name pcc-prod -p 80:80 \
  -e POSTGRES_USER=xxxxxx \
  -e POSTGRES_PASSWORD=xxxxxx \
  -e POSTGRES_DB=xxxxxxx \
  -e POSTGRES_HOST=xxxxxx \
  -e POSTGRES_PORT=xxxxx \
  --replace pcc:latest
```

For Docker, replace `podman` with `docker`.

## Testing

Ensure the database is running, then execute:
```sh
python -m pytest
```

## API Documentation

FastAPI automatically generates interactive documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Environment Variables

The application relies on environment variables. Create a `.env` file with the following:
```ini
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
POSTGRES_HOST=your_db_host
POSTGRES_PORT=your_db_port
```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License.

