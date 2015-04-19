import times
import destinations
import utility

friday_evening_to_sunday_evening = utility.ScraperConfig(
  destinations.short_dist_dests,
  utility.gen_date_pairs('friday', 'sunday', 24),
  times.depart_evening,
  times.arrive_evening,
  'Friday evening',
  'Sunday evening',
  'fares'
)

friday_evening_to_monday_morning = utility.ScraperConfig(
  destinations.short_dist_dests,
  utility.gen_date_pairs('friday', 'monday', 24),
  times.depart_evening,
  times.arrive_morning,
  'Friday evening',
  'Monday morning',
  'fares'
)

thursday_evening_to_sunday_evening = utility.ScraperConfig(
  destinations.short_dist_dests + destinations.medium_dist_dests,
  utility.gen_date_pairs('thursday', 'sunday', 24),
  times.depart_evening,
  times.arrive_evening,
  'Thursday evening',
  'Sunday evening',
  '3dayweekends'
)

thursday_evening_to_monday_morning = utility.ScraperConfig(
  destinations.short_dist_dests + destinations.medium_dist_dests,
  utility.gen_date_pairs('thursday', 'monday', 24),
  times.depart_evening,
  times.arrive_morning,
  'Thursday evening',
  'Monday morning',
  '3dayweekends'
)

friday_evening_to_monday_evening = utility.ScraperConfig(
  destinations.short_dist_dests + destinations.medium_dist_dests,
  utility.gen_date_pairs('friday', 'monday', 24),
  times.depart_evening,
  times.arrive_evening,
  'Friday evening',
  'Monday evening',
  '3dayweekends'
)

friday_evening_to_tuesday_morning = utility.ScraperConfig(
  destinations.short_dist_dests + destinations.medium_dist_dests,
  utility.gen_date_pairs('friday', 'tuesday', 24),
  times.depart_evening,
  times.arrive_morning,
  'Friday evening',
  'Tuesday morning',
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
