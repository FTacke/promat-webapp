from playwright.sync_api import sync_playwright
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto('http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation')
            
            def get_style(selector, prop):
                el = page.query_selector(selector)
                if not el: return 'Not Found'
                return el.evaluate(f'(el) => getComputedStyle(el).{prop}')

            padding_section = get_style('.audio-section', 'padding')
            mb_header = get_style('.audio-section-header', 'marginBottom')
            mt_grid = get_style('.audio-grid', 'marginTop')
            padding_card = get_style('.audio-card', 'padding')
            
            # Find all potential cards and players
            all_elements = page.query_selector_all('*')
            cards = [el for el in all_elements if 'card' in (el.get_attribute('class') or '').lower()]
            
            players = page.query_selector_all('.audio-player, audio, .player, [class*="player"]')
            
            print(f'Audio Section Padding: {padding_section}')
            print(f'Header Margin Bottom: {mb_header}')
            print(f'Grid Margin Top: {mt_grid}')
            print(f'Card Padding: {padding_card}')
            
            if len(players) >= 2:
                o0 = players[0].evaluate('(el) => el.offsetTop')
                o1 = players[1].evaluate('(el) => el.offsetTop')
                print(f'Player Offset Delta: {o1 - o0}px')
            else:
                print(f'Players found: {len(players)}')

        except Exception as e:
            print(f'Error: {e}')
        finally:
            browser.close()

if __name__ == "__main__":
    run()
