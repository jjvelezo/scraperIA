import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchFrameException, WebDriverException
import time
from bs4 import BeautifulSoup

def scrape_website(website):
    print("Launching chrome browser...")

    options = webdriver.ChromeOptions()
    # Add options to handle potential iframe issues
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--no-sandbox")

    # Selenium Manager (bundled with Selenium >= 4.10) downloads a matching
    # chromedriver automatically, so no local binary/path is needed.
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(website)
        print("Page loaded...")
        
        # Wait for page to fully load
        time.sleep(5)
        
        # Get main page content
        main_html = driver.page_source
        print("Main content extracted...")
        
        # Find and extract iframe content
        iframe_contents = extract_iframe_content(driver)
        
        # Combine main content with iframe contents
        combined_html = combine_content(main_html, iframe_contents)
        
        return combined_html
        
    finally:
        driver.quit()

def extract_iframe_content(driver):
    iframe_contents = []
    
    try:
        # Find all iframes on the page
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")
        
        for i, iframe in enumerate(iframes):
            try:
                print(f"Processing iframe {i+1}...")
                
                # Get iframe source URL if available
                iframe_src = iframe.get_attribute("src")
                iframe_id = iframe.get_attribute("id") or f"iframe_{i}"
                
                print(f"Iframe {i+1} - ID: {iframe_id}, SRC: {iframe_src}")
                
                # Switch to iframe
                driver.switch_to.frame(iframe)
                
                # Wait a bit for iframe content to load
                time.sleep(3)
                
                # Get iframe content
                iframe_html = driver.page_source
                
                # Store iframe content with metadata
                iframe_data = {
                    'id': iframe_id,
                    'src': iframe_src,
                    'content': iframe_html
                }
                iframe_contents.append(iframe_data)
                
                print(f"Iframe {i+1} content extracted successfully")
                
            except (NoSuchFrameException, WebDriverException) as e:
                print(f"Could not access iframe {i+1}: {str(e)}")
                
            finally:
                # Always switch back to main content
                try:
                    driver.switch_to.default_content()
                except:
                    pass
                    
    except Exception as e:
        print(f"Error finding iframes: {str(e)}")
    
    return iframe_contents

def combine_content(main_html, iframe_contents):
    """Combine main page content with iframe contents"""
    combined_content = f"=== MAIN PAGE CONTENT ===\n{main_html}\n\n"
    
    for i, iframe_data in enumerate(iframe_contents):
        combined_content += f"=== IFRAME {i+1} CONTENT ===\n"
        combined_content += f"ID: {iframe_data['id']}\n"
        combined_content += f"SRC: {iframe_data['src']}\n"
        combined_content += f"CONTENT:\n{iframe_data['content']}\n\n"
    
    return combined_content

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Handle combined content (main + iframes)
    if "=== MAIN PAGE CONTENT ===" in html_content:
        return html_content  # Return as-is since it's already structured
    
    # Handle regular single page content
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    # Handle combined content structure
    if "=== MAIN PAGE CONTENT ===" in body_content:
        sections = body_content.split("===")
        cleaned_sections = []
        
        for section in sections:
            if section.strip():
                # Clean each section separately
                soup = BeautifulSoup(section, "html.parser")
                for script_or_style in soup(["script", "style"]):
                    script_or_style.extract()
                
                cleaned_text = soup.get_text(separator="\n")
                cleaned_text = "\n".join(
                    line.strip() for line in cleaned_text.splitlines() if line.strip()
                )
                
                if cleaned_text.strip():
                    cleaned_sections.append(cleaned_text)
        
        return "\n\n".join(cleaned_sections)
    
    # Handle regular content
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]

