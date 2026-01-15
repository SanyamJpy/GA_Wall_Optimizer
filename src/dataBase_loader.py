import json
import logging
from pathlib import Path


# filePath = "dataBase/test_dataBase_2.json"

def getDataBase(filePath):

    try:
        with open(filePath) as file:
            dataBase = json.load(file)

        return dataBase
    
    except FileNotFoundError:
        logging.info ("File {} not found".format("dataBase/test_dataBase_2.json"))
        return None
    
    # If any errors in JSON
    except json.JSONDecodeError:
        logging.info ("File {} is not a valid JSON file".format("dataBase/test_dataBase_2.json"))
        return None



# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# currentDir = Path(__file__).parent
# filePath = currentDir / "dataBase/test_dataBase_2.json"



# dataBase = getDataBase(filePath)
