# Sys related imports
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, DateTime, Column, Float, Integer, String, Date
from xmlrpc.client import DateTime
from unicodedata import numeric
from datetime import date, datetime, timedelta
from distutils.command.clean import clean
from time import timezone
import pytz

# api json related imports
import requests

# Data Handling imports
import pandas as pd
from pandas import json_normalize
pd.options.mode.chained_assignment = None

# DB Connection and Data Migration Imports


def search_date():
    '''
    Checks to see if 8am cst has happened
    if not then it pulls yesterday's results
    if yes then it pulls todays results
    this lines up with ESO's daily update
    '''
    time_zone = pytz.timezone('America/Chicago')
    datetime_timezone = datetime.now(time_zone)
    current_hour = int(datetime_timezone.strftime('%H'))

    search_date = str(date.today()) if current_hour > 8 else str(
        date.today()-timedelta(days=1))

    return search_date


def starter_url_generatoror():
    '''
    Creates an easier interface for making more complex
    queries for KCAN api
    in 'search_dictionary' add any known column and known 
    attribute that you want to query for in relivant data set
    format == "column header" : "known criterion"

    Only creates first needed URL
    No pagination defeated in this function    
    '''search_date
    search_dictionary = {
        "EFA Date": search_date(), "Company": "HABITAT ENERGY LIMITED"}
    resource_id = "ddc4afde-d2bd-424d-891c-56ad49c13d1a"

    dictionary_list = ['"'+param[0]+'":"'+param[1] +
                       '"' for param in search_dictionary.items()]
    dictionary_string = '{'+','.join(dictionary_list)+'}'

    starting_api = '/api/3/action/datastore_search?q=' + \
        dictionary_string+'&resource_id='+resource_id

    return starting_api


def ApiScraper(links, rawdf, domain):
    # Moving through the links
    link = links[-1]
    request = requests.get(domain+link)
    if request.status_code == 200:
        json = request.json()

        # Stop if there are no records returned
        if json['result']['records'] == []:
            return pd.DataFrame()

        # adding results to rawdf
        df = json_normalize(json['result']['records'])

        # store next link from json
        links.append(json['result']['_links']['next'])

        return df
    else:
        raise 'Response Code: '+str(request.status_code)


def Cleaner(rawdf):
    df = pd.DataFrame(rawdf).astype({
        "_id": int,
        "Company": object,
        "Unit Name": object,
        "EFA": int,
        "Service": object,
        "Cleared Volume": float,
        "Clearing Price": float,
        "Technology Type": object,
        "Cancelled": object
    })

    # Handling dates
    df['EFA Date'] = pd.to_datetime(df['EFA Date'])
    df['Delivery End'] = pd.to_datetime(df['Delivery End'])
    df['Delivery Start'] = pd.to_datetime(df['Delivery Start'])

    # Lowering texts and removing spaces
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(" ", "")

    return df


def EngineGenerator():
    loginAttempt = True
    while loginAttempt:
        try:
            print('-'*20)
            print('PostgreSQL Server Login Information:')
            username = str(
                input('Enter Username (Default: postgres)\n>')).strip()
            password = str(input('Enter Password (Default: None)\n>')).strip()
            host_address = str(
                input('Enter Host Address (Default: localhost)\n>')).strip()
            port = str(input('Enter Port (Default: 5432)\n>')).strip()
            database_name = str(
                input('Enter Database Name (Default: habitat)\n>')).strip()

            engine_string = 'postgresql://'

            defaults = ['', 'postgres', '', '', '@',
                        'localhost', ':', '5432', '/', 'habitat']
            user_input = ['', username, ':', password, '@',
                          host_address, ':', port, '/', database_name]

            for i in range(0, len(defaults), 2):
                if user_input[i+1] == '':
                    engine_string += defaults[i]+defaults[i+1]
                else:
                    engine_string += user_input[i]+user_input[i+1]

            engine = create_engine(engine_string, echo=False)

            if not database_exists(engine.url):
                create_database(engine.url)

            loginAttempt = False

        except Exception as e:
            print(e)
            tryagain = input('\n\n>>Try Again<<\n(Y/N) >> ')
            if tryagain.upper() == 'N':
                raise 'Could Not Login To PostgreSQL Server'
    print('-'*20)
    print('PostgreSQL Server Connection Successful\n', engine_string)
    return engine


def DatabaseHandler(df):
    # Creating engine, Database and allowing for Schema definition
    engine = EngineGenerator()

    Session = sessionmaker(bind=engine)
    session = Session()

    # Define schema and migrate information
    # OR
    # Append newly scraped information

    try:
        Base = declarative_base()

        class eso_auction_results_habitat_schema(Base):
            __tablename__ = 'eso_auction_results_habitat'
            _id = Column(Integer, primary_key=True)
            company = Column(String[50])
            unitname = Column(String)
            efadate = Column(DateTime())
            deliverystart = Column(DateTime())
            deliveryend = Column(DateTime())
            efa = Column(Integer)
            service = Column(String)
            clearedvolume = Column(Float)
            clearingprice = Column(Float)
            technologytype = Column(String)
            location = Column(String)
            cancelled = Column(String)
            rankefadate = Column(Float)
            rankcompany = Column(Float)

        Base.metadata.create_all(engine)

    except Exception as e:
        print(e)

    try:
        df.to_sql('eso_auction_results_habitat', con=engine,
                  if_exists='append', index=False)
    except Exception as e:
        print(">> Error >> No New Values Added To Database <<")


def main():

    links = [starter_url_generator()]
    rawdf = pd.DataFrame()
    domain = 'https://data.nationalgrideso.com'
    cont = True

    # ApiScaper Iterator
    while cont:
        tempdf = ApiScraper(links, rawdf, domain)
        if tempdf.shape[0] > 0:
            rawdf = pd.concat([rawdf, tempdf])
        else:
            cont = False

    print('\nApiScraper: True\n')

    clean_df = Cleaner(rawdf)
    # Creating long term storage version of df
    clean_df.to_csv("df", index=False)

    DatabaseHandler(clean_df)
    print('\nDatabaseHandler: Successful\n')


main()
