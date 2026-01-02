from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import pytz
import os

from selenium.webdriver.chrome.service import Service  # Import Service


# Set up Chrome options (no need for Firefox options)
options = Options()
# Optional: You can disable GPU or run headlessly if needed
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')

# Set up the ChromeDriver service
service = Service(executable_path="/usr/lib/chromium-browser/chromedriver")  # Specify the path to chromedriver

# Initialize the WebDriver with the service and options
driver = webdriver.Chrome(service=service, options=options)


# --- Step 1: Go directly to the YouTube channel ---
driver.get("https://www.youtube.com/@TV5Philippines")
time.sleep(5)  # wait for the page to fully load

try:
    # --- Step 2: Find and click livestream ---
    live_badge = driver.find_element(By.XPATH, "//span[contains(text(), 'LIVE')]")
    video_link = live_badge.find_element(By.XPATH, "../../../../..")
    video_link.click()
    print("✅ Livestream found and clicked!")

    # --- Step 3: Wait for player to load ---
    player_xpath = "//div[@id='movie_player']"
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, player_xpath))
    )
    print("🎬 Video player detected, waiting for chat...")

    # --- Step 4: Close chat before fullscreen ---
    try:
        chat_iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@id='chatframe']"))
        )
        driver.switch_to.frame(chat_iframe)
        print("💬 Chat iframe found, waiting 7 seconds...")
        time.sleep(7)
        print("✅ 7 seconds done, closing chat...")

        close_chat_xpath = (
            "/html/body/yt-live-chat-app/div/yt-live-chat-renderer/"
            "tp-yt-iron-pages/div/yt-live-chat-header-renderer/div[4]/"
            "yt-button-renderer/yt-button-shape/button"
        )
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, close_chat_xpath))
        )
        close_button.click()
        print("✅ Chat panel closed successfully.")
        driver.switch_to.default_content()

    except Exception as chat_error:
        print("⚠️ Chat close failed, hiding via JS fallback.")
        driver.switch_to.default_content()
        driver.execute_script(
            "chat = document.querySelector('#chat, #chatframe'); "
            "if (chat) chat.style.display='none';"
        )
        print("✅ Chat iframe hidden via JS fallback.")

    # --- Step 5: Go fullscreen ---
    video_player = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, player_xpath))
    )
    time.sleep(1.5)
    video_player.send_keys("f")
    print("✅ Sent 'f' key. Video should now be fullscreen.")

except Exception as e:
    print("⚠️ Livestream not found or layout changed.")
    print("Error:", e)

# -------------------------------------------------------------------
# Step 6: Wait until 2:30 PM Philippines time, then simulate shutdown
# -------------------------------------------------------------------

philippines_tz = pytz.timezone("Asia/Manila")

print("🕒 Waiting for 2:30 PM Philippines time to close Firefox...")

while True:
    now_ph = datetime.now(philippines_tz)
    current_time = now_ph.strftime("%I:%M:%S %p")
    print(f"⏰ Current PH Time: {current_time}", end="\r")

    # Check if it's 2:30 PM
    if now_ph.hour == 14 and now_ph.minute == 30:
        print("\n🕑 2:30 PM reached! Closing Firefox and simulating shutdown...")
        driver.quit()
        print("💻 pc shutdown")
        os.system("shutdown /s /t 5")  # for Windows, shuts down in 5 seconds
        break

    time.sleep(10)  # check every 10 seconds
