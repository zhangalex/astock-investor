import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.sql import exists
import csv 
import tushare as ts

from app import db
from app import app 
from app.models.main import Simu

import datetime

import json
import demjson

def refreshSimu():
  # with open(app.config['SIMU_DATA_PATH']) as csvDataFile:
    # csvReader = csv.reader(csvDataFile)
    # for row in csvReader:
        # print(row['artificialPersonName'])

  input_file = csv.DictReader(open(app.config['SIMU_DATA_PATH']))
  for row in input_file:
    print(row['registerDate'])
