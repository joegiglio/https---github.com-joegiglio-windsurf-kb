import pytest
from playwright.sync_api import expect, Page
import os
import time
import logging
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def flask_server(app):
    """Start Flask server for testing"""
    def run_app():
        app.run(port=5000)
    
    server = threading.Thread(target=run_app, daemon=True)
    server.start()
    time.sleep(2)  # Give the server time to start
    yield server

@pytest.fixture(autouse=True)
def setup_test(page: Page):
    """Setup and cleanup for each test"""
    # Set a longer timeout for all operations
    page.set_default_timeout(60000)  # 60 seconds
    yield
    try:
        page.close()
    except Exception as e:
        logger.error(f"Error closing page: {e}")

def admin_login(page: Page):
    """Helper function to perform admin login"""
    page.goto("http://localhost:5000/admin/login")
    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "admin123")
    page.click("button[type='submit']")
    # Wait for navigation to complete
    page.wait_for_url("http://localhost:5000/admin/")

@pytest.mark.e2e
def test_admin_login(page: Page, flask_server):
    """Test 1: Admin Login Functionality"""
    logger.info('Running admin login test')
    admin_login(page)
    # Check if we're on the admin page (with or without trailing slash)
    assert page.url.rstrip('/') == "http://localhost:5000/admin"

@pytest.mark.e2e
def test_category_creation(page: Page, flask_server):
    """Test 2: Category Creation and Validation"""
    logger.info('Running category creation test')
    admin_login(page)
    
    page.goto("http://localhost:5000/admin/categories")
    page.fill("input[name='name']", "Test Category")
    page.fill("textarea[name='description']", "Test Description")
    page.click("button:has-text('Add Category')")
    # Wait for the category to appear
    page.wait_for_selector("text=Test Category", state="visible")
    expect(page.locator("text=Test Category")).to_be_visible()

@pytest.mark.e2e
def test_article_creation(page: Page, flask_server):
    """Test 3: Article Creation with Rich Text"""
    logger.info('Running article creation test')
    admin_login(page)
    
    page.goto("http://localhost:5000/admin/articles")
    page.click("a:has-text('Add Article')")
    page.fill("input[name='title']", "Test Article")
    # Wait for the editor to be ready
    page.wait_for_selector(".ql-editor", state="visible")
    # Fill the rich text editor
    page.locator(".ql-editor").fill("Test content with formatting")
    page.click("button:has-text('Save')")
    # Wait for the article to appear
    page.wait_for_selector("text=Test Article", state="visible")
    expect(page.locator("text=Test Article")).to_be_visible()

@pytest.mark.e2e
def test_search_functionality(page: Page, flask_server):
    """Test 4: Search Functionality and Results"""
    logger.info('Running search functionality test')
    page.goto("http://localhost:5000")
    page.fill("input[name='q']", "test")
    page.click("button:has-text('Search')")
    # Wait for search results
    page.wait_for_selector(".search-results", state="visible")
    expect(page.locator(".search-results")).to_be_visible()

@pytest.mark.e2e
def test_article_view_counter(page: Page, flask_server):
    """Test 5: Article View Counter Increment"""
    logger.info('Running article view counter test')
    page.goto("http://localhost:5000/article/1")  # Using the test article created in setup
    # Wait for view count to be visible
    page.wait_for_selector(".view-count", state="visible")
    initial_views = page.locator(".view-count").inner_text()
    page.reload()
    page.wait_for_selector(".view-count", state="visible")
    expect(page.locator(".view-count")).not_to_have_text(initial_views)

@pytest.mark.e2e
def test_category_reordering(page: Page, flask_server):
    """Test 6: Category Reordering via Drag and Drop"""
    logger.info('Running category reordering test')
    admin_login(page)
    
    page.goto("http://localhost:5000/admin/categories")
    # Wait for categories to be loaded
    page.wait_for_selector(".category-item", state="visible")
    # Perform drag and drop operation
    source = page.locator(".category-item").first
    target = page.locator(".category-item").last
    source.drag_to(target)
    # Wait for the order to update
    time.sleep(1)  # Give time for any animations to complete

@pytest.mark.e2e
def test_image_upload(page: Page, flask_server):
    """Test 7: Image Upload in Articles"""
    logger.info('Running image upload test')
    admin_login(page)
    
    page.goto("http://localhost:5000/admin/articles/add")
    # Wait for the file input to be ready
    page.wait_for_selector("input[type='file']", state="visible")
    # Upload image using file input
    page.set_input_files("input[type='file']", "tests/test_image.jpg")
    # Wait for preview
    page.wait_for_selector(".upload-preview", state="visible")
    expect(page.locator(".upload-preview")).to_be_visible()

@pytest.mark.e2e
def test_admin_dashboard_metrics(page: Page, flask_server):
    """Test 8: Admin Dashboard Metrics"""
    logger.info('Running admin dashboard metrics test')
    admin_login(page)
    
    page.goto("http://localhost:5000/admin")
    # Wait for metrics to load
    page.wait_for_selector(".total-articles", state="visible")
    page.wait_for_selector(".total-views", state="visible")
    page.wait_for_selector(".total-searches", state="visible")
    expect(page.locator(".total-articles")).to_be_visible()
    expect(page.locator(".total-views")).to_be_visible()
    expect(page.locator(".total-searches")).to_be_visible()

@pytest.mark.e2e
def test_article_editing(page: Page, flask_server):
    """Test 9: Article Editing and Content Sanitization"""
    logger.info('Running article editing test')
    admin_login(page)
    
    page.goto("http://localhost:5000/admin/articles")
    # Wait for articles to load
    page.wait_for_selector("a:has-text('Edit')", state="visible")
    page.click("a:has-text('Edit')")
    # Wait for editor
    page.wait_for_selector(".ql-editor", state="visible")
    page.locator(".ql-editor").fill("<script>alert('test')</script>Safe content")
    page.click("button:has-text('Save')")
    # Wait for content to be saved and displayed
    page.wait_for_selector("text=Safe content", state="visible")
    expect(page.locator("text=Safe content")).to_be_visible()
    expect(page.locator("script:has-text('test')")).not_to_be_attached()

@pytest.mark.e2e
def test_responsive_design(page: Page, flask_server):
    """Test 10: Responsive Design Across Viewports"""
    logger.info('Running responsive design test')
    # Test mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:5000")
    expect(page.locator(".navbar-toggler")).to_be_visible()
    
    # Test tablet viewport
    page.set_viewport_size({"width": 768, "height": 1024})
    page.goto("http://localhost:5000")
    
    # Test desktop viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto("http://localhost:5000")
    expect(page.locator(".navbar-toggler")).not_to_be_visible()
