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
    func to find the layer of the material(to be mutated) in the dataBase

    'INPUTS':
    "db": dataBase
    "random_mat": random material chosen from the child wall assembly

    'RETURNS':
    "layer_key": layer_key of the material
    "mat_key": material_key of the material dict
    """

    # get all the layers and there mats from the dataBase
    comps = db.get("Components")
    # get the id of the material to be mutated
    target_id = random_mat.get("id")

    if target_id is None:
        logging.error("Target ID is None")
        return None
    
    # loop thru the layers and there materials
    for layer_key, materials in comps.items():
        for mat_key, mat_dict in materials.items():
            if mat_dict.get("id") == target_id:
                # return the layer_key and mat_key
                return layer_key, mat_key
            
    logging.error("Material not found in dataBase")
    exit()



def get_mats_of_layer(db, layer_key):

    """
    func to get all the materials of the found layer

    'INPUTS':
    "db": dataBase
    "layer_key": layer of the material

    'RETURNS':
    "materials": materials of the layer
    """

    all_mats = []

    comps = db.get("Components")
    # get all the mat_keys and mat_dicts of that layer
    materials = comps.get(layer_key)

    # get only the mat_dicts and append to a list
    for mats in materials.values():
        all_mats.append(mats)

    # return materials
    return all_mats


def get_new_material(dataBase, random_mat):
    """
    func to get a new material from the same layer as the material to be mutated

    'INPUTS':
    "dataBase": dataBase
    "random_mat": material to be mutated
    "layer_key": layer of the material to be mutated

    'RETURNS':
    "new_mat": new material(dict) from the same layer: {...}
    """

    # get the layer_key of the material to be mutated
    layer_key, mat = find_mat_layer(dataBase, random_mat)

    # get all the materials of that layer
    mats = get_mats_of_layer(dataBase, layer_key)

    for mat in mats:
        print(mat.get("name"))

    # choose a new material randomly from that layer
    new_mat = random.choice(mats)

    # check if the new material is different from the old one
    while new_mat.get("id") == random_mat.get("id"):
        new_mat = random.choice(mats)

    # debug
    logging.info(f"Mutated from {random_mat.get('name')} to {new_mat.get('name')}")

    return new_mat



# Caling functions------------------------------------------------

random_mat = {'name': 'MAGOXX_Board', 'id': '03_02', 'factor': 1.21, 'u-value': 3.93, 'u-value_unit': 'W/m2.K', 'r-value': 0.084, 'r-value_unit': 'm2.K/W', 'lambda': 0.0, 'lambda-value_unit': 'W/m.K', 'thickness_init': 9, 'thickness_range': [], 'density': 1100, 'unit': 'm2', 'A1-A3': 21.1, 'A4': 2.71, 'A5': 0.745, 'C1': 0.032, 'C2': 0.106, 'C3': 0.0, 'C4': 0.326, 'D': -0.028}

new_mat = get_new_material(dataBase, random_mat)




"""
to run as a module
python -m src.mutation 
"""