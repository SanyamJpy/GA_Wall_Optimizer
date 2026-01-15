from .dataBase_loader import getDataBase
import random
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s:%(lineno)d - %(message)s'
)

filePath = "dataBase/test_dataBase_2.json"
# load dataBase
dataBase = getDataBase(filePath)

# conversion mm to m
conv = 1/1000

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


def mutate_child(dataBase, child, child_t, mutation_rate=0.2):
    """
    Mutates a random no of materials in the child wall assembly based on the mutation rate

    'INPUTS':
    "dataBase": dataBase
    "child": child wall assembly (list of material dicts)
    "child_t": thicknesses of the child wall assembly (list of dicts)
    "mutation_rate": float between 0 and 1 (eg: 0.2 = 20% mutation)

    'RETURNS':
    "mutated_child": mutated child wall assembly (list of material dicts)
    "mutated_child_t": mutated thicknesses of the child wall assembly (list of dicts)
    """

    # make copies of the child and child_t to mutate
    mutated_child = child[:]
    mutated_child_t = child_t[:]

    # no of layers
    num_layers = len(mutated_child)
    print("\n")
    logging.info(f"Number of layers in child wall assembly: {num_layers}")

    # how many mats to mutate?
    num_to_mutate = int(num_layers * mutation_rate)
    print(num_layers * mutation_rate)
    print("layers to mutate:", num_to_mutate)
    # fallback to at least 1 mutation
    if num_to_mutate == 0:
        num_to_mutate = 1

    # choose random indices to mutate
    "random.sample(population, k): chooses k unique random elements from a population sequence or set."
    indices_to_mutate = random.sample(range(num_layers), num_to_mutate)
    
    logging.info(f"Mutating {num_to_mutate} layers at indices: {indices_to_mutate}")
    print("\n")

    # loop over each idx to mutate
    for idx in indices_to_mutate:

        # old material dict
        old_mat = mutated_child[idx]
        old_mat_t = mutated_child_t[idx]

        # find layer of the old material
        layer_key, mat_key = find_mat_layer(dataBase, old_mat)
        if layer_key is None:
            logging.warning(f"Material {old_mat.get('name')} not found in dataBase. Skipping.")
            continue

        # get all materials of that layer
        all_mats_of_layer = get_mats_of_layer(dataBase, layer_key)

        # choose a new material randomly from that layer
        new_mat = random.choice(all_mats_of_layer)
        # ensure new material is different
        while new_mat.get("id") == old_mat.get("id"):
            new_mat = random.choice(all_mats_of_layer)

        # pick a random thickness within the range of the new material
        thickness_range = new_mat.get("thickness_range", [])
        # check if thickness_range is valid and has vals
        if not thickness_range:
            # use the init_thickness
            new_thickness = new_mat.get("thickness_init")

        else:
            new_thickness = random.choice(thickness_range)

        # Update both lists at the same idx
        mutated_child[idx] = new_mat
        mutated_child_t[idx] = {new_mat.get("name"): round(new_thickness * conv, 4)}

        # logging.info(f"Mutated Layers {idx}: {old_mat.get('name')} -> {new_mat.get('name')}, Thickness: {old_mat_t} -> {mutated_child_t[idx]}")

    return mutated_child, mutated_child_t

# Caling functions------------------------------------------------



"""
to run as a module
python -m src.mutation 
"""