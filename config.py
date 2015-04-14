import config_utility

two_day_weekend = config_utility.ScraperConfig([
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
  ],
  config_utility.generate_weekend_dates(24),
  '2000-2400',
  '1600-2200',
  'fares'
)

three_day_weekend = config_utility.ScraperConfig([
  #'SJD',
  'YYC',
  'PVR',
  'AUS',
  'SAT',
  'ORD,MDW',
  'STL',
  'JAC'
  ],
  config_utility.generate_three_day_weekend_dates(24),
  '2000-2400',
  '1600-2200',
  '3dayweekends'
)

