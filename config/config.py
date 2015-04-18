import destinations
import utility

friday_evening_to_sunday_evening = utility.ScraperConfig(
  destinations.short_dist_dests,
  utility.generate_weekend_dates(24),
  '2000-2400',
  '1800-2200',
  'evening',
  'evening',
  'fares'
)

friday_evening_to_monday_morning = utility.ScraperConfig(
  destinations.short_dist_dests,
  utility.generate_fridays_to_mondays(24),
  '2000-2400',
  '0400-0800',
  'evening',
  'morning',
  'fares'
)

three_day_weekend = utility.ScraperConfig(
  destinations.short_dist_dests + destinations.medium_dist_dests,
  utility.generate_three_day_weekend_dates(24),
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
