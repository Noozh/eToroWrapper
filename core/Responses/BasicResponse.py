

class BasicResponse():

    def __init__(self, status, description, response):
        """
        Constructor for the response object

        :param status: Status of the response
        :type status: string
        :param description: Brief description of the information provided in the response
        :type description: string
        :param response: Response payload
        :type response: dict, string
        """
        self.status = status
        self.description = description
        self.response = response

    def json_response(self):
        """
        Formats properly a response to convert it into a json

        :return response: Its a json which contains the parameters provide in the constructor
        :rtype response: dict
        """
        response = {}
        response ["status"] = self.status
        response ["description"] = self.description
        response ["response"] = self.response
        return response
