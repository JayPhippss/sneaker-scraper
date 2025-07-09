from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import json

def setup_driver(headless=True):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--window-size=1280,1024')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def safe_find(driver, by, value, attr=None):
    try:
        el = driver.find_element(by, value)
        return el.get_attribute(attr) if attr else el.text.strip()
    except:
        return ""

def scrape_sneakers():
    driver = setup_driver(headless=True)
    wait = WebDriverWait(driver, 10)
    base_url = "https://www.soleretriever.com/sneaker-release-dates"
    page = 1
    all_sneakers = []

    while True:
        list_url = f"{base_url}?page={page}"
        print(f"🔗 Opening list page {page}: {list_url}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        driver.get(list_url)
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-test-id="raffle-item"]')))
        except:
            print(f"No cards on page {page}. Ending.")
            break
        time.sleep(2)

        # Extract detail URLs
        cards = driver.find_elements(By.CSS_SELECTOR, '[data-test-id="raffle-item"]')
        detail_urls = []
        for card in cards:
            try:
                a = card.find_element(By.TAG_NAME, 'a')
                href = a.get_attribute('href')
                if href:
                    detail_urls.append(href)
            except:
                continue

        print(f"🗂 Found {len(detail_urls)} detail URLs on page {page}")

        for idx, detail_url in enumerate(detail_urls):
            try:
                print(f"  🚀 Navigating to detail {idx+1}/{len(detail_urls)}: {detail_url}")
                driver.get(detail_url)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.rounded-md.border.border-gray-200.bg-white.text-gray-950')))
                time.sleep(1.5)

                title = safe_find(driver, By.XPATH, "//div[contains(@class, 'text-pretty')]")
                release_date = safe_find(driver, By.TAG_NAME, "time", attr="datetime")
                formatted_date = safe_find(driver, By.TAG_NAME, "time")
                is_date_complete = len(release_date) == 10
                sku = safe_find(driver, By.XPATH, "//div[contains(text(), 'SKU')]/following-sibling::div")
                colorway = safe_find(driver, By.XPATH, "//div[contains(@class, 'text-right') and contains(text(), '/')]")
                retail_price = safe_find(driver, By.XPATH, "//div[contains(@class, 'text-sm font-medium') and contains(text(), '$')]")
                live_price = safe_find(driver, By.XPATH, "//span[contains(@class, 'text-turquoise-500') and contains(@class, 'cursor-pointer')]")
                purchase_link = safe_find(driver, By.XPATH, "//a[contains(@class, 'leading-none') and contains(@href, 'http')]", attr="href")

                # Gather images
                image_urls = []
                slides = driver.find_elements(By.CLASS_NAME, "embla__slide")
                for slide in slides:
                    try:
                        img = slide.find_element(By.TAG_NAME, "img")
                        src = img.get_attribute("src")
                        if src:
                            image_urls.append(src)
                    except:
                        pass

                sneaker = {
                    "title": title,
                    "release_date": release_date if is_date_complete else "",
                    "formatted_date": formatted_date,
                    "is_date_complete": is_date_complete,
                    "price": retail_price,
                    "sku": sku,
                    "colorway": colorway,
                    "live_price": live_price,
                    "purchase_link": purchase_link,
                    "images": image_urls
                }
                all_sneakers.append(sneaker)
                print(f"    ✅ Parsed: {title}")

            except Exception as e:
                print(f"    ❌ Failed detail {idx+1}: {e}")
                continue

        page += 1

    driver.quit()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sneakers_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_sneakers, f, indent=2, ensure_ascii=False)
    print(f"🎉 Done! Total scraped: {len(all_sneakers)}. Saved to {filename}")

if __name__ == "__main__":
    scrape_sneakers()
