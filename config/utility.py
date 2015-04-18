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

def format_date(date):
  return str(date.year)+'-'+str('{:02d}'.format(date.month))+'-'+str('{:02d}'.format(date.day))

def gen_date_pairs(day1, day2, num_weeks):
  result = []
  weekend_dates = generate_weekend_dates(num_weeks)
  for i in xrange(num_weeks):
    result.append([weekend_dates[day1][i], weekend_dates[day2][i]])
  return result

def generate_weekend_dates(num_weeks):
  weekend_dates = {'thursday': [], 'friday': [], 'saturday': [], 'sunday': [], 'monday': [], 'tuesday': []}
  starting_date = datetime.date.today()
  nearest_thursday = starting_date + datetime.timedelta( (3-starting_date.weekday()) %7)

  for i in xrange(num_weeks):
    thursday = nearest_thursday + datetime.timedelta(i*7)
    weekend_dates['thursday'].append(format_date(thursday))
    weekend_dates['friday'].append(format_date(thursday + datetime.timedelta(1)))
    weekend_dates['saturday'].append(format_date(thursday + datetime.timedelta(2)))
    weekend_dates['sunday'].append(format_date(thursday + datetime.timedelta(3)))
    weekend_dates['monday'].append(format_date(thursday + datetime.timedelta(4)))
    weekend_dates['tuesday'].append(format_date(thursday + datetime.timedelta(5)))

  return weekend_dates


