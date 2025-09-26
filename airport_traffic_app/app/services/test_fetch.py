import departure_cache

flights = departure_cache.fetch_departures(year=2025, month=9, day=26, hour=6, airport_code="BOS")
print(flights)