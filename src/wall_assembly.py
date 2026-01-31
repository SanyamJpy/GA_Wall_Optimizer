from .dataBase_loader import getDataBase
import random
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s:%(lineno)d - %(message)s'
)



# func to create a simple wall assem
def wallAssembly(dataBase, index=0):


    # create  lists for all the materials of each layer
    mat1_list = []
    mat2_list = []
    mat3_list = []
    mat4_list = []
    mat5_list = []
    mat6_list = []
    mat8_list = []
    mat9_list = []
    # list to store all wall layers
    layers = []


    for layer in dataBase["Components"]:
        layers.append(layer)
    

    for l in layers:
        if l == "04_wallInsulationInside":
            for material in dataBase["Components"][l]:
                # print(material)
                mat4_list.append(material)

        elif l == "09_wallFinishFacade":
            for material in dataBase["Components"][l]:
                mat9_list.append(material)
        
        elif l == "03_woodBasedBoard":
            for material in dataBase["Components"][l]:
                mat3_list.append(material)

        elif l == "01_wallFinishInside":
            for material in dataBase["Components"][l]:
                mat1_list.append(material)

        elif l == "05_PrimaryStructure":
            for material in dataBase["Components"][l]:
                mat5_list.append(material)

        elif l == "06_secondaryInsulation":
            for material in dataBase["Components"][l]:
                mat6_list.append(material)

        elif l == "08_battens_rainscreen":
            for material in dataBase["Components"][l]:
                mat8_list.append(material)

        elif l == "02_IfcMember-vapour":
            for material in dataBase["Components"][l]:
                mat2_list.append(material)

    # print(mat1_list)

    # #select random material Name from list -> "string"
    lay_1_mat = mat1_list[random.randint(0, len(mat1_list)-1)]
    lay_2_mat = mat2_list[random.randint(0, len(mat2_list)-1)]
    lay_3_mat = mat3_list[random.randint(0, len(mat3_list)-1)]
    lay_4_mat = mat4_list[random.randint(0, len(mat4_list)-1)]
    lay_5_mat = mat5_list[random.randint(0, len(mat5_list)-1)]
    lay_6_mat = mat6_list[random.randint(0, len(mat6_list)-1)]
    lay_8_mat = mat8_list[random.randint(0, len(mat8_list)-1)]
    lay_9_mat = mat9_list[random.randint(0, len(mat9_list)-1)]



    logging.info(f"Wall-{index}\nSelected Materials: \nLayer 1_Mat: {lay_1_mat} \nLayer 2_Mat: {lay_2_mat} \nLayer 3_Mat: {lay_3_mat} \nLayer 4_Mat: {lay_4_mat} \nLayer 5_Mat: {lay_5_mat} \nLayer 6_Mat: {lay_6_mat} \nLayer 8_Mat: {lay_8_mat} \nLayer 9_Mat: {lay_9_mat}")
    print("="*100)

    "create a wall assem-------------------------------------------"
    wall_assem = [
        dataBase["Components"]["01_wallFinishInside"][lay_1_mat],
        dataBase["Components"]["02_IfcMember-vapour"][lay_2_mat],
        dataBase["Components"]["03_woodBasedBoard"][lay_3_mat],
        dataBase["Components"]["04_wallInsulationInside"][lay_4_mat],
        dataBase["Components"]["05_PrimaryStructure"][lay_5_mat],
        dataBase["Components"]["06_secondaryInsulation"][lay_6_mat],
        dataBase["Components"]["08_battens_rainscreen"][lay_8_mat],
        dataBase["Components"]["09_wallFinishFacade"][lay_9_mat]
    ]


    return wall_assem

if __name__ == "__main__":

    filePath = "dataBase/test_dataBase_2.json"

    dataBase = getDataBase(filePath)
    if not dataBase:
        print("Data Base not loaded")
        print("x-"*20)
        exit()

    wall_assem =wallAssembly(dataBase)

    # for m in wall_assem:
    #     print("HERE ====.",m)
    #     print(m["name"])
    



# To RUN THIS FILE as a module
# python -m src.wall_assembly   