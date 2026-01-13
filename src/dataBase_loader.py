import json
import logging
from pathlib import Path


filePath = "dataBase/test_dataBase_2.json"

def getDataBase():

    try:
        with open("dataBase/test_dataBase_2.json") as file:
            dataBase = json.load(file)
        
        # logging.info ("DataBase loaded!")
        # print ("=="*20)
        
        # print (dataBase)

        # for components in dataBase["Components"]:
            # print ("{}====== {}".format(components, dataBase[components]))
            # print(components["layer_name"])
            # print ("=="*20)
            # for materials in dataBase[components]:
            #     print ("{}====== {}".format(materials, dataBase[components][materials]))
            

            # print(dataBase[components]["IfcBuildingElementProxy-wallInsulationInside"])

        # for component in dataBase["Components"]:
        #     print (component)
        #     print ("=="*20)
            # for layer in component['materials']:
            #     # print (layer)
            #     print ("=="*20)
            #     for material in dataBase[component][layer]:
            #         print ("{}====== {}".format(material, dataBase[component][layer][material]))

        # for component in dataBase["Components"]:
        #     if component['Layer_id']== 4:
        #         # print (component['Layer_id'])
        #         # print ("=="*20)
        #         # print (component['layer_name'])
        #         # print ("=="*20)
        #         # print(component['materials'])
        #         for layer in component['materials']:
        #             if layer['name'] == "StoneWool_Insulation":
        #                 print (layer["lambda"])

        """ Debug for filePath_2"""

        # for component in dataBase["Components"]:
        #     print (component)
        #     for material in dataBase['Components'][component]:
        #         print(material)
        #         print ("=="*20)

        # lambdaVal = dataBase['Components']['wallInsulationInside']['StoneWool_Insulation']['lambda']
        # thickness = dataBase['Components']['wallInsulationInside']['StoneWool_Insulation']['thickness_init'] /1000

        # rVal = thickness / lambdaVal 
        # print ("r-value: {}".format(rVal))

        return dataBase
    
    except FileNotFoundError:
        logging.info ("File {} not found".format("dataBase/test_dataBase_2.json"))
        return None
    
    # If any errors in JSON
    except json.JSONDecodeError:
        logging.info ("File {} is not a valid JSON file".format("dataBase/test_dataBase_2.json"))
        return None



# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

currentDir = Path(__file__).parent
filePath = currentDir / "dataBase/test_dataBase_2.json"



# dataBase = getDataBase(filePath)
