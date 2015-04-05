import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url = 'https://www.google.com/flights/#search;f=SFO;t=CUN;d=2015-05-10;r=2015-05-11;ti=,l1200-2200'

driver = webdriver.Chrome('/Applications/chromedriver')
driver.get(url)

time.sleep(2)

best_flights = driver.find_elements_by_css_selector(".PNIT24B-c-Qb")
for flight in best_flights:
  infos = flight.text.split("\n")
  print infos  
driver.close()
