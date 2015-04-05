import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url_template = 'https://www.google.com/flights/#search;f={origin};t={destination};d={depart_date};r={return_date};ti=t{depart_times},l{arrival_times}'

def generate_weekend_dates(num_weeks):
  weekend_dates = []
  nearest_friday = datetime.date.today() + datetime.timedelta( (4-datetime.date.today().weekday()) %7)
  for i in xrange(num_weeks):
    friday = nearest_friday + datetime.timedelta(i*7)
    sunday = friday + datetime.timedelta(2)
    weekend_dates.append([
      str(friday.year)+"-"+str('{:02d}'.format(friday.month))+"-"+str('{:02d}'.format(friday.day)),
      str(sunday.year)+"-"+str('{:02d}'.format(sunday.month))+"-"+str('{:02d}'.format(sunday.day))
      ])
  return weekend_dates

destinations = ["AUS", "PDX", "CUN"]
weekend_dates = generate_weekend_dates(24)
#weekend_dates = [["2015-08-21","2015-08-23"]]
#destinations = ["AUS"]
#weekend_dates = generate_weekend_dates(1)

for d in destinations:
  for weekend in weekend_dates:
    url = url_template.format(
      origin="SFO",
      destination=d,
      depart_date=weekend[0],
      return_date=weekend[1],
      depart_times="1900-2400",
      arrival_times="1200-2200")
    print url
    driver = webdriver.Chrome('/Applications/chromedriver')
    driver.get(url)

    time.sleep(2)

    best_flights = driver.find_elements_by_css_selector(".PNIT24B-c-Qb")
    if len(best_flights) == 0:
      best_flights = driver.find_elements_by_css_selector(".PNIT24B-c-H")
    if len(best_flights) == 0:
     best_flight = ['no results']
    else:
      flights_by_price = {}
      prices = []
      for flight in best_flights:
        infos = flight.text.split("\n")
        if not "more expensive" in infos[0]:
          price = int(infos[0][1:])
          flights_by_price[price] = infos
          prices.append(price)
      best_flight = flights_by_price[min(prices)]

    print best_flight
    driver.close()

