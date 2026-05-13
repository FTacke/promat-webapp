import asyncio
import os
from playwright.async_api import async_playwright

async def capture():
    routes = [
        '/de/teaching',
        '/de/teaching/spanish',
        '/de/teaching/english',
        '/de/teaching/spanish/final-r',
        '/en/teaching',
        '/en/teaching/spanish',
        '/de/sample'
    ]
    base_url = 'http://127.0.0.1:8010'
    output_dir = 'tmp/ui-qa/2026-05-11-teaching-polish-followup-fresh'
    
    async with async_playwright() as p:
        # Launching msedge via channel
        browser = await p.chromium.launch(channel='msedge', headless=True)
        
        for route in routes:
            try:
                name = route.strip('/').replace('/', '_')
                url = f'{base_url}{route}'
                
                # Desktop
                context_desktop = await browser.new_context(viewport={'width': 1280, 'height': 800})
                page = await context_desktop.new_page()
                await page.goto(url, wait_until='networkidle')
                await page.screenshot(path=f'{output_dir}/{name}-desktop.png')
                
                # HTML Dump
                content = await page.content()
                with open(f'{output_dir}/{name}.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                await context_desktop.close()
                
                # Mobile
                context_mobile = await browser.new_context(viewport={'width': 375, 'height': 667}, is_mobile=True)
                page = await context_mobile.new_page()
                await page.goto(url, wait_until='networkidle')
                await page.screenshot(path=f'{output_dir}/{name}-mobile.png')
                await context_mobile.close()
                
                print(f'Captured {route}')
            except Exception as e:
                print(f'Failed {route}: {e}')
                
        await browser.close()

asyncio.run(capture())
