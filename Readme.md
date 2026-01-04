# CPE Training Tracker

A lightweight web application for tracking Continuing Professional Education (CPE) hours. Built with Flask and SQLite, designed for personal homeserver deployment.

## Features

- 👤 User authentication (registration and login)
- ➕ Add training records with name, hours, and optional links
- 📋 View all training records in a sortable table
- ✏️ Edit existing records
- 🗑️ Delete records
- 📊 Dashboard with total hours summary
- 📥 Export records to CSV with date range filtering
- 🐳 Fully containerized for easy deployment

## Quick Start

### Using Docker (Recommended)

1. **Clone or download this repository**

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

4. **Create your first account:**
   Click "Register" and create a new user account

### Manual Installation

1. **Install Python 3.11+**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access at:** `http://localhost:5000`

## File Structure

```
cpe-tracker/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container build instructions
├── docker-compose.yml       # Docker Compose configuration
├── templates/               # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_record.html
│   ├── records.html
│   ├── edit_record.html
│   └── export.html
├── static/                  # Static files (currently unused)
├── instance/                # SQLite database location (auto-created)
│   └── cpe_tracker.db
└── data/                    # Docker volume mount point
```

## Configuration

### Environment Variables

Set these in `docker-compose.yml` or your environment:

- `SECRET_KEY`: Flask secret key for session security (change in production!)
- `SQLALCHEMY_DATABASE_URI`: Database connection string (default: SQLite)

### Changing the Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Access on port 8080 instead
```

## Database

The application uses SQLite by default, storing data in `instance/cpe_tracker.db` (or `/app/instance/cpe_tracker.db` in Docker).

### Backup Your Data

**Docker:**
```bash
docker cp cpe-tracker:/app/instance/cpe_tracker.db ./backup.db
```

**Manual:**
```bash
cp instance/cpe_tracker.db backup.db
```

## Usage Guide

### Adding Training Records

1. Log in to your account
2. Click "Add Training" in the navigation
3. Fill in:
   - **Training Name**: Name of the course/training
   - **Hours**: Number of CPE hours (e.g., 1.5)
   - **Link**: Optional URL to training material or certificate
4. Click "Add Record"

### Viewing Records

- **Dashboard**: Shows total hours and 5 most recent records
- **View Records**: Complete list of all training records with edit/delete options

### Exporting to CSV

1. Click "Export" in the navigation
2. Optionally select a date range
3. Click "Download CSV"
4. Open in Excel, Google Sheets, or any spreadsheet application

### Editing/Deleting Records

1. Go to "View Records"
2. Click "Edit" to modify a record
3. Click "Delete" to remove a record (with confirmation)

## Security Considerations

### Production Deployment

1. **Change the SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Update `docker-compose.yml` with the generated key

2. **Use HTTPS:** Deploy behind a reverse proxy (nginx, Caddy, Traefik)

3. **Restrict access:** Use firewall rules or VPN for homeserver access

4. **Regular backups:** Automate database backups

### Password Security

- Passwords are hashed using Werkzeug's security functions
- Never stored in plain text
- Each user's data is isolated

## Troubleshooting

### Container won't start
```bash
docker-compose logs cpe-tracker
```

### Database permission issues
```bash
sudo chown -R 1000:1000 ./data
```

### Reset database
```bash
docker-compose down
rm -rf ./data/cpe_tracker.db
docker-compose up -d --build
```

## Technology Stack

- **Backend**: Flask 3.0
- **Database**: SQLite 3
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Container**: Docker, Docker Compose

## Contributing

This is a personal project, but feel free to fork and customize for your needs!

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues or questions, please refer to the Flask and Docker documentation:
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
