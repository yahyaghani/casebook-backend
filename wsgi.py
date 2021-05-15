"""Web Server Gateway Interface"""

##################
# FOR PRODUCTION
####################
from py._builtin import execfile

from src.app import app
from src.authentication.db_connector import DatabaseConnector
#from src.authentication.login import LoginApi
from flask import Flask, request

from src.authentication.authentication import AuthApi
import src.authentication.login as login




if __name__ == "__main__":
    execfile(login)
    ####################
    # FOR DEVELOPMENT
    ####################
    #app.run(host='0.0.0.0', debug=True)



