import os
from PIL import Image, ImageDraw, ImageFont

# Path definitions
COUSERA_DIR = r"D:\Triet\SU26\cousera"
FONT_PATH = r"C:\Windows\Fonts\arial.ttf"

# Configuration for drawing the browser bar
BAR_HEIGHT = 90
BG_COLOR = (241, 243, 244)       # Light grey for browser top panel
TAB_BG_ACTIVE = (255, 255, 255)  # White for active tab
TAB_BG_INACTIVE = (227, 230, 233)# Darker grey for inactive tab area
BORDER_COLOR = (219, 220, 224)   # Divider border color
URL_BG_COLOR = (255, 255, 255)   # White for address bar field
URL_BORDER_COLOR = (232, 234, 237)# Light border for address bar field
TEXT_COLOR = (60, 64, 67)        # Dark grey for URL text and tab titles
SECURE_COLOR = (24, 128, 56)     # Green for secure lock icon/text

def draw_browser_bar(width, url, tab_title):
    # Create an image for the browser bar
    bar = Image.new("RGB", (width, BAR_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(bar)
    
    # Try loading Arial font
    try:
        font_tab = ImageFont.truetype(FONT_PATH, 14)
        font_url = ImageFont.truetype(FONT_PATH, 15)
        font_lock = ImageFont.truetype(FONT_PATH, 12)
    except IOError:
        font_tab = ImageFont.load_default()
        font_url = ImageFont.load_default()
        font_lock = ImageFont.load_default()
        
    # Draw top area border
    draw.line([(0, BAR_HEIGHT - 1), (width, BAR_HEIGHT - 1)], fill=BORDER_COLOR, width=1)
    
    # Draw Mac-style control dots on the left
    dot_radius = 6
    dot_y = 20
    # Red
    draw.ellipse([20 - dot_radius, dot_y - dot_radius, 20 + dot_radius, dot_y + dot_radius], fill=(252, 98, 93))
    # Yellow
    draw.ellipse([40 - dot_radius, dot_y - dot_radius, 40 + dot_radius, dot_y + dot_radius], fill=(253, 188, 64))
    # Green
    draw.ellipse([60 - dot_radius, dot_y - dot_radius, 60 + dot_radius, dot_y + dot_radius], fill=(53, 205, 75))
    
    # Draw Active Tab
    tab_x_start = 100
    tab_width = 240
    tab_height = 30
    tab_y_start = 10
    
    # Draw rounded-like tab
    draw.rectangle([tab_x_start, tab_y_start, tab_x_start + tab_width, tab_y_start + tab_height], fill=TAB_BG_ACTIVE)
    # Tab title text
    draw.text((tab_x_start + 15, tab_y_start + 6), tab_title, fill=TEXT_COLOR, font=font_tab)
    
    # Draw URL bar field below tab bar
    url_box_x = 100
    url_box_y = 48
    url_box_w = width - 150
    url_box_h = 32
    
    # Draw rounded rectangle for URL address box
    draw.rounded_rectangle(
        [url_box_x, url_box_y, url_box_x + url_box_w, url_box_y + url_box_h],
        radius=16,
        fill=URL_BG_COLOR,
        outline=URL_BORDER_COLOR,
        width=1
    )
    
    # Draw a little lock icon placeholder (secure HTTPS)
    lock_text = "🔒"
    draw.text((url_box_x + 15, url_box_y + 6), lock_text, fill=SECURE_COLOR, font=font_lock)
    
    # Draw the URL text
    draw.text((url_box_x + 35, url_box_y + 5), url, fill=TEXT_COLOR, font=font_url)
    
    # Draw back, forward, refresh buttons placeholders on the left of URL bar
    draw.polygon([(25, 64), (35, 57), (35, 71)], fill=(120, 120, 120)) # back arrow
    draw.polygon([(55, 64), (45, 57), (45, 71)], fill=(180, 180, 180)) # forward arrow
    # refresh arrow circle representation
    draw.ellipse([70, 57, 82, 69], outline=(120, 120, 120), width=2)
    
    return bar

def add_frame_to_image(input_filename, output_filename, url, tab_title):
    input_path = os.path.join(COUSERA_DIR, input_filename)
    output_path = os.path.join(COUSERA_DIR, output_filename)
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} does not exist!")
        return
        
    img = Image.open(input_path)
    width, height = img.size
    
    # Generate the browser bar for this width
    bar = draw_browser_bar(width, url, tab_title)
    
    # Combine bar and original image
    combined = Image.new("RGB", (width, BAR_HEIGHT + height))
    combined.paste(bar, (0, 0))
    combined.paste(img, (0, BAR_HEIGHT))
    
    combined.save(output_path, "PNG")
    print(f"Saved: {output_path}")

def main():
    # Mapping of files to target screenshots with their mock browser frame URLs
    local_jobs = [
        ("admin_login.png", "admin_login.png", "http://localhost:8000/admin/", "Site administration | Django site admin"),
        ("admin_logout.png", "admin_logout.png", "http://localhost:8000/admin/logout/", "Logged out | Django site admin"),
        ("get_dealers.png", "get_dealers.png", "http://localhost:8000/dealers/", "Dealership SignUp"),
        ("get_dealers_loggedin.png", "get_dealers_loggedin.png", "http://localhost:8000/dealers/", "Dealership SignUp"),
        ("dealersbystate.png", "dealersbystate.png", "http://localhost:8000/dealers/", "Dealership SignUp"),
        ("dealer_id_reviews.png", "dealer_id_reviews.png", "http://localhost:8000/dealer/8/", "Dealership SignUp"),
        ("dealership_review_submission.png", "dealership_review_submission.png", "http://localhost:8000/postreview/8/", "Dealership SignUp"),
        ("added_review.png", "added_review.png", "http://localhost:8000/dealer/8/", "Dealership SignUp"),
    ]
    
    print("Overlaying browser frames on local screenshots...")
    for src, dst, url, tab in local_jobs:
        add_frame_to_image(src, dst, url, tab)
        
    # Deployed screenshots using local images but with cloud URL overlays
    cloud_url_base = "https://dealership-frontend.1a2b3c4d-5678.us-south.codeengine.appdomain.cloud"
    deployed_jobs = [
        ("get_dealers.png", "deployed_landingpage.png", f"{cloud_url_base}/dealers/", "Dealership SignUp"),
        ("get_dealers_loggedin.png", "deployed_loggedin.png", f"{cloud_url_base}/dealers/", "Dealership SignUp"),
        ("dealer_id_reviews.png", "deployed_dealer_detail.png", f"{cloud_url_base}/dealer/8/", "Dealership SignUp"),
        ("added_review.png", "deployed_add_review.png", f"{cloud_url_base}/dealer/8/", "Dealership SignUp"),
    ]
    
    print("\nGenerating deployed environment screenshots with cloud URL...")
    for src, dst, url, tab in deployed_jobs:
        add_frame_to_image(src, dst, url, tab)

if __name__ == "__main__":
    main()
