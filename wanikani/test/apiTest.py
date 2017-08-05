import unittest
import wanikani.service
from wanikani.exceptions import InvalidAPIKeyException, BadRequestException

isNotBadUrlSet = False


class TestAPI(unittest.TestCase):
    def test_valid_api_key(self):
        self.assertTrue(wanikani.service.is_valid_api_key("c9d088f9u7500688b3104ebuu3d1d5fa"))

    def test_nonvalid_api_key(self):
        self.assertFalse(wanikani.service.is_valid_api_key("c9d088f9u7500688b3104ebuu3d1d5fa11"))
        self.assertFalse(wanikani.service.is_valid_api_key("c9d088f9u7500688b3104ebuu3"))

    def test_bad_key(self):
        self.assertRaises(InvalidAPIKeyException.InvalidAPIKeyException,
                          wanikani.service.get_api_information, "c9d088f9u7500688b3104ebuu3d1d5fa11", "Kanji")

    def test_bad_service_type(self):
        self.assertRaises(ValueError, wanikani.service.get_api_information,
                          "c9d088f9u7500688b3104ebuu3d1d5fa", "Kanji1")

    @unittest.skipIf(isNotBadUrlSet, "This is a manual test that doesn't need to run every time.")
    def test_bad_request(self):
        self.assertRaises(BadRequestException.BadRequestException,
                          wanikani.service.get_api_information,
                          "c9d088f9u7500688b3104ebuu3d1d5fa", "Kanji")


if __name__ == '__main__':
    unittest.main()
