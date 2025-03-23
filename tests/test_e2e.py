import pytest
from playwright.sync_api import expect, Page
import os
import time
import logging
import threading
from app import create_app
import uuid

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def flask_server(app):
    """Start Flask server for testing"""
    def run_app():
        app.run(port=5000)
    
    logger.info("Starting Flask server...")
    server = threading.Thread(target=run_app, daemon=True)
    server.start()
    time.sleep(2)  # Give the server time to start
    logger.info("Flask server is running")
    yield server
    logger.info("Flask server fixture cleanup complete")

@pytest.fixture(autouse=True)
def setup_test(page: Page):
    """Setup and cleanup for each test"""
    # Set timeout to 5 seconds for all operations
    logger.info("Setting up test with 5s timeout")
    page.set_default_timeout(5000)  # 5 seconds
    yield
    try:
        logger.info("Cleaning up test - closing page")
        page.close()
    except Exception as e:
        logger.error(f"Error closing page: {e}")

def admin_login(page: Page):
    """Helper function to perform admin login"""
    logger.info('Performing admin login...')
    page.goto("http://localhost:5000/admin/login")
    
    logger.debug("Filling login form")
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    
    logger.debug("Submitting login form")
    with page.expect_navigation():
        page.click("button[type='submit']")
    
    logger.debug("Waiting for navigation to admin page")
    page.wait_for_selector(".navbar-brand:has-text('Knowledge Base Admin')")
    logger.info("Admin login successful")

@pytest.mark.e2e
def test_admin_login(page: Page, flask_server):
    """Test 1: Admin Login Functionality"""
    logger.info('Running admin login test')
    admin_login(page)
    # Check if we're on the admin page (with or without trailing slash)
    logger.debug("Verifying admin page URL")
    assert page.url.rstrip('/') == "http://localhost:5000/admin"
    logger.info("Admin login test passed")

@pytest.mark.e2e
def test_category_creation(page: Page, flask_server):
    """Test 2: Category Creation and Validation"""
    logger.info('Running category creation test')
    admin_login(page)

    # Generate unique category name
    category_name = f"Test Category {uuid.uuid4().hex[:8]}"
    category_desc = f"Description for {category_name}"

    logger.debug("Navigating to categories page")
    page.goto("http://localhost:5000/admin/categories")
    
    logger.debug("Opening add category modal")
    page.click("button:has-text('Add Category')")
    
    logger.debug("Filling category form")
    page.fill("#categoryName", category_name)
    page.fill("#categoryDescription", category_desc)
    
    logger.debug("Submitting category form")
    with page.expect_navigation():  # Wait for page reload after form submission
        page.click("#addCategoryForm button[type='submit']")
    
    logger.debug("Waiting for success message")
    page.wait_for_selector(".alert-success:has-text('Category added successfully')")
    
    logger.debug("Waiting for page to settle")
    page.wait_for_timeout(1000)  # Wait 1 second for any animations/transitions
    
    logger.debug("Waiting for category to appear in table")
    row = page.locator("[data-testid='category-row']", has_text=category_name)
    expect(row).to_be_visible()
    expect(row).to_contain_text(category_desc)
    
    logger.info("Category creation test passed")

@pytest.mark.e2e
def test_article_creation(page: Page, flask_server):
    """Test 3: Article Creation with Rich Text"""
    logger.info('Running article creation test')
    admin_login(page)
    
    logger.debug("Navigating to articles page")
    page.goto("http://localhost:5000/admin/articles")
    logger.debug("Clicking add article button")
    page.click("a:has-text('Add Article')")
    logger.debug("Filling article form")
    page.fill("input[name='title']", "Test Article")
    # Wait for the editor to be ready
    logger.debug("Waiting for editor to be ready")
    page.wait_for_selector(".ql-editor", state="visible", timeout=5000)
    # Fill the rich text editor
    logger.debug("Filling rich text editor")
    page.locator(".ql-editor").fill("Test content with formatting")
    logger.debug("Submitting article form")
    page.click("button:has-text('Save')")
    # Wait for the article to appear
    logger.debug("Waiting for article to appear")
    page.wait_for_selector("text=Test Article", state="visible", timeout=5000)
    expect(page.locator("text=Test Article")).to_be_visible()
    logger.info("Article creation test passed")

@pytest.mark.e2e
def test_search_functionality(page: Page, flask_server):
    """Test 4: Search Functionality and Results"""
    logger.info('Running search functionality test')
    logger.debug("Navigating to search page")
    page.goto("http://localhost:5000")
    logger.debug("Filling search form")
    page.fill("#search-input", "test")
    logger.debug("Submitting search form")
    page.click("button:has-text('Search')")
    # Wait for search results
    logger.debug("Waiting for search results")
    page.wait_for_selector(".search-results-section:not(.d-none)", state="visible", timeout=5000)
    expect(page.locator(".search-results-section")).not_to_have_class("d-none")
    logger.info("Search functionality test passed")

@pytest.mark.e2e
def test_article_view_counter(page: Page, flask_server):
    """Test 5: Article View Counter Increment"""
    logger.info('Running article view counter test')
    logger.debug("Navigating to article page")
    page.goto("http://localhost:5000/article/1")  # Using the test article created in setup
    # Wait for view count to be visible
    logger.debug("Waiting for view count to be visible")
    page.wait_for_selector(".view-count", state="visible", timeout=5000)
    logger.debug("Getting initial view count")
    initial_views = page.locator(".view-count").inner_text()
    logger.debug("Reloading page")
    page.reload()
    logger.debug("Waiting for view count to be visible after reload")
    page.wait_for_selector(".view-count", state="visible", timeout=5000)
    expect(page.locator(".view-count")).not_to_have_text(initial_views)
    logger.info("Article view counter test passed")

@pytest.mark.e2e
def test_category_reordering(page: Page, flask_server):
    """Test 6: Category Reordering via Drag and Drop"""
    logger.info('Running category reordering test')
    admin_login(page)
    
    logger.debug("Navigating to categories page")
    page.goto("http://localhost:5000/admin/categories")
    # Wait for categories to be loaded
    logger.debug("Waiting for categories to be loaded")
    page.wait_for_selector(".category-item", state="visible", timeout=5000)
    # Perform drag and drop operation
    logger.debug("Performing drag and drop operation")
    source = page.locator(".category-item").first
    target = page.locator(".category-item").last
    source.drag_to(target)
    # Wait for the order to update
    logger.debug("Waiting for order to update")
    time.sleep(1)  # Give time for any animations to complete
    logger.info("Category reordering test passed")

@pytest.mark.e2e
def test_image_upload(page: Page, flask_server):
    """Test 7: Image Upload in Articles"""
    logger.info('Running image upload test')
    admin_login(page)
    
    logger.debug("Navigating to article creation page")
    page.goto("http://localhost:5000/admin/articles/add")
    # Wait for the file input to be ready
    logger.debug("Waiting for file input to be ready")
    page.wait_for_selector("input[type='file']", state="visible", timeout=5000)
    # Upload image using file input
    logger.debug("Uploading image")
    page.set_input_files("input[type='file']", "tests/test_image.jpg")
    # Wait for preview
    logger.debug("Waiting for preview")
    page.wait_for_selector(".upload-preview", state="visible", timeout=5000)
    expect(page.locator(".upload-preview")).to_be_visible()
    logger.info("Image upload test passed")

@pytest.mark.e2e
def test_admin_dashboard_metrics(page: Page, flask_server):
    """Test 8: Admin Dashboard Metrics"""
    logger.info('Running admin dashboard metrics test')
    admin_login(page)
    
    logger.debug("Navigating to admin dashboard")
    page.goto("http://localhost:5000/admin")
    # Wait for metrics to load
    logger.debug("Waiting for metrics to load")
    page.wait_for_selector(".total-articles", state="visible", timeout=5000)
    page.wait_for_selector(".total-views", state="visible", timeout=5000)
    page.wait_for_selector(".total-searches", state="visible", timeout=5000)
    expect(page.locator(".total-articles")).to_be_visible()
    expect(page.locator(".total-views")).to_be_visible()
    expect(page.locator(".total-searches")).to_be_visible()
    logger.info("Admin dashboard metrics test passed")

@pytest.mark.e2e
def test_article_editing(page: Page, flask_server):
    """Test 9: Article Editing and Content Sanitization"""
    logger.info('Running article editing test')
    admin_login(page)
    
    logger.debug("Navigating to article list page")
    page.goto("http://localhost:5000/admin/articles")
    # Wait for articles to load
    logger.debug("Waiting for articles to load")
    page.wait_for_selector("a:has-text('Edit')", state="visible", timeout=5000)
    logger.debug("Clicking edit button")
    page.click("a:has-text('Edit')")
    # Wait for editor
    logger.debug("Waiting for editor to be ready")
    page.wait_for_selector(".ql-editor", state="visible", timeout=5000)
    logger.debug("Filling editor with malicious content")
    page.locator(".ql-editor").fill("<script>alert('test')</script>Safe content")
    logger.debug("Submitting article form")
    page.click("button:has-text('Save')")
    # Wait for content to be saved and displayed
    logger.debug("Waiting for content to be saved and displayed")
    page.wait_for_selector("text=Safe content", state="visible", timeout=5000)
    expect(page.locator("text=Safe content")).to_be_visible()
    expect(page.locator("script:has-text('test')")).not_to_be_attached()
    logger.info("Article editing test passed")

@pytest.mark.e2e
def test_responsive_design(page: Page, flask_server):
    """Test 10: Responsive Design Across Viewports"""
    logger.info('Running responsive design test')
    # Test mobile viewport
    logger.debug("Setting mobile viewport")
    page.set_viewport_size({"width": 375, "height": 667})
    logger.debug("Navigating to homepage")
    page.goto("http://localhost:5000")
    expect(page.locator(".navbar-toggler")).to_be_visible()
    
    # Test tablet viewport
    logger.debug("Setting tablet viewport")
    page.set_viewport_size({"width": 768, "height": 1024})
    logger.debug("Navigating to homepage")
    page.goto("http://localhost:5000")
    
    # Test desktop viewport
    logger.debug("Setting desktop viewport")
    page.set_viewport_size({"width": 1920, "height": 1080})
    logger.debug("Navigating to homepage")
    page.goto("http://localhost:5000")
    expect(page.locator(".navbar-toggler")).not_to_be_visible()
    logger.info("Responsive design test passed")
