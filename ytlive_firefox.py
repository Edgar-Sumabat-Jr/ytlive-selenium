from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import pytz
import os


# 1. Define the path to your Firefox profile directory
profile_path = r'/home/ed/snap/firefox/common/.mozilla/firefox/kv02ko7y.default'

# 2. Define the path to your geckodriver executable
geckodriver_path = r'/home/ed/Documents/ytlive/geckodriver-v0.35.0-linux64/geckodriver'

# 3. Create Firefox options
options = Options()
options.add_argument("-profile")
options.add_argument(profile_path)

# 4. Set up a Service object if geckodriver is not in your system PATH
service = Service(executable_path=geckodriver_path)

# 5. Initialize the WebDriver with the options and service
driver = webdriver.Firefox(service=service, options=options)

# --- Step 1: Go directly to the YouTube channel ---
driver.get("https://www.youtube.com/@NBCNews")
time.sleep(5)  # Wait for the page to fully load

try:
    # --- Step 2: Find and click livestream ---
    live_badge = driver.find_element(By.XPATH, "//span[contains(text(), 'LIVE')]")
    video_link = live_badge.find_element(By.XPATH, "../../../../..")
    video_link.click()
    print("✅ Livestream found and clicked!")

    # --- Step 3: Wait for player to load ---
    player_xpath = "//div[@id='movie_player']"
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, player_xpath)))
    print("🎬 Video player detected, waiting for chat...")

    # --- Step 4: Close chat before fullscreen ---
    try:
        chat_iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@id='chatframe']"))
        )
        driver.switch_to.frame(chat_iframe)
        print("💬 Chat iframe found, closing chat...")
        time.sleep(7)
        close_chat_xpath = (
            "/html/body/yt-live-chat-app/div/yt-live-chat-renderer/"
            "tp-yt-iron-pages/div/yt-live-chat-header-renderer/div[4]/"
            "yt-button-renderer/yt-button-shape/button"
        )
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, close_chat_xpath))
        )
        close_button.click()
        print("✅ Chat closed successfully.")
        driver.switch_to.default_content()

    except Exception as chat_error:
        print("⚠️ Chat close failed, hiding via JS fallback.")
        driver.switch_to.default_content()
        driver.execute_script(
            "chat = document.querySelector('#chat, #chatframe'); "
            "if (chat) chat.style.display='none';"
        )
        print("✅ Chat iframe hidden via JS fallback.")

    # Go fullscreen
    video_player = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, player_xpath)))
    video_player.send_keys("f")
    print("✅ Video should now be fullscreen.")

except Exception as e:
    print("⚠️ Error: Livestream not found or layout changed.")
    print("Error:", e)

# -------------------------------------------------------------------
# Step 6: Wait until 2:30 PM Philippines time, then simulate shutdown
# -------------------------------------------------------------------

philippines_tz = pytz.timezone("Asia/Manila")

try:
    while True:
        # Check if the driver is still connected and if there is at least one window
        if len(driver.window_handles) == 0 or not driver.service.is_connectable():
            print("⚠️ Firefox is closed or the window is no longer available. Terminating program.")
            break

        now_ph = datetime.now(philippines_tz)
        current_time = now_ph.strftime("%I:%M:%S %p")
        print(f"⏰ Current PH Time: {current_time}", end="\r")

        # Adjust to the correct 2:30 PM time check
        if now_ph.hour == 14 and now_ph.minute == 30:
            print("\n🕑 2:30 PM reached! Closing Firefox and shutting down...")
            driver.quit()  # Ensure browser is properly closed
            print("💻 Shutting down the PC...")

            # Shutdown command for Ubuntu/Linux
            os.system("sudo shutdown now")  # This will initiate shutdown immediately
            break

        time.sleep(10)  # Check every 10 seconds

except Exception as e:
    print(f"⚠️ An error occurred: {e}")

finally:
    # Always make sure the driver is quit at the end of the program
    try:
        driver.quit()
    except Exception as quit_error:
        print("⚠️ Driver quit error:", quit_error)
