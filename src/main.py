import os, sys
import logging
from dotenv import load_dotenv
from importer import Importer
import mysql.connector
from distutils.util import strtobool
import connexion
from model.person import db

path_env = sys.path[0] + '/../.env'
ENV = os.getenv('ENV')
if str(ENV) == 'production':
    path_env = sys.path[0] + '/../.env.production'
elif str(ENV) == 'development':
    path_env = sys.path[0] + '/../.env.development'

load_dotenv(path_env)

LOG_FILE = os.getenv('LOG_PATH')
# Logging
logging.basicConfig(filename=LOG_FILE, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout)) # Write also to console

logging.info('Environment: '+ str(ENV))

PORT= os.getenv('API_PORT')
logging.debug('api_port: '+ str(PORT))

application = connexion.FlaskApp(__name__)
application.add_api("../swagger.yaml")
app = application.app
hostname = os.getenv('DB_HOST')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')
if hostname is None or username is None or password is None or database is None:
    logging.error('Please set the DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME environment variables')
    sys.exit(1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + username + ':' + password + '@' + hostname + '/' + database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if __name__ == "__main__":
    logging.info("****************** START *****************************")
    IMPORT_CSV = strtobool(os.getenv("IMPORT_CSV", "false"))
    if IMPORT_CSV == True:
        logging.info("Import START")
        mydb = mysql.connector.connect( host=hostname, user=username, passwd=password, db=database )
        IMPORT_CSV_PATH = os.getenv('IMPORT_CSV_PATH')
        importer = Importer(mydb, IMPORT_CSV_PATH)
        importer.process()
        
        mydb.close()
        logging.info("import STOP")
    
    logging.info("Api START")
    db.init_app(app)
    app.run(debug=False, port=PORT)
    
    logging.info("****************** STOP *****************************")
