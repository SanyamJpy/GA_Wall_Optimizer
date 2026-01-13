from .dataBase_loader import getDataBase
from .wall_assembly import wallAssembly


# Function for individual debugging of modules
# to reduce redundancy of calling wall_assem in each module

def main():

    # filepaths for dataBase
    
    filePath = "dataBase/test_dataBase_2.json"


    # fetch dataBase
    dataBase = getDataBase()
    if not dataBase:
        print("Data Base not loaded")
        print("x-"*20)
        exit()

    # call wallAssembly func & initialize
    wall_assem= wallAssembly(dataBase)

    return wall_assem