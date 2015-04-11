#!/usr/bin/env python
import datetime
import time
import MySQLdb
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url_template = 'https://www.google.com/flights/#search;f={origin};t={destination};d={depart_date};r={return_date};s=0;ti=t{depart_times},l{arrival_times}'

def execute_sql(sql):
  try:
    cursor.execute(sql)
    db.commit()
    print 'db execute success'
  except MySQLdb.Error as e:
    db.rollback()
    print 'db execute error'
    print e

# Choose lowest price.
def get_price(price):
  price = unicodedata.normalize('NFKD', price).encode('ascii','ignore')
  infos_parts = price.split('$')
  price = '$' + infos_parts[1]
  return price

def generate_weekend_dates(num_weeks):
  weekend_dates = []
  nearest_friday = datetime.date.today() + datetime.timedelta( (4-datetime.date.today().weekday()) %7)
  for i in xrange(num_weeks):
    friday = nearest_friday + datetime.timedelta(i*7)
    sunday = friday + datetime.timedelta(2)
    weekend_dates.append([
      str(friday.year)+'-'+str('{:02d}'.format(friday.month))+'-'+str('{:02d}'.format(friday.day)),
      str(sunday.year)+'-'+str('{:02d}'.format(sunday.month))+'-'+str('{:02d}'.format(sunday.day))
      ])
  return weekend_dates

destinations = ['AUS', 'PDX', 'YVR', 'LAS', 'SAN', 'PHX', 'SLC', 'SEA', 'LAX']
weekend_dates = generate_weekend_dates(24)
# 2 similar flights
#destinations = ['SAN']
#weekend_dates = [['2015-05-29','2015-05-31']]

# Excess round trip
#destinations = ['LAS']
#weekend_dates = [['2015-10-30','2015-11-01']]
# Missing back operator
#destinations = ['AUS']
#weekend_dates = [['2015-06-12','2015-06-14']]
# No flights
#weekend_dates = [['2015-08-21','2015-08-23']]
#destinations = ['AUS']
# Southwest
#weekend_dates = [['2015-04-24','2015-04-26']]
#destinations = ['PHX']
# Expansion past fold
#weekend_dates = [['2015-08-21','2015-08-23']]
#destinations = ['SEA']

db = MySQLdb.connect('173.194.80.20','root','roos','weekendfares')
cursor=db.cursor()

driver = webdriver.Chrome('/Applications/chromedriver')
#driver.implicitly_wait(1)

def find_best_flights():
  # Find the set of best flights. Try the Best flights module.
  best_flights = driver.find_elements_by_css_selector('.PNIT24B-c-Nb')

  # If there isn't a Best flights module, use the regular list.
  if len(best_flights) == 0:
    best_flights = driver.find_elements_by_css_selector('.PNIT24B-c-G')

  # Keep going if there are no flights returned at all.
  if len(best_flights) == 0:
   best_flights = []

  time.sleep(0.1)
  return best_flights

expanded_count = 0
def expand_similar_flight():
  best_flights = find_best_flights()
  print "BEST FLIGHTS: ", best_flights

  skipped_flights = 0
  for flight in best_flights:
    try:
      infos = flight.text.split('\n')
    except:
      infos = flight.text.split('\n')

    print "EXPAND INFOS: ", infos

    # Skip lines saying "Show more expensive and longer flights."
    if len(infos) < 3:
      continue
    depart_times = infos[2]

    if 'similar flights' in depart_times:
      # if less flights have been skipped than expanded flights, skip
      global expanded_count
      if skipped_flights < expanded_count:
        skipped_flights += 1
      else:
        expanded_count += 1
        driver.execute_script("var elms = document.getElementsByClassName('tooltipContent'); for (var i=0;i<elms.length;i++) {elms[i].style.display = 'none' }");
        flight.click()
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        return False
  return True


for d in destinations:
  for weekend in weekend_dates:

    check_date = datetime.date.today().isoformat()

    # Skip if already in Cloud SQL.

    #select_sql="""SELECT * FROM fares WHERE check_date = '%s' and there_date = '%s' and destination_airport = '%s'""" % (check_date, weekend[0], d)
    #execute_sql(select_sql)
    #sql_result = cursor.fetchone()
    #if sql_result is not None:
    #  continue
    #################################

    url = url_template.format(
      origin='SFO',
      destination=d,
      depart_date=weekend[0],
      return_date=weekend[1],
      depart_times='2000-2400',
      arrival_times='1600-2200')

    print url

    # Load page.
    driver.get(url)

    def get_best_flight():
      page_loaded = False
      while not page_loaded:
        time.sleep(0.2)
        outbound_elem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.PNIT24B-Fb-e')))
        outbound_is_hidden = outbound_elem.get_attribute('aria-hidden')

        no_flights_elem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.PNIT24B-Ob-a')))
        no_flights_is_hidden = no_flights_elem.get_attribute('aria-hidden')

        load_elem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.PNIT24B-e-q')))
        loader_is_hidden = load_elem.get_attribute('aria-hidden')

        if (not outbound_is_hidden or not no_flights_is_hidden) and loader_is_hidden:
          page_loaded = True

      global expanded_count
      expanded_count = 0
      no_more_similar_flights = False
      # Find set of best flights.
      best_flights = find_best_flights()
      print "GETBEST best_flights: ", best_flights

      # If flights were returned...
      if len(best_flights) > 0:

        # expand the similar flights
        expanded_count = 0
        while no_more_similar_flights == False:
          no_more_similar_flights = expand_similar_flight()

        # find lowest price
        flights_by_price = {}
        prices = []
        best_flights = find_best_flights()
        last_price = -1
        for flight in best_flights:
          infos = flight.text.split('\n')
          try:
            infos.remove('')
            infos.remove('')
            infos.remove('')
          except:
            pass
          print "Previous infos: ", infos
          if '$' in infos[0]:
            price = get_price(infos[0])
            #print "d: ", price
            infos[0] = price
            #print "Price: ", price
            last_price = price
          elif last_price != -1:
            infos = [last_price] + infos
          else:
            continue

          # Delete any 'round trip' text.
          if 'round' in infos[1]:
            del infos[1]

          # Delete layover info. We just want price, time, operator, length, stops.
          infos = infos[:5]
          print "Amended infos: ", infos

          price = int(infos[0][1:].replace(',', ''))

          # Add to candidate set if not a similar flights item.
          if price not in flights_by_price and 'similar' not in infos[1] and 'similar' not in infos[2]:
            flights_by_price[price] = [infos, flight]
            print "appended price: ", price
            prices.append(price)

        # bfi is short for best_flight_info
        if len(prices) > 0:
          bfi = flights_by_price[min(prices)][0]
          best_flight_element = flights_by_price[min(prices)][1]
          return [bfi, best_flight_element]
      return [0, 0]

    # If there are flights...
    there_bfi, there_bfe = get_best_flight()
    if there_bfi:
      print "there BFI: ", there_bfi

      # Select first best flight.
      there_bfe.click()
      time.sleep(2)

      back_bfi, back_bfe = get_best_flight()
      print "back BFI: ", back_bfi
      bfi = [check_date, weekend[0], weekend[1], d] + there_bfi + back_bfi
      print "BFI: ", bfi


      # Select return best flight.
      try:
        back_bfe.click()
      except:
        time.sleep(1)
        back_bfe.click()
      time.sleep(1)

      # Collect book url
      book_url = driver.current_url
    # If not flights...
    else:
      bfi = [check_date, weekend[0], weekend[1], d] + ['n/a'] * 10
      book_url = 'n/a'

    delete_sql="""DELETE FROM fares WHERE check_date = '%s' and there_date = '%s' and destination_airport = '%s'""" % (bfi[0], bfi[1], bfi[3])

    execute_sql(delete_sql)

    insert_sql="""INSERT INTO fares (check_date, there_date, back_date, destination_airport, price, there_times, there_operator, there_time, there_stops, back_times, back_operator, back_time, back_stops, book_url) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (bfi[0], bfi[1], bfi[2], bfi[3], bfi[9], bfi[5], bfi[6], bfi[7], bfi[8], bfi[10], bfi[11], bfi[12], bfi[13], book_url)

    print insert_sql.encode('utf8')

    execute_sql(insert_sql)

db.close()
driver.close()


