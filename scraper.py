#!/usr/bin/env python
import airfare_scraper
import config

#two_day_scraper = airfare_scraper.AirfareScraper(config.two_day_weekend, False)
#two_day_scraper.scrape()
three_day_scraper = airfare_scraper.AirfareScraper(config.three_day_weekend, False)
three_day_scraper.scrape()
