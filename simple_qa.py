import asyncio
from playwright.async_api import async_playwright
async def f():
  async with async_playwright() as p:
    b = await p.chromium.launch()
    p = await b.new_page()
    for l in ['de', 'en']:
      await p.goto(f'http://127.0.0.1:8000/{l}/teaching/spanish/which-pronunciation')
      h = await p.evaluate('() => Array.from(document.querySelectorAll(".didactic-card")).map(c => c.offsetHeight)')
      fr = await p.evaluate('() => document.querySelectorAll(".further-reading li").length')
      print(f'{l} Heights: {h}, FR: {fr}')
    await b.close()
asyncio.run(f())
