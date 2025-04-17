import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os

st.set_page_config(page_title="Twitter Comment Scraper", layout="centered")
st.title("🧹 Twitter Comment Scraper")

username = st.text_input("Twitter Username or Email")
password = st.text_input("Twitter Password", type="password")
tweet_links = st.text_area("Paste Tweet URLs (comma-separated)")
run = st.button("Scrape Replies")

if run and username and password and tweet_links:
    st.write("Launching Chrome browser...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://x.com/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
        driver.find_element(By.NAME, "text").send_keys(username, Keys.RETURN)

        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        driver.find_element(By.NAME, "password").send_keys(password, Keys.RETURN)

        time.sleep(5)

        urls = [url.strip() for url in tweet_links.split(",") if url.strip()]
        rows = []

        for url in urls:
            st.write(f"Scraping: {url}")
            driver.get(url)
            time.sleep(5)

            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            replies = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')

            for reply in replies:
                try:
                    text = reply.text.strip().replace('\n', ' ')
                    rows.append([url, text])
                except:
                    continue

        csv_file = "twitter_replies.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tweet URL", "Reply Text"])
            writer.writerows(rows)

        with open(csv_file, "rb") as f:
            st.download_button("📥 Download CSV", f, file_name="twitter_replies.csv", mime="text/csv")

        os.remove(csv_file)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

    finally:
        driver.quit()
