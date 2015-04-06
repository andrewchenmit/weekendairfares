import datetime
import time
import MySQLdb
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url_template = 'https://www.google.com/flights/#search;f={origin};t={destination};d={depart_date};r={return_date};ti=t{depart_times},l{arrival_times}'

def execute_sql(sql):
  try:
    cursor.execute(sql)
    db.commit()
    print "db insert success"
  except MySQLdb.Error as e:
    db.rollback()
    print "db insert error"
    print e

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

destinations = ["AUS", "PDX", "CUN", "YVR", "LAS", "SAN", "PHX", "SLC", "SEA", "LAX", "BOS"]
weekend_dates = generate_weekend_dates(48)
#weekend_dates = [["2015-08-21","2015-08-23"]]
#destinations = ["AUS"]
#weekend_dates = generate_weekend_dates(1)

db = MySQLdb.connect("173.194.80.20","root","roos","weekendfares")
cursor=db.cursor()

driver = webdriver.Chrome('/Applications/chromedriver')

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
          price = int(infos[0].replace(',', ''))
          if price not in flights_by_price:
            flights_by_price[price] = infos
            prices.append(price)
      best_flight = flights_by_price[min(prices)]

      if len(best_flight) > 1 :
        del best_flight[1]

      best_flight = [datetime.date.today().isoformat(), weekend[0], weekend[1], d] + best_flight
      print best_flight

      delete_sql="""DELETE FROM fares WHERE check_date = '%s' and there_date = '%s' and destination_airport = '%s'""" % (best_flight[0], best_flight[1], best_flight[3])

      execute_sql(delete_sql)

      insert_sql="""INSERT INTO fares (check_date, there_date, back_date, destination_airport, price, there_times, there_operator, there_time, there_stops) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (best_flight[0], best_flight[1], best_flight[2], best_flight[3], best_flight[4], best_flight[5], best_flight[6], best_flight[7], best_flight[8])

      print insert_sql

      execute_sql(insert_sql)

db.close()
driver.close()


