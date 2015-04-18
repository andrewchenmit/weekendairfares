import datetime
import time
import MySQLdb
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AirfareScraper:
  def __init__(self, config, overwrite):
    # Set unconfigurables.
    self.driver = webdriver.Firefox()
    self.origin = 'SFO,SJC'
    self.db = MySQLdb.connect('173.194.80.20','root','roos','weekendfares')
    self.cursor = self.db.cursor()
    self.url_template = 'https://www.google.com/flights/#search;f={origin};t={destination};d={depart_date};r={return_date};s=0;ti=t{depart_times},l{arrival_times}'
    self.check_date = datetime.date.today().isoformat()
    self.expanded_count = 0

    # Set configurables.
    self.dests = config.dests
    self.date_pairs = config.date_pairs
    self.depart_times = config.depart_times
    self.arrival_times = config.arrival_times
    self.outbound_depart_period = config.outbound_depart_period
    self.return_arrival_period = config.return_arrival_period
    self.sql_table = config.sql_table
    self.overwrite = overwrite

  # execute_sql: Execute SQL against Cloud SQL database.
  def execute_sql(self, sql):
    try:
      self.cursor.execute(sql)
      self.db.commit()
      print 'db execute success'
    except MySQLdb.Error as e:
      self.db.rollback()
      print 'db execute error'
      print e

  # in_cloudSQL: Check if pending scrape is already in Cloud SQL.
  def in_cloudSQL(self, check_date, there_date, back_date, outbound_depart_period, return_arrival_period, destination_airport):
    select_sql="""SELECT * FROM fares WHERE check_date = '%s' and there_date = '%s' and back_date = '%s' and there_period = '%s' and back_period = '%s' and destination_airport = '%s'""" % (check_date, there_date, back_date, outbound_depart_period, return_arrival_period, destination_airport)
    self.execute_sql(select_sql)
    return self.cursor.fetchone()

  # find_best_flights: Scrape current page for flights data of best flights.
  def find_best_flights(self):
    # Find the set of best flights. Try the Best flights module.
    best_flights = self.driver.find_elements_by_css_selector('.PNIT24B-c-Nb')

    # If there isn't a Best flights module, use the regular list.
    if len(best_flights) == 0:
      best_flights = self.driver.find_elements_by_css_selector('.PNIT24B-c-G')

    # Keep going if there are no flights returned at all.
    if len(best_flights) == 0:
     best_flights = []

    time.sleep(0.1)
    return best_flights

  # expand_similar_flight: Expand all the collapsed flights.
  def expand_similar_flight(self):
    skipped_flights = 0

    best_flights = self.find_best_flights()
    print "BEST FLIGHTS: ", best_flights

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
        if skipped_flights < self.expanded_count:
          skipped_flights += 1
        else:
          self.expanded_count += 1
          self.driver.execute_script("var elms = document.getElementsByClassName('tooltipContent'); for (var i=0;i<elms.length;i++) {elms[i].style.display = 'none' }");
          flight.click()
          time.sleep(2)
          self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
          return False
    return True

  # get_price: Choose lowest price.
  def get_price(self, price):
    price = unicodedata.normalize('NFKD', price).encode('ascii','ignore')
    infos_parts = price.split('$')
    price = '$' + infos_parts[1]
    return price

  # get_best_flight: Get the details for the best flight on the page.
  def get_best_flight(self):
    no_more_similar_flights = False

    # Wait until flight data is loaded.
    page_loaded = False
    while not page_loaded:
      time.sleep(0.2)

      outbound_elem = WebDriverWait(self.driver, 5).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, '.PNIT24B-Fb-e')))
      outbound_is_hidden = outbound_elem.get_attribute('aria-hidden')

      no_flights_elem = WebDriverWait(self.driver, 5).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, '.PNIT24B-Ob-a')))
      no_flights_is_hidden = no_flights_elem.get_attribute('aria-hidden')

      load_elem = WebDriverWait(self.driver, 5).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, '.PNIT24B-e-q')))
      loader_is_hidden = load_elem.get_attribute('aria-hidden')

      if (not outbound_is_hidden or not no_flights_is_hidden) and loader_is_hidden:
        page_loaded = True

    # Find set of best flights.
    best_flights = self.find_best_flights()
    print "GETBEST best_flights: ", best_flights

    # If flights were returned...
    if len(best_flights) > 0:

      # Expand the similar flights.
      self.expanded_count = 0
      while no_more_similar_flights == False:
        no_more_similar_flights = self.expand_similar_flight()

      # Find lowest price.
      flights_by_price = {}
      prices = []
      best_flights = self.find_best_flights()
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
          price = self.get_price(infos[0])
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

      if len(prices) > 0:
        bfi = flights_by_price[min(prices)][0]
        best_flight_element = flights_by_price[min(prices)][1]
        return [bfi, best_flight_element]
    return [0, 0]

  def scrape(self):
    for d in self.dests:
      for date_pair in self.date_pairs:

        # Skip if configured to skip fares already in Cloud SQL.
        if not self.overwrite:
          if self.in_cloudSQL(self.check_date, date_pair[0], date_pair[1], self.outbound_depart_period, self.return_arrival_period, d) is not None:
            continue

        # Load page.
        url = self.url_template.format(
            origin = self.origin,
            destination = d,
            depart_date = date_pair[0],
            return_date = date_pair[1],
            depart_times = self.depart_times,
            arrival_times = self.arrival_times)
        print url
        self.driver.get(url)

        # Scrape for the best roundtrip flight.
        bfi_prefix = [self.check_date, date_pair[0], date_pair[1], d]
        bfi_suffix = [1]
        # If there are flights...
        there_bfi, there_bfe = self.get_best_flight()
        if there_bfi:
          print "there BFI: ", there_bfi

          # Select first best flight.
          there_bfe.click()
          time.sleep(2)

          back_bfi, back_bfe = self.get_best_flight()
          print "back BFI: ", back_bfi

          # Select return best flight.
          back_bfe.click()
          time.sleep(2)

          # Collect book url
          book_url = self.driver.current_url


        # If there are no flights...
        else:
          there_bfi = ['n/a'] * 5
          back_bfi = ['n/a'] * 5
          book_url = 'n/a'

        bfi = bfi_prefix + there_bfi + back_bfi + [book_url] + bfi_suffix
        print "BFI: ", bfi

        # Insert best roundtrip flight into Cloud SQL, replacing any previous version.
        delete_sql="""DELETE FROM %s WHERE check_date = '%s' and there_date = '%s' and back_date = '%s' and destination_airport = '%s'""" % (self.sql_table, bfi[0], bfi[1], bfi[2], bfi[3])
        self.execute_sql(delete_sql)

        insert_sql="""INSERT INTO %s (check_date, there_date, back_date, destination_airport, price, there_times, there_operator, there_time, there_stops, back_times, back_operator, back_time, back_stops, book_url, latest, there_period, back_period) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (self.sql_table, bfi[0], bfi[1], bfi[2], bfi[3], bfi[9], bfi[5], bfi[6], bfi[7], bfi[8], bfi[10], bfi[11], bfi[12], bfi[13], bfi[14], bfi[15], self.outbound_depart_period, self.return_arrival_period)
        print insert_sql.encode('utf8')
        self.execute_sql(insert_sql)

    # Update which fares are latest.
    update_sql="""UPDATE %s SET latest='1' WHERE check_date = '%s'""" % (self.sql_table, self.check_date)
    self.execute_sql(update_sql)
    update2_sql="""UPDATE %s SET latest='0' WHERE check_date != '%s'""" % (self.sql_table, self.check_date)
    self.execute_sql(update2_sql)

    # Clean up database and driver.
    self.db.close()
    self.driver.close()
