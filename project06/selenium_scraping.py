from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

def scrape_ign_pc_news(output_filename):
    url = 'https://pl.ign.com/'

    options = Options()
    options.add_argument("--disable-extensions")

    service = Service('./webdriver/chromedriver.exe')

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)

        try:
            decline_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#qc-cmp2-ui > div.qc-cmp2-footer.qc-cmp2-footer-overlay.qc-cmp2-footer-scrolled > div > button:nth-child(2)"))
            )
            decline_button.click()
            print("Declined cookies.")
        except Exception as e:
            print(f"No cookies pop-up found or error clicking decline button: {e}")

        try:
            pc_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.sidebar-section:nth-child(1) > li:nth-child(4) > a:nth-child(1)"))
            )
            pc_button.click()
            print("Navigated to PC section.")
        except Exception as e:
            print(f"Error clicking PC section: {e}")


        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        print("Finished scrolling.")

        time.sleep(5)
        # Extract news articles
        news_data = []
        
        articles_sections = driver.find_elements(By.CSS_SELECTOR, 'section.broll')
        nested_articles = [articles_section.find_elements(By.CSS_SELECTOR, 'div:nth-child(3) > article') for articles_section in articles_sections]
        articles = [x for xs in nested_articles for x in xs]
        for article in articles:
            try:
                title = article.find_element(By.CSS_SELECTOR, "div:nth-child(2) > h3:nth-child(2) > a:nth-child(1) > span:nth-child(1)").text
                link = article.find_element(By.CSS_SELECTOR, "div:nth-child(2) > h3:nth-child(2) > a").get_attribute('href')
                desc = article.find_element(By.CSS_SELECTOR, "div:nth-child(2) > p:nth-child(3)").text

                news_data.append({'title': title,
                              'desc': desc,
                              'link':link})
            except Exception as e:
                print(f"Error extracting article data: {e}")

        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=4)

        print(f"Scraped data saved to {output_filename}")

    finally:
        driver.quit()

if __name__ == "__main__":

    output_filename = "./project06/ign_pc_news.json"
    scrape_ign_pc_news(output_filename)
