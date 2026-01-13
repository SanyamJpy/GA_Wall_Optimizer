from .dataBase_loader import getDataBase
import random
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s:%(lineno)d - %(message)s'
)

# load dataBase
dataBase = getDataBase()

# ==================================================================================

def find_mat_layer(db, random_mat):

    """
    func to find the layer of the material in the dataBase

    'INPUTS':
    "db": dataBase
    "random_mat": random material chosen from the child wall assembly

    'RETURNS':
    "layer_key": layer_key of the material
    "mat_key": material_key of the material dict
    """

    comps = db.get("Components")
    target_id = random_mat.get("id")

    if target_id is None:
        logging.error("Target ID is None")
        return None
    
    for layer_key, materials in comps.items():
        for mat_key, mat_dict in materials.items():
            if mat_dict.get("id") == target_id:
                return layer_key, mat_key
            
    logging.error("Material not found in dataBase")
    exit()





random_mat = {'name': 'MAGOXX_Board', 'id': '03_02', 'factor': 1.21, 'u-value': 3.93, 'u-value_unit': 'W/m2.K', 'r-value': 0.084, 'r-value_unit': 'm2.K/W', 'lambda': 0.0, 'lambda-value_unit': 'W/m.K', 'thickness_init': 9, 'thickness_range': [], 'density': 1100, 'unit': 'm2', 'A1-A3': 21.1, 'A4': 2.71, 'A5': 0.745, 'C1': 0.032, 'C2': 0.106, 'C3': 0.0, 'C4': 0.326, 'D': -0.028}
    
# print(random_mat.get("id"))
# for layer in dataBase["Components"]:
#     print(layer)
# print(dataBase.get("Components"))


def get_mats_of_layer(db, layer_key):

    """
    func to get all the materials of the layer

    'INPUTS':
    "db": dataBase
    "layer_key": layer of the material

    'RETURNS':
    "materials": materials of the layer
    """

    all_mats = []

    comps = db.get("Components")
    materials = comps.get(layer_key)

    for mats in materials.values():
        all_mats.append(mats)

    # return materials
    return all_mats


layer, mat = find_mat_layer(dataBase, random_mat)
print(layer, mat)


mats = get_mats_of_layer(dataBase, layer)
print(mats[0])




"""
to run as a module
python -m src.mutation 
"""