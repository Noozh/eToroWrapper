from . import BasicResponse

class ErrorResponse(BasicResponse.BasicResponse):

    def __init__(self, status, description, response, error):
        """
        Constructor for the response object

        :param status: Status of the response
        :type status: string
        :param description: Brief description of the information provided in the response
        :type description: string
        :param response: Response payload
        :type response: dict, string
        :param error: Error message
        :type error: string
        """
        super().__init__(status, description, response)
        self.error = error

    def json_error_response (self):
        """
        Formats properly a response to convert it into a json

        :return response: Its a json which contains the parameters provide in the constructor
        :rtype response: dict
        """
        response = self.json_response()
        response ["error_message"] = self.error
        return response
