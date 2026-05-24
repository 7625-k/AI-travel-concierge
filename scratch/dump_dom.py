from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        
        # Log in
        page.wait_for_selector("input[placeholder='Enter your username']", timeout=20000)
        page.fill("input[placeholder='Enter your username']", "testuser")
        page.fill("input[placeholder='••••••••']", "password")
        page.click("button:has-text('Sign In to Concierge')")
        
        # Wait for main page
        page.wait_for_selector("button:has-text('Chat Assistant')", timeout=20000)
        time.sleep(2) # Give a second for styles to settle
        
        with open("scratch/dom_output.txt", "w", encoding="utf-8") as f:
            # Active button (Chat Assistant)
            active_btn = page.query_selector("button:has-text('Chat Assistant')")
            if active_btn:
                f.write("Active Button (Chat Assistant) Computed Styles:\n")
                bg = active_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
                bg_img = active_btn.evaluate("el => window.getComputedStyle(el).backgroundImage")
                color = active_btn.evaluate("el => window.getComputedStyle(el).color")
                border = active_btn.evaluate("el => window.getComputedStyle(el).border")
                f.write(f"  background-color = '{bg}'\n")
                f.write(f"  background-image = '{bg_img}'\n")
                f.write(f"  color = '{color}'\n")
                f.write(f"  border = '{border}'\n")
            
            # Inactive button (AI Trip Planner)
            inactive_btn = page.query_selector("button:has-text('AI Trip Planner')")
            if inactive_btn:
                f.write("\nInactive Button (AI Trip Planner) Computed Styles:\n")
                bg = inactive_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
                bg_img = inactive_btn.evaluate("el => window.getComputedStyle(el).backgroundImage")
                color = inactive_btn.evaluate("el => window.getComputedStyle(el).color")
                border = inactive_btn.evaluate("el => window.getComputedStyle(el).border")
                f.write(f"  background-color = '{bg}'\n")
                f.write(f"  background-image = '{bg_img}'\n")
                f.write(f"  color = '{color}'\n")
                f.write(f"  border = '{border}'\n")
                
        # Take a final screenshot to confirm visually
        page.screenshot(path="scratch/logged_in_styled.png")
        print("Updated styling screenshot saved to scratch/logged_in_styled.png")
                        
    except Exception as e:
        with open("scratch/dom_output.txt", "w", encoding="utf-8") as f:
            f.write(f"Error: {e}\n")
    finally:
        browser.close()
