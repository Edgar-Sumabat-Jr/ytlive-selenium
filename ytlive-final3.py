import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import pytz
import os

# --------------------------------------------------
# Chrome options (NO profile for testing)
# --------------------------------------------------

TEST_MODE = False

options = uc.ChromeOptions()

# ✅ Chromium snap profile
options.add_argument("--user-data-dir=/home/ed/snap/chromium/common/chromium")
options.add_argument("--profile-directory=Profile 1")

options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--disable-blink-features=AutomationControlled")

# REQUIRED for snap Chromium stability
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")

print("🚀 Launching Chromium with profile...")

driver = uc.Chrome(
    options=options,
    use_subprocess=True
)

print("✅ Chromium launched, continuing script")


# --------------------------------------------------
# Decide which YouTube channel to open based on PH time
# --------------------------------------------------

philippines_tz = pytz.timezone("Asia/Manila")
now_ph = datetime.now(philippines_tz)

tv5_url = "https://www.youtube.com/@TV5Philippines"
gma_url = "https://www.youtube.com/@gmanetwork"

channel_url = None
shutdown_hour = None
shutdown_minute = None

# 8:00 AM to 2:30 PM → TV5 → shutdown at 2:30 PM
if (
    now_ph.hour >= 8
    and (now_ph.hour < 14 or (now_ph.hour == 14 and now_ph.minute <= 30))
):
    channel_url = tv5_url
    shutdown_hour = 14
    shutdown_minute = 30
    print("📺 TV5 selected | Shutdown at 2:30 PM")

# 2:35 PM onwards → GMA → shutdown at 8:00 PM
elif (
    now_ph.hour > 14
    or (now_ph.hour == 14 and now_ph.minute >= 35)
):
    channel_url = gma_url
    shutdown_hour = 20
    shutdown_minute = 0
    print("📺 GMA selected | Shutdown at 8:00 PM")

else:
    print("⏳ Outside streaming window.")

# --------------------------------------------------
# Step 1: Open channel
# --------------------------------------------------

driver.get(channel_url if channel_url else tv5_url)
time.sleep(6)

try:
    # --------------------------------------------------
    # Step 2: Click LIVE video
    # --------------------------------------------------
    live_badge = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'LIVE')]"))
    )
    video_link = live_badge.find_element(By.XPATH, "../../../../..")
    video_link.click()
    print("✅ Livestream clicked")

    # --------------------------------------------------
    # Step 3: Wait for player
    # --------------------------------------------------
    player_xpath = "//div[@id='movie_player']"
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, player_xpath))
    )
    print("🎬 Player loaded")

    # --------------------------------------------------
        # --- Step 4: Close chat before fullscreen ---
    try:
        chat_iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@id='chatframe']"))
        )
        driver.switch_to.frame(chat_iframe)
        print("💬 Chat iframe found, closing chat...")
        time.sleep(5)

        close_chat_xpath = (
            "//yt-live-chat-header-renderer"
            "//button[@aria-label='Close']"
        )

        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, close_chat_xpath))
        )
        close_button.click()
        print("✅ Chat closed successfully.")

        driver.switch_to.default_content()

    except Exception as chat_error:
        print("⚠️ Chat close failed, hiding via JS fallback.")
        driver.switch_to.default_content()
        driver.execute_script(
            "let chat=document.querySelector('#chat,#chatframe');"
            "if(chat){chat.style.display='none';}"
        )
        print("✅ Chat iframe hidden via JS fallback.")


    # --------------------------------------------------
    # Step 5: Fullscreen
    # --------------------------------------------------
    player = driver.find_element(By.XPATH, player_xpath)
    player.send_keys("f")
    print("🖥️ Fullscreen enabled")

except Exception as e:
    print("⚠️ Failed to start livestream:", e)

# --------------------------------------------------
# Step 6: Shutdown at 2:30 PM PH time
# --------------------------------------------------

print(f"⏰ Waiting for shutdown at {shutdown_hour:02d}:{shutdown_minute:02d} PH time")

try:
    while True:
        if len(driver.window_handles) == 0:
            print("⚠️ Browser closed. Exiting.")
            break

        now_ph = datetime.now(philippines_tz)
        print(f"⏰ PH Time: {now_ph.strftime('%I:%M:%S %p')}", end="\r")

        if (
            now_ph.hour == shutdown_hour
            and now_ph.minute == shutdown_minute
        ):
            print("\n🛑 Shutdown time reached")

            driver.quit()
            # os.system("sudo shutdown now")
            print("🧪 TEST MODE: Shutdown command skipped")
            break

        time.sleep(10)

except Exception as e:
    print("⚠️ Runtime error:", e)

finally:
    try:
        driver.quit()
    except:
        pass
