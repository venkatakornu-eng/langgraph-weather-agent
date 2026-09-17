import unittest

from components.helper_functions import (
    classify_temperature,
    format_weather_time,
    get_weather_description,
    offset_seconds_to_text,
    parse_utc_offset,
    wind_direction_to_compass,
)


class HelperFunctionTests(unittest.TestCase):
    def test_temperature_boundaries(self):
        self.assertEqual(classify_temperature(0), "cold")
        self.assertEqual(classify_temperature(10), "cool")
        self.assertEqual(classify_temperature(18), "comfortable")
        self.assertEqual(classify_temperature(26), "warm")
        self.assertEqual(classify_temperature(32), "hot")

    def test_weather_code_lookup(self):
        self.assertEqual(get_weather_description(0), "Clear sky")
        self.assertIn("123", get_weather_description(123))

    def test_utc_offset(self):
        self.assertEqual(parse_utc_offset("+0530").total_seconds(), 19800)
        self.assertEqual(parse_utc_offset("-08:00").total_seconds(), -28800)

    def test_offset_seconds_to_text(self):
        self.assertEqual(offset_seconds_to_text(3600), "+01:00")
        self.assertEqual(offset_seconds_to_text(19800), "+05:30")
        self.assertEqual(offset_seconds_to_text(-28800), "-08:00")

    def test_format_weather_time(self):
        result = format_weather_time("2026-09-16T17:45", "Europe/London", 3600)
        self.assertIn("17:45 local", result)
        self.assertIn("Europe/London", result)
        self.assertIn("UTC+01:00", result)

    def test_wind_direction(self):
        self.assertEqual(wind_direction_to_compass(0), "N")
        self.assertEqual(wind_direction_to_compass(90), "E")
        self.assertEqual(wind_direction_to_compass(225), "SW")


if __name__ == "__main__":
    unittest.main()
