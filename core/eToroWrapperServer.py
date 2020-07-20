from flask import Flask
from Crawler.eToroCrawler import eToroCrawler
from Responses.BasicResponse import BasicResponse
from Responses.ErrorResponse import ErrorResponse
from Exceptions.LeverageNotAvailable import LeverageNotAvailable
import selenium.common.exceptions as ES
import Responses.Messages as M
import Parser.Parser as P
import Logger.Logger as L
import os, psutil, subprocess
import requests

class eToroWrapperServer():

    def __init__(self):
        """
        Constructor for the class eToroWrapperServer
        """
        self.app = Flask(__name__)
        self.logger = L.create_log("logfile.log")
        self.logger.info("Logfile was created")
        self.setRoutes()
        self.driver = eToroCrawler()
        self.logger.info("Crawler has been initialized succesfully")
        self.api_pid = os.getpid()
        #self.webdriver_pid = self.driver.driver.service.process.pid
        #print("API pid: " + str(self.api_pid) + " webdriver pid: " + str(self.webdriver_pid))
        #subprocess.Popen(['python3', 'ServerWatcher.py' ,str(self.api_pid), str(self.webdriver_pid)])
        self.logger.info("Server is online")
        self.app.run(debug=True, host='0.0.0.0', use_reloader=False)
        # command = 'python3 ServerWatcher.py ' + str(os.getpid())
        # print(command)
        # os.system(command)

    def setRoutes(self):
        """
        This method maps API endpoints with each functional method
        """
        self.app.add_url_rule('/service_status','service_status', self.service_status) # Permite conocer el estado de la API
        self.app.add_url_rule('/change_mode/<string:mode>', 'change_mode', self.change_mode) # Permite conmutar entre modo real y virtual
        self.app.add_url_rule('/get_active_info/<string:action>/<string:active>', 'get_active_info', self.get_active_info) # Obtiene los datos de las posiciones activas de un determinado activo
        self.app.add_url_rule('/get_wallet_info', 'get_wallet_info', self.get_wallet_info) # Obtiene los datos relativos a la cartera ofrecidos por eToro
        self.app.add_url_rule('/get_portfolio/', 'get_portfolio', self.get_portfolio, defaults={"active":None}) # Obtiene los datos de las posiciones activas de un determinado activo
        self.app.add_url_rule('/get_portfolio/<string:active>', 'get_portfolio', self.get_portfolio) # Obtiene los datos de las posiciones activas de un determinado activo
        self.app.add_url_rule('/open_position/<string:action>/<string:active>/<string:leverage>/<string:amount>', 'open_position', self.open_position) # Permite abrir una posicion de un activo determinado
        self.app.add_url_rule('/close_position/<string:active>/<int:id>', 'close_position', self.close_position) # Permite cerrar una posicion de un activo determinado
        self.app.add_url_rule('/close_all/', 'close_all', self.close_all, defaults={"active":None}) # Permite cerrar todas las posiciones de un activo determinado
        self.app.add_url_rule('/close_all/<string:active>', 'close_all', self.close_all) # Permite cerrar todas las posiciones de un activo determinado

    def service_status(self):
        """
        This method enables user to know wheter this service is running or not
        """
        self.logger.info("Endpoint /service_status was called")
        response = BasicResponse("OK", M.API_STATUS_DESCRIPTION, M.API_STATUS_OK)
        return response.json_response()

    def change_mode(self, mode):
        """
        This method enables changing between "virtual" and "real" mode

        :param mode: Mode you want to change. It can be "virtual" or "real"
        :type mode: string

        :return: Returns a json response which the status of the request and the information requested if succeed
        :rtype: Response
        """
        self.logger.info("Endpoint /change_mode/" + mode + "was called")
        try:
            if mode == "real" or mode == "virtual":
                self.driver.change_mode(mode)
                self.logger.info("Mode changed succesfully")
                response = BasicResponse("OK", M.CHANGE_MODE_DESCRIPTION, M.CHANGE_MODE_OK + mode)
                return response.json_response()
            else:
                self.logger.warn("Unavailable mode was provided")
                response = ErrorResponse("KO", M.CHANGE_MODE_DESCRIPTION, M.CHANGE_MODE_KO, M.CHANGE_MODE_INVALID_PARAM)
                return response.json_error_response()
        except ES.TimeoutException as err:
            self.logger.warning("Operation couldn't be done: " + str(err))
            response = ErrorResponse("KO", M.CHANGE_MODE_DESCRIPTION, M.CHANGE_MODE_KO, str(err))
            return response.json_error_response()

    # Agregar excepciones
    def get_active_info(self, action, active):
        """
        This method provides detailed info about and active for a buying or selling action

        :param action: The action type. It can be "buy" or "sell"
        :type action: string
        :param active: Name used for an active in the eToro Web IDE.
        :type active: string

        :return: Returns a json response which the status of the request and the information requested if succeed
        :rtype: Response
        """
        self.logger.info("Endpoint /get_active_info/" + action + "/" + active + "was called")
        info = self.driver.get_active_info(action, active)
        response = BasicResponse("OK", M.PORTFOLIO_DESCRIPTION, info)
        return response.json_response()

    def get_wallet_info(self):
        """
        This method provides the user wallet info. It can be called by requesting /get_wallet_info

        :return: Returns a json response which the status of the request and the information requested if succeed
        :rtype: Response
        """
        self.logger.info("Endpoint /get_wallet_info was called")
        try:
            wallet = P.parse_wallet(self.driver.get_wallet_info())
            self.logger.info("Wallet info was gathered succesfully")
            response = BasicResponse("OK", M.WALLET_DESCRIPTION, wallet)
            return response.json_response()
        except ES.TimeoutException as err:
            self.logger.warning("Wallet info couldn't be gathered: " + str(err))
            response = ErrorResponse("KO", M.WALLET_DESCRIPTION, M.WALLET_KO, str(err))
            return response.json_error_response()

    def get_portfolio(self, active):
        """
        This method provides general or specific info from user's porfolio such as actives managed or positions opened of each active. This method can be called by requesting to /get_portfolio/<string:active>

        :param active: Its value should be the name of a specific active (btc, ethereum...) or the word general in order to get the general user portfolio.
        :type active: string

        :return: Returns a json response which the status of the request and the information requested if succeed
        :rtype: Response
        """
        self.logger.info("Endpoint /get_portfolio/" + active + " was called")
        try:

            if active == None:
                portfolio = P.parse_portfolio(self.driver.get_portfolio(""))
                self.logger.info("Portfolio general data was gathered")
            else:
                portfolio = P.parse_active_portfolio(self.driver.get_portfolio(active))
                self.logger.info("Portfolio for " + active + " data was gathered")
            response = BasicResponse("OK", M.PORTFOLIO_DESCRIPTION, portfolio)
            return response.json_response()
        except ES.TimeoutException as err:
            self.logger.warning("Portfolio info couldn't be gathered: " + str(err))
            response = ErrorResponse("KO", M.PORTFOLIO_DESCRIPTION, M.PORTFOLIO_KO, str(err))
            return response.json_error_response()

    def open_position(self, action, active, leverage, amount):
        """
        This method enables opening a new position. It can manage some parameters such as action type, active, leverage and amount

        :param action: The action type. It can be "buy" or "sell"
        :type action: string
        :param active: Name used for an active in the eToro Web IDE.
        :type active: string
        :param leverage: Leverage multiplier. It should be an available value in eToro Web IDE.
        :type leverage: string
        :param amount: Amount of active.
        :type amount: string

        :return: Returns a json response which the status of the request and the information requested if succeed
        :rtype: Response
        """
        self.logger.info("Endpoint /open_position/" + action + "/" + active + "/" + leverage + "/" + amount + " was called")
        try:
            self.driver.open_position(action, active, leverage, amount)
            self.logger.info("Position was opened succesfully")
            response = BasicResponse("OK", M.OPEN_POSITION_DESCRIPTION, M.OPEN_POSITION_OK)
            return response.json_response()
        except LeverageNotAvailable as err:
            self.logger.warn("Provided leverage is not allowed for this active")
            response = ErrorResponse("KO", M.OPEN_POSITION_DESCRIPTION, M.OPEN_POSITION_KO, str(err))
            return response.json_error_response()
        except Exception as err:
            self.logger.warning("Position couldn't be opened: " + str(err))
            response = ErrorResponse("KO", M.OPEN_POSITION_DESCRIPTION, M.OPEN_POSITION_KO, str(err))
            return response.json_error_response()

    def close_position(self, active, id):
        """
        This method enables closing an existing position.

        :param active: Name used for an active in the eToro Web IDE.
        :type active: string
        :param id: Current id for the target position.
        :type id: int

        :return: Returns a json response which the status of the request and the information requested if succeed
        :rtype: Response
        """
        self.logger.info("Endpoint /close_position/" + active + "/" + id)
        try:
            self.driver.close_position(active, id)
            self.logger.info("Position was closed succesfully")
            response = BasicResponse("OK", M.CLOSE_POSITION_DESCRIPTION, M.CLOSE_POSITION_OK)
            return response.json_response()
        except Exception as err:
            self.logger.warning("Position couldn't be closed: " + str(err))
            response = ErrorResponse("KO", M.CLOSE_POSITION_DESCRIPTION, M.CLOSE_POSITION_KO, str(err))
            return response.json_error_response()

    def close_all(self, active):
        """
        This method enables closing all opened position. It could receive a parameter to focus on a scpecific active

        :param active: Name used for an active in the eToro Web IDE.
        :type active: string

        :return: Returns a json response which the status of the request and the information requested if succeed
        :rtype: Response
        """
        self.logger.info("Endpoint /close_all/" + active )
        try:
            if active == None:
                self.driver.close_all()
                self.logger.info("Positions were closed succesfully")
            else:
                self.driver.close_all_active(active)
                self.logger.info("Positions were closed succesfully")
            response = BasicResponse("OK", M.CLOSE_POSITION_DESCRIPTION, M.CLOSE_POSITION_OK)
            return response.json_response()
        except Exception as err:
            self.logger.warning("Position couldn't be closed: " + str(err))
            response = ErrorResponse("KO", M.CLOSE_POSITION_DESCRIPTION, M.CLOSE_POSITION_KO, str(err))
            return response.json_error_response()


server = eToroWrapperServer()
# print(command)
# os.system(command)
# server.app.run(debug=True, host='0.0.0.0')
