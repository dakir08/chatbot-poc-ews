import json
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.sync_api import sync_playwright
from utils.utils import normalize_spaces, append_to_json_file


class WebCrawler:

    def get_internal_links(self, url):
        internal_links = set()
        domain_name = urlparse(url).netloc

        try:
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                for link in soup.find_all('a', href=True):
                    absolute_link = urljoin(url, link['href'])
                    if urlparse(absolute_link).netloc == domain_name:
                        if not any(absolute_link.endswith(ext) for ext in [".pdf", ".jpg", ".jpeg", ".png", ".gif"]):  # Filtering out file links
                            internal_links.add(absolute_link)
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
        return list(internal_links)
    
    def get_localization_links(self, url):
        localization_paths = set()
        all_links = self.get_internal_links(url)

        # Regular expression to match localization patterns in URLs
        # This pattern should be adjusted based on the specific format of localization paths
        localization_pattern = re.compile(r'(/[a-z]{2}/[a-z]{2}/|/[a-z]{2}/)')

        for link in all_links:
            match = localization_pattern.search(link)
            if match:
                # Construct URL with base and localization path
                localization_url = f"{url.rstrip('/')}{match.group()}"
                localization_paths.add(localization_url)

        return list(localization_paths)
    

    def selenium_test(self, url):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless=new")

        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            driver.get(url)
            
            # elem = WebDriverWait(driver, 5).until(
            # EC.presence_of_element_located((By.ID, "content"))
            # )

            content = driver.find_element(By.ID, 'content')
            print("PRINT PAGE SOURCE")
            f = open("page_source.txt", "w")
            f.write(driver.page_source)
            f.close()
        finally:
            driver.quit()
            
    def playwright_crawl_clubs(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=200)
            page = browser.new_page()
            page.goto("https://www.fitnessfirst.com/my/en/clubs")

            # Title
            title = page.query_selector("span.heading-1").text_content()
            contents = []

            # Finding the 'Find Our Club' section
            find_our_club_section = page.query_selector('div.rte-wrapper').text_content()
            contents.append(find_our_club_section.strip())

            # Finding the 'Recommended Club' section
            recommended_club = page.query_selector("aside.club-emblem-badge").text_content()
            contents.append(recommended_club.strip())

            # # Finding the list of gym clubs
            gym_clubs = page.query_selector_all('div.d-flex.flex-column.h-100.p-10p.p-lg-20p')
            gym_clubs_texts = []
            for club in gym_clubs:
                gym_clubs_texts.append(club.text_content())
                contents.append(club.text_content().strip())

            page.locator("button.btn.btn-gray.page-link").nth(1).click()
            page.wait_for_timeout(1000)

            gym_clubs = page.query_selector_all('div.d-flex.flex-column.h-100.p-10p.p-lg-20p')
            gym_clubs_texts = []
            for club in gym_clubs:
                gym_clubs_texts.append(club.text_content())
                contents.append(club.text_content().strip())

            data = {
                "url": "https://www.fitnessfirst.com/my/en/clubs",
                "title":title,
                "content": normalize_spaces(contents),
            }

            append_to_json_file("./preprocessor/data/crawlData.json", data)

    def playwright_crawl_personal_training(self):
        url = "https://www.fitnessfirst.com/my/en/personal-training"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=200)
            page = browser.new_page()
            page.goto(url)

            contents = []
            # Title
            title = page.query_selector("span.heading-1").text_content()

            # Get the certified and qualified coaches section
            sections = page.query_selector_all("div.container.my-60p.my-lg-70p")

            for section in sections:
                contents.append(section.text_content().strip())

            # Get the key pillars
            key_pillar_title = page.query_selector("div.rte-wrapper.display-l.text-white.text-center.text-xl-start").text_content()
            key_pillar = page.query_selector("div.row.justify-content-xl-end").text_content()

            contents.append(key_pillar_title.strip())
            contents.append(key_pillar.strip())

            # Get fitness journey
            fitness_journey_title = page.query_selector("h2.fs-32p.fs-lg-48p.display-l.text-center.text-lg-start.text-white.text-uppercase").text_content()

            contents.append(fitness_journey_title.strip())

            fitness_journeys = page.query_selector_all("div.personal-training-timeline-content-wrapper")

            for section in fitness_journeys:
                contents.append(section.text_content().strip())

            data = {
                "url": "https://www.fitnessfirst.com/my/en/personal-training",
                "title": title,
                "content": normalize_spaces(contents),
            }

            append_to_json_file("./preprocessor/data/crawlData.json", data)

    def playwright_crawl_classes(self):
        url = "https://www.fitnessfirst.com/my/en/classes"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=200)
            page = browser.new_page()
            page.goto(url)

            contents = []
            # Title
            title = page.query_selector("span.heading-1").text_content()

            # Sections
            sections = page.query_selector_all("div.d-lg-flex.flex-lg-column.h-100")

            for section in sections:
                contents.append(section.text_content().strip())

            # classes
            classes_title = page.query_selector("h2.fs-32p.fs-lg-48p.text-uppercase")

            contents.append(classes_title.text_content().strip())

            next_button = page.locator("button.btn.btn-gray.page-link").nth(1)

            continue_crawl_class = True

            while continue_crawl_class:
                classes = page.query_selector_all("div.d-flex.justify-content-between.gap-2")

                for singleclass in classes:
                    workout = singleclass.query_selector("p.d-none.d-lg-inline-block.fs-14p.fs-lg-16p.mb-4p")
                    workout_type = singleclass.query_selector("a.text-reset.text-uppercase.text-decoration-none.stretched-link")
                    workout_text = f"{workout.text_content().strip()}: {workout_type.text_content().strip()}"
                    contents.append(workout_text)



                if next_button.is_disabled() is False:
                    page.locator("button.btn.btn-gray.page-link").nth(1).click()
                    page.wait_for_timeout(1000)
                else:
                    continue_crawl_class = False
        
            data = {
                "url": url,
                "title": title,
                "content": normalize_spaces(contents),
            }

            append_to_json_file("./preprocessor/data/crawlData.json", data)

    def playwright_crawl(self):
        print("crawling clubs")
        self.playwright_crawl_clubs()
        print("crawling personal training")
        self.playwright_crawl_personal_training()
        print("crawling classes")
        self.playwright_crawl_classes()