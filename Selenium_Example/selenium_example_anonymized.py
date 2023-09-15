from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time


def devsleep(t):
    time.sleep(t)


def navigateToGrafana(driver):
    driver.get("")
    time.sleep(1)
    secondary_button = driver.find_element(
        By.XPATH, '//*[@id="details-button"]')
    secondary_button.send_keys(Keys.ENTER)
    time.sleep(1)
    proceed_link = driver.find_element(By.XPATH, '//*[@id="proceed-link"]')
    proceed_link.send_keys(Keys.ENTER)
    return proceed_link


def login(driver):

    print(driver)
    username = driver.find_element(
        By.XPATH, '//*[@id="reactRoot"]/div/main/div[3]/div/div[2]/div/div/form/div[1]/div[2]/div/div/input')
    username.send_keys('')
    password = driver.find_element(By.XPATH, '//*[@id="current-password"]')
    password.send_keys('')
    enter = driver.find_element(
        By.XPATH, '//*[@id="reactRoot"]/div/main/div[3]/div/div[2]/div/div/form/button')
    enter.send_keys(Keys.ENTER)


def grabfailedssh(driver):
    time.sleep(3)
    driver.get(
        "https://54.80.162.111/d/ir7x3Zq7z/default?orgId=1&viewPanel=3&from=now-7d&to=now")
    time.sleep(10)
    try:
        nofail = driver.find_element(
            By.XPATH, '/html/body/div[1]/div/main/div[3]/div/div/div[1]/div/div/div[1]/div/div/div[7]/div/section/div[2]/div/div')
        nofailtext = nofail.text
        return nofailtext
    except:
        fail = driver.find_element(
            By.XPATH, '/html/body/div[1]/div/main/div[3]/div/div/div[1]/div/div/div[1]/div/div/div[7]/div/section/div[2]/div/div[1]/div/table')
        failtext = fail.text

        return failtext.to_list()


def dataframe(text):
    df = pd.DataFrame(text)


def main():
    driver = webdriver.Chrome(
        executable_path=".\chrome_driver\chromedriver.exe")
    driver.implicitly_wait(0.5)
    navigateToGrafana(driver)
    login(driver)
    text = grabfailedssh(driver)
    text_file = open("Output.txt", "w")
    text_file.write(text)
    text_file.close()
    devsleep(3000)


main()


# def navigateGrafana(driver):
#     time.sleep(3)
#     browse = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div[3]/div/div/div[1]/div/div/div[1]/div/div/div[3]/div/section/div[2]/div/div[1]/div[1]/ul/li/div/div/a')
#     # //*[@id="react-aria3339806887-7"]
#     # /html/body/div[1]/div/nav/ul[2]/li[2]/div/a
#     time.sleep(1)
#     browse.click()
#     #time.sleep(6)
#     # failedssh = driver.find_element(By.XPATH, '')
#     # failedssh.click()
#     # time.sleep(0.5)
#     # browse.click()
#     # time.sleep(1)
#     # browse.send_keys(Keys.ARROW_RIGHT)
#     # browse.send_keys(Keys.ARROW_DOWN)
#     # action = ActionChains(browse)
#     # action.send_keys(Keys.ARROW_RIGHT)
#     # action.pause(0.5)
#     # action.send_keys(Keys.ARROW_DOWN)
#     # action.pause(0.5)
#     # action.send_keys(Keys.ARROW_DOWN)
#     # action.pause(0.5)
#     # action.send_keys(Keys.ENTER)
#     #action.perform()
