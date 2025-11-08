from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Setup Firefox driver ---
options = Options()
driver = webdriver.Firefox(options=options)

# --- Step 1: Go directly to the YouTube channel ---
driver.get("https://www.youtube.com/@gmanetwork")
time.sleep(5)  # wait for the page to fully load

# --- Step 2: Look for any "LIVE" video and click it ---
try:
    # Find any thumbnail with "LIVE" badge text
    live_badge = driver.find_element(By.XPATH, "//span[contains(text(), 'LIVE')]")

    # Move up to the clickable video link container
    video_link = live_badge.find_element(By.XPATH, "../../../../..")
    video_link.click()
    print("✅ Livestream found and clicked!")

    # -------------------------------------------------------------------
    #                   NEW ORDER: CLOSE CHAT FIRST
    # -------------------------------------------------------------------

    # --- Step 3: Wait for the live video page to load ---
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='movie_player']"))
    )
    print("🎬 Video player detected, waiting for chat to load...")

    # --- Step 4: Close the Livestream Chat Panel ---
    try:
        # Wait for the chat iframe to appear
        chat_iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@id='chatframe']"))
        )
        print("💬 Chat iframe found.")

        # Switch to the chat iframe
        driver.switch_to.frame(chat_iframe)

        # Wait 7 seconds for chat contents to load fully
        print("⏳ Waiting 7 seconds for chat to fully load...")
        time.sleep(7)
        print("✅ 7 seconds passed, attempting to close chat...")

        # Your provided XPath for the close chat button
        close_chat_xpath = (
            "/html/body/yt-live-chat-app/div/yt-live-chat-renderer/"
            "tp-yt-iron-pages/div/yt-live-chat-header-renderer/div[4]/"
            "yt-button-renderer/yt-button-shape/button"
        )

        # Wait for and click the button
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, close_chat_xpath))
        )
        close_button.click()
        print("✅ Chat panel closed successfully using provided XPath!")

        # Switch back to main document
        driver.switch_to.default_content()

    except Exception as chat_error:
        print("⚠️ Could not close chat normally, using JS fallback.")
        print("Chat Error:", chat_error)
        driver.switch_to.default_content()
        driver.execute_script(
            "chat = document.querySelector('#chat, #chatframe'); "
            "if (chat) chat.style.display='none';"
        )
        print("✅ Chat iframe hidden via JS fallback.")

    # -------------------------------------------------------------------
    #                   AFTER CHAT IS CLOSED → FULLSCREEN
    # -------------------------------------------------------------------

    try:
        # Ensure the player is still loaded
        video_player = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='movie_player']"))
        )
        time.sleep(1.5)
        video_player.send_keys("f")
        print("✅ Sent 'f' key. Video should now be fullscreen (after chat closed).")

    except Exception as fs_error:
        print("⚠️ Could not enter fullscreen.")
        print("Fullscreen Error:", fs_error)

except Exception as e:
    print("⚠️ No livestream found on the channel or layout changed.")
    print("Error:", e)

# -------------------------------------------------------------------
#                 NEW ADDITIONS END HERE
# -------------------------------------------------------------------

print("Browser will remain open for monitoring.")
time.sleep(9999999)
driver.quit()
