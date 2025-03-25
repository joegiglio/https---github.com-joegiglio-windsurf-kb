# Knowledge Base Application

A modern, responsive knowledge base application built with Flask and Bootstrap. Features include article management, category organization, and an admin interface for content management.

## Features

- 📚 Article Management: Create, edit, and organize articles
- 🗂️ Category System: Organize content with categories
- 🔒 Admin Interface: Secure admin panel for content management
- 📱 Responsive Design: Works on desktop, tablet, and mobile
- 🔍 Search Functionality: Search through articles
- 📊 Analytics Dashboard: Track views and user engagement

## Technical Requirements

- Python 3.12+
- Flask
- SQLAlchemy
- Bootstrap 5.3
- jQuery 3.7+
- Playwright (for testing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/joegiglio/windsurf-vide-coding-kb
cd kb1
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Database Initialization

1. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

2. Create an admin user:
```bash
flask create-admin --username admin --password admin123
```

## Running the Application

1. Start the development server:
```bash
flask run
```

2. Access the application:
- Main site: http://localhost:5000
- Admin panel: http://localhost:5000/admin

## Running Tests

### Setup Playwright

1. Install Playwright browsers:
```bash
playwright install
```

### Running E2E Tests

1. Run all tests:
```bash
pytest tests/
```

2. Run specific test file:
```bash
pytest tests/test_e2e.py
```

3. Run specific test:
```bash
pytest tests/test_e2e.py::test_category_creation
```

### Test Configuration

- Tests use a separate SQLite database
- Admin credentials for tests:
  - Username: admin
  - Password: admin123

## Project Structure

```
knowledge-base/
├── README.md           # Project documentation
├── admin.py           # Admin related functionality
├── app.py            # Application entry point
├── changes.log       # Change log file
├── extensions.py     # Flask extensions
├── hello.py         # Hello world example
├── init_db.py       # Database initialization
├── migrations/      # Database migrations
│   ├── README
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── models.py        # Database models
├── pytest.ini      # Pytest configuration
├── requirements.txt # Project dependencies
├── static/         # Static files
│   ├── css/        # Stylesheets
│   │   ├── admin.css
│   │   ├── article.css
│   │   └── style.css
│   └── js/         # JavaScript files
│       ├── admin/
│       │   ├── articles.js
│       │   ├── categories.js
│       │   ├── dashboard.js
│       │   ├── login.js
│       │   ├── search_report.js
│       │   └── utils.js
│       ├── admin.js
│       ├── article.js
│       └── main.js
├── templates/      # HTML templates
│   ├── admin/     # Admin templates
│   │   ├── articles.html
│   │   ├── base.html
│   │   ├── categories.html
│   │   ├── index.html
│   │   ├── login.html
│   │   └── search_report.html
│   ├── article.html
│   ├── base.html
│   ├── category.html
│   └── index.html
└── tests/         # Test files
    ├── __init__.py
    ├── conftest.py
    ├── create_test_image.py
    └── test_e2e.py
```

## Security Features

- Input sanitization on both client and server side
- Password hashing using industry standards
- CSRF protection
- Field length and data type validation
- Secure session management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This license allows you to use, copy, modify, merge, publish, or distribute copies of this software.
Users may not use any part of this software in commercial projects.
The authors of this software are not liable for any damages or losses resulting from the use of this software.  It is being shared for educational purposes only.

## Acknowledgments

- Joe Giglio (original author) [LinkedIn Profile](https://www.linkedin.com/in/joegiglio/)
- Codeium Windsurf [Website](https://codeium.com/windsurf)
- Anthropic Claude 3.5 Sonnet [Website](https://www.anthropic.com/claude)