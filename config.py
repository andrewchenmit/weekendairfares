import config_utility

short_dist_dests = [
  'PDX',
  'SAN',
  'YYJ',
  'YVR',
  'PHX',
  'SEA',
  'SLC',
  'LAS',
  'LAX',
  'DEN',
  'PSP'
]

medium_dist_dests = [
  'SJD',
  'YYC',
  'PVR',
  'AUS',
  'SAT',
  'ORD,MDW',
  'STL',
  'JAC'
]

friday_evening_to_sunday_evening = config_utility.ScraperConfig(
  short_dist_dests,
  config_utility.generate_weekend_dates(24),
  '2000-2400',
  '1800-2200',
  'evening',
  'evening',
  'fares'
)

friday_evening_to_monday_morning = config_utility.ScraperConfig(
  short_dist_dests,
  config_utility.generate_fridays_to_mondays(24),
  '2000-2400',
  '0400-0800',
  'evening',
  'morning',
  'fares'
)

three_day_weekend = config_utility.ScraperConfig(
  short_dist_dests + medium_dist_dests,
  config_utility.generate_three_day_weekend_dates(24),
  '2000-2400',
  '1800-2200',
  'evening',
  'evening',
  '3dayweekends'
)

configs_to_scrape = [
    friday_evening_to_sunday_evening,
    friday_evening_to_monday_morning,
    three_day_weekend
]
