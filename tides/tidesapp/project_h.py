#!/bin/env python3

from enum import Enum
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep


class PriceTables(Enum):
    EUA, UKA = range(2)


def main_app(price_table):

    # XPATHs..
    URL = r'https://ember-climate.org/data/data-tools/carbon-price-viewer/'
    iframe_xpath = r'//iframe[contains(@src,"anvil.app")]'
    if price_table == PriceTables.EUA:
        button_xpath = r'(//button[contains(@class,"btn-default")]/descendant::span[@class="button-text"])[1]'
    elif price_table == PriceTables.UKA:
        button_xpath = r'(//button[contains(@class,"btn-default")]/descendant::span[@class="button-text"])[2]'

    # Browser activity..
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 30)
    driver.get(URL)
    iframe = driver.find_element(By.XPATH, iframe_xpath)
    driver.switch_to.frame(iframe)
    button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    button.click()
    sleep(5)
    driver.close()

if __name__ == '__main__':
    main_app(PriceTables.EUA)
    main_app(PriceTables.UKA)

