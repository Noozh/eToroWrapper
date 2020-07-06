
class LeverageNotAvailable(Exception):
    def __init__(self, *args):
        """
        Custom exception constructor

        :param *args: It should contain an element whose content should be an average rate
        :type *args: list

        """
        self.leverage = args[0]

    def __str__(self):
        """
        To string custom method

        :return: Custom message which provides a description of the exception
        :rtype: string

        """
        return 'Error, provided leverage(' + self.leverage + ') is not available for this active. Please check available leverages in /get_active_info/<string:action>/<string:active>'
