import asyncio
from playwright.async_api import async_playwright
import os

routes = [
    '/de/teaching',
    '/de/teaching/spanish',
    '/de/teaching/english',
    '/de/teaching/spanish/final-r',
    '/en/teaching',
    '/en/teaching/spanish'
]

qa_dir = 'tmp/ui-qa/2026-05-11-teaching-layout-grid'
base_url = 'http://127.0.0.1:8010'

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        desktop_context = await browser.new_context(viewport={'width': 1280, 'height': 1024})
        mobile_context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True)
        
        for route in routes:
            safe_name = route.strip('/').replace('/', '-')
            full_url = f'{base_url}{route}'
            
            # Desktop
            page = await desktop_context.new_page()
            try:
                await page.goto(full_url, wait_until='networkidle')
                await page.screenshot(path=f'{qa_dir}/{safe_name}-desktop.png')
                html = await page.content()
                with open(f'{qa_dir}/{safe_name}.html', 'w', encoding='utf-8') as f:
                    f.write(html)
            except Exception as e:
                print(f'Error capturing desktop {route}: {e}')
            await page.close()
            
            # Mobile
            page = await mobile_context.new_page()
            try:
                await page.goto(full_url, wait_until='networkidle')
                await page.screenshot(path=f'{qa_dir}/{safe_name}-mobile.png')
            except Exception as e:
                print(f'Error capturing mobile {route}: {e}')
            await page.close()
            
        await browser.close()

asyncio.run(capture())
