from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time

# --- Setup Firefox driver ---
options = Options()
driver = webdriver.Firefox(options=options)

# --- Step 1: Go directly to the YouTube channel ---
driver.get("https://www.youtube.com/@TV5Philippines")
time.sleep(5)  # wait for the page to fully load

# --- Step 2: Look for any "LIVE" video ---
try:
    # Find any thumbnail with "LIVE" badge text
    live_badge = driver.find_element(By.XPATH, "//span[contains(text(), 'LIVE')]")
    
    # Move up to the clickable video link container
    video_link = live_badge.find_element(By.XPATH, "../../../../..")
    video_link.click()
    print("✅ Livestream found and clicked!")
except Exception as e:
    print("⚠️ No livestream found on the channel or layout changed.")
    print("Error:", e)

# --- Step 3: Keep the browser open for a while ---
time.sleep(9999999)
driver.quit()
