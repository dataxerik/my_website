API_KEY_404 = "Could\'t find the API key. Please re-enter the API key."
API_KEY_MALFORMED = "The given API key isn't valid. Please enter a valid API key."
API_KEY_BAD_CALL = "While calling the WaniKani service, there was an issue. " \
                  "Please double check the API key and try again."
BAD_REQUEST_RESPONSE = "There was an issue while calling the Wanikani api. Please wait and try again later."
class APIErrorMessage:
    @staticmethod
    def construct_api_error_message(message):
        return "Error: {0}".format(message)

