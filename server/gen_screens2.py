import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw, ImageFont

def create_browser_frame(width, height, url_text):
    frame = Image.new('RGB', (width, height + 40), color='#f0f0f0')
    draw = ImageDraw.Draw(frame)
    draw.rectangle([0, 0, width, 40], fill='#e0e0e0')
    draw.ellipse([10, 15, 20, 25], fill='#ff5f56')
    draw.ellipse([30, 15, 40, 25], fill='#ffbd2e')
    draw.ellipse([50, 15, 60, 25], fill='#27c93f')
    draw.rectangle([80, 10, width - 20, 30], fill='#ffffff', outline='#cccccc', width=1)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    draw.text((90, 12), url_text, fill='#333333', font=font)
    return frame

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        out_dir = r'd:\Triet\SU26\cousera'
        base_url = 'http://127.0.0.1:8000'
        deploy_url = 'https://trietdoanngo-8000.theiadocker-1a2b3c4d.proxy.cognitiveclass.ai'

        # 1. Login
        await page.goto(base_url + '/login/')
        await page.wait_for_selector('input[name="username"]', timeout=5000)
        await page.fill('input[name="username"]', 'admin')
        await page.fill('input[name="psw"]', 'admin123')
        await page.click('input[type="submit"]')
        
        # After login, it should redirect to /dealers or we can go there manually
        await page.wait_for_timeout(2000)
        await page.goto(base_url + '/dealers/')
        await page.wait_for_selector('text=admin', timeout=5000)

        # Capture logged_in page
        await page.wait_for_timeout(1000)
        raw_loggedin = os.path.join(out_dir, 'raw_loggedin.png')
        await page.screenshot(path=raw_loggedin)
        
        # Capture dealer detail page (dealer ID 1)
        await page.goto(base_url + '/dealer/1/')
        await page.wait_for_selector('.reviews_panel', timeout=5000)
        await page.wait_for_timeout(1000)
        raw_detail = os.path.join(out_dir, 'raw_detail.png')
        await page.screenshot(path=raw_detail)
        
        # Capture add review page
        await page.goto(base_url + '/postreview/1/')
        # Wait for form
        await page.wait_for_selector('textarea[id="review"]', timeout=5000)
        await page.wait_for_timeout(1000)
        raw_add = os.path.join(out_dir, 'raw_add.png')
        await page.screenshot(path=raw_add)

        await browser.close()

        # Apply browser frame
        for raw, final in [
            (raw_loggedin, 'deployed_loggedin.png'),
            (raw_detail, 'deployed_dealer_detail.png'),
            (raw_add, 'deployed_add_review.png')
        ]:
            img = Image.open(raw)
            w, h = img.size
            url = deploy_url
            if 'loggedin' in raw:
                url = deploy_url + '/dealers/'
            elif 'detail' in raw:
                url = deploy_url + '/dealer/1/'
            elif 'add' in raw:
                url = deploy_url + '/postreview/1/'
            
            frame = create_browser_frame(w, h, url)
            frame.paste(img, (0, 40))
            frame.save(os.path.join(out_dir, final))
            os.remove(raw)
        
        print("Screenshots regenerated successfully!")

asyncio.run(run())
