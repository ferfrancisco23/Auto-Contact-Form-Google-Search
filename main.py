from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup as bs4
from random import randint
from time import sleep
import requests
import os

min_seconds = 12
max_seconds = 32
site_link_list = []
request_headers = {
    "Accept-Language":"en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39"
}


# Ask user for a list of links (temporary)
user_input = input("Enter all site links:")

while user_input != '':
    site_link_list.append(user_input)
    user_input = input()
########################################

try:
    service = ChromeService(executable_path=ChromeDriverManager().install())
except ValueError:
    service = ChromeService(executable_path=ChromeDriverManager(version='114.0.5735.90').install())

driver = webdriver.Chrome(service=service)
driver.get("http://trieste.io")
driver.get_log("browser")
driver.implicitly_wait(60)

# Login to Trieste
trieste_username = driver.find_element(By.ID, "user_email")
trieste_password = driver.find_element(By.ID, "user_password")
login_submit_button = driver.find_element(By.NAME, "commit")

trieste_username.send_keys(os.environ.get("TRIESTE_USERNAME"))
sleep(1)
trieste_password.send_keys(os.environ.get("TRIESTE_PASSWORD"))
sleep(2)
login_submit_button.click()
###########################################

# Iterate through SL list and process each lead one by one
for site_link in site_link_list:
    #
    sleep(randint(min_seconds, max_seconds))
    driver.get(site_link)
    lead_url = driver.find_element(By.ID, "site_link_from_url").get_attribute("value")
    google_url = f"https://www.google.com/search?q=site:{lead_url}%20%22/contact%22%20&pws=0&num=100"

    try:
        driver.get(lead_url)
    except:
        print(f"{lead_url} site down \nSL: {site_link}")

    # Get google search result parsed html
    sleep(randint(min_seconds, max_seconds))
    google_request = requests.get(google_url, headers=request_headers)
    google_request.raise_for_status()
    google_results_soup = bs4(google_request.text, "lxml")
    try:
        contact_page = google_results_soup.find('div', class_="yuRUbf").a.get('href')
    except AttributeError:
        driver.get(site_link)
        pass
    else:
        # Add note to SL and click submit
        driver.get(site_link)
        sleep(3)
        add_a_note = driver.find_element(By.LINK_TEXT, "Add a Note")
        add_a_note.click()

        note_textbox = driver.find_element(By.ID, "note_body")
        note_textbox.send_keys(contact_page)
        sleep(randint(min_seconds, max_seconds))
        submit_note = driver.find_element(By.XPATH, '//*[@id="create_note_form"]/input[2]')
        submit_note.click()

        # Change site link status to "Guest post paid"
        sl_type = Select(driver.find_element(By.XPATH, '//*[@id="site_link_link_type_event"]'))
        sl_type.select_by_visible_text("Guest Post Paid")
        update_button = driver.find_element(By.XPATH, '//*[@id="site_link_form"]/input[1]')
        update_button.click()

        # Write processed site links onto text file
        with open("for_initial_email.txt", "a") as initial_email_file:
            initial_email_file.write(f"{site_link}\n")


input("continue?")