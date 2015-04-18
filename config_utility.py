import datetime

class ScraperConfig:
  def __init__(self, dests, date_pairs, depart_times, arrival_times, outbound_depart_period, return_arrival_period, sql_table):
    self.dests = dests
    self.date_pairs = date_pairs
    self.depart_times = depart_times
    self.arrival_times = arrival_times
    self.outbound_depart_period = outbound_depart_period
    self.return_arrival_period = return_arrival_period
    self.sql_table = sql_table

def generate_weekend_dates(num_weeks):
  weekend_dates = []
  starting_date = datetime.date(2015,4,4)
  nearest_friday = starting_date + datetime.timedelta( (4-starting_date.weekday()) %7)
  for i in xrange(num_weeks):
    friday = nearest_friday + datetime.timedelta(i*7)
    sunday = friday + datetime.timedelta(2)
    weekend_dates.append([
      str(friday.year)+'-'+str('{:02d}'.format(friday.month))+'-'+str('{:02d}'.format(friday.day)),
      str(sunday.year)+'-'+str('{:02d}'.format(sunday.month))+'-'+str('{:02d}'.format(sunday.day))
      ])
  return weekend_dates

def generate_three_day_weekend_dates(num_weeks):
  weekend_dates = []
  starting_date = datetime.date(2015,4,4)
  nearest_thursday = starting_date + datetime.timedelta( (3-starting_date.weekday()) %7)
  for i in xrange(num_weeks):
    thursday = nearest_thursday + datetime.timedelta(i*7)
    friday = thursday + datetime.timedelta(1)
    sunday = friday + datetime.timedelta(2)
    monday = sunday + datetime.timedelta(1)

    weekend_dates.append([
      str(thursday.year)+'-'+str('{:02d}'.format(thursday.month))+'-'+str('{:02d}'.format(thursday.day)),
      str(sunday.year)+'-'+str('{:02d}'.format(sunday.month))+'-'+str('{:02d}'.format(sunday.day))
      ])
    weekend_dates.append([
      str(friday.year)+'-'+str('{:02d}'.format(friday.month))+'-'+str('{:02d}'.format(friday.day)),
      str(monday.year)+'-'+str('{:02d}'.format(monday.month))+'-'+str('{:02d}'.format(monday.day))
      ])
  return weekend_dates

def generate_fridays_to_mondays(num_weeks):
  weekend_dates = []
  starting_date = datetime.date(2015,4,4)
  nearest_friday = starting_date + datetime.timedelta( (4-starting_date.weekday()) %7)
  for i in xrange(num_weeks):
    friday = nearest_friday + datetime.timedelta(i*7)
    monday = friday + datetime.timedelta(3)

    weekend_dates.append([
      str(friday.year)+'-'+str('{:02d}'.format(friday.month))+'-'+str('{:02d}'.format(friday.day)),
      str(monday.year)+'-'+str('{:02d}'.format(monday.month))+'-'+str('{:02d}'.format(monday.day))
      ])
  return weekend_dates
