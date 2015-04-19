import times
import destinations
import utility

weeks = 12

friday_evening_to_sunday_evening = utility.ScraperConfig(
  destinations.short_dist_dests,
  utility.gen_date_pairs('friday', 'sunday', weeks),
  times.depart_evening,
  times.arrive_evening,
  'Fri evening',
  'Sun evening',
  'fares'
)

friday_evening_to_monday_morning = utility.ScraperConfig(
  destinations.short_dist_dests,
  utility.gen_date_pairs('friday', 'monday', weeks),
  times.depart_evening,
  times.arrive_morning,
  'Fri evening',
  'Mon morning',
  'fares'
)

thursday_evening_to_sunday_evening = utility.ScraperConfig(
  destinations.medium_dist_dests,
  utility.gen_date_pairs('thursday', 'sunday', weeks),
  times.depart_evening,
  times.arrive_evening,
  'Thu evening',
  'Sun evening',
  '3dayweekends'
)

thursday_evening_to_monday_morning = utility.ScraperConfig(
  destinations.medium_dist_dests,
  utility.gen_date_pairs('thursday', 'monday', weeks),
  times.depart_evening,
  times.arrive_morning,
  'Thu evening',
  'Mon morning',
  '3dayweekends'
)

friday_evening_to_monday_evening = utility.ScraperConfig(
  destinations.medium_dist_dests,
  utility.gen_date_pairs('friday', 'monday', weeks),
  times.depart_evening,
  times.arrive_evening,
  'Fri evening',
  'Mon evening',
  '3dayweekends'
)

friday_evening_to_tuesday_morning = utility.ScraperConfig(
  destinations.medium_dist_dests,
  utility.gen_date_pairs('friday', 'tuesday', weeks),
  times.depart_evening,
  times.arrive_morning,
  'Fri evening',
  'Tue morning',
  '3dayweekends'
)

configs_to_scrape = [
  thursday_evening_to_sunday_evening,
  thursday_evening_to_monday_morning,
  friday_evening_to_monday_evening,
  friday_evening_to_tuesday_morning,
  friday_evening_to_sunday_evening,
  friday_evening_to_monday_morning
]
