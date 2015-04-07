import datetime
import time
import MySQLdb
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url_template = 'https://www.google.com/flights/#search;f={origin};t={destination};d={depart_date};r={return_date};ti=t{depart_times},l{arrival_times}'

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
  #print "a: ", price
  infos_parts = price.split('$')
  #print "b: ", infos_parts
  price = '$' + infos_parts[1]
  #print "c: ", price
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

#destinations = ['AUS', 'PDX', 'CUN', 'YVR', 'LAS', 'SAN', 'PHX', 'SLC', 'SEA', 'LAX', 'BOS']
#weekend_dates = generate_weekend_dates(48)
weekend_dates = [['2015-04-17','2015-04-19']]
destinations = ['AUS']
#weekend_dates = generate_weekend_dates(1)

db = MySQLdb.connect('173.194.80.20','root','roos','weekendfares')
cursor=db.cursor()

driver = webdriver.Chrome('/Applications/chromedriver')

def find_best_flights():
  # Find the set of best flights. Try the Best flights module.
  best_flights = driver.find_elements_by_css_selector('.PNIT24B-c-Qb')

  # If there isn't a Best flights module, use the regular list.
  if len(best_flights) == 0:
    best_flights = driver.find_elements_by_css_selector('.PNIT24B-c-H')

  # Keep going if there are no flights returned at all.
  if len(best_flights) == 0:
   best_flights = [['no results']]

  return best_flights

expanded_count = 0
def expand_similar_flight():
  best_flights = find_best_flights()

  skipped_flights = 0
  for flight in best_flights:
    infos = flight.text.split('\n')
    if len(infos) < 3:
      continue
    print "INFOS: ", infos
    depart_times = infos[2]

    if 'similar flights' in depart_times:
      # if less flights have been skipped than expanded flights, skip
      global expanded_count
      #print "Skipped flights: ", skipped_flights
      #print "Expanded count: ", expanded_count
      if skipped_flights < expanded_count:
        skipped_flights += 1
      else:
        expanded_count += 1
        #print infos
        flight.click()
        time.sleep(1)
        return False
  return True


for d in destinations:
  for weekend in weekend_dates:
    url = url_template.format(
      origin='SFO',
      destination=d,
      depart_date=weekend[0],
      return_date=weekend[1],
      depart_times='1900-2400',
      arrival_times='1200-2200')

    print url

    # Wait 2s for results to load.
    driver.get(url)
    time.sleep(2)

    def get_best_flight():
      global expanded_count
      expanded_count = 0
      no_more_similar_flights = False
      print "getting best flight..."
      # Find set of best flights.
      best_flights = find_best_flights()

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
        last_price = ''
        for flight in best_flights:
          infos = flight.text.split('\n')
          try:
            infos.remove('')
          except:
            pass
          #print "Previous infos: ", infos
          if '$' in infos[0]:
            price = get_price(infos[0])
            #print "d: ", price
            infos[0] = price
            #print "Price: ", price
            last_price = price
          else:
            infos = [last_price] + infos

          # If there were no expansions, delete "round trip"
          print "EXPANDED: ", expanded_count
          if expanded_count == 0:
            del infos[1]

          print "Amended infos: ", infos

          price = int(infos[0][1:].replace(',', ''))

          # Add to candidate set if not a similar flights item.
          if price not in flights_by_price and 'similar' not in infos[2]:
            flights_by_price[price] = [infos, flight]
            print "appended price: ", price
            prices.append(price)

        # bfi is short for best_flight_info
        bfi = flights_by_price[min(prices)][0]
        best_flight_element = flights_by_price[min(prices)][1]
        return [bfi, best_flight_element]

    there_bfi, there_bfe = get_best_flight()
    print "there BFI: ", there_bfi

    # Select first best flight.
    there_bfe.click()
    time.sleep(2)

    back_bfi, back_bfe = get_best_flight()
    print "back BFI: ", back_bfi
    bfi = [datetime.date.today().isoformat(), weekend[0], weekend[1], d] + there_bfi + back_bfi
    print "BFI: ", bfi

    delete_sql="""DELETE FROM fares WHERE check_date = '%s' and there_date = '%s' and destination_airport = '%s'""" % (bfi[0], bfi[1], bfi[3])

    execute_sql(delete_sql)

    insert_sql="""INSERT INTO fares (check_date, there_date, back_date, destination_airport, price, there_times, there_operator, there_time, there_stops, back_times, back_operator, back_time, back_stops) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (bfi[0], bfi[1], bfi[2], bfi[3], bfi[9], bfi[5], bfi[6], bfi[7], bfi[8], bfi[10], bfi[11], bfi[12], bfi[13])

    print insert_sql

    execute_sql(insert_sql)

db.close()
driver.close()


