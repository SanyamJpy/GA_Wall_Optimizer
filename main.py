# python main.py

from src.dataBase_loader import getDataBase
from src.wall_assembly import wallAssembly
from src.u_val import calc_U_val_Gwp_total
from src.fitness import fitness
import logging
import random


# load dataBase
dataBase = getDataBase()
if not dataBase:
    print("Data Base not loaded")
    print("x-"*20)
    exit()

# ---------------------------------------------------------------

"GA parameters"
population = 20

gen = 0  # initial generation
# set to track seen wall signatures; to avoid duplicates
seenWalls = set()


# initialize list to store wall assemblies
init_walls_list = []
# list to store thicknesses of initial wall assemblies
init_walls_t = []

"""
lists to store all u-values, gwp-values and fitness values of all wall assemblies thru gens: (list of dicts)
see pg.8 for understanding 
"""
all_U = []
all_Gwp = []
all_fitness = []

# list to store the best wall assemblies as parents
parents = []
# list to store chosen thicknesses of parent walls
parentWalls_t= []

"""
lists to store parents u and gwp values for each generation: (list of dicts)
see pg.7 for understanding 
"""
all_parents_U = []
all_parents_Gwp = []

# =============================================================================================

# Loop to create multiple wall assemblies: Initial Population
for i in range(population):
    walls= wallAssembly(dataBase, i)
    # print(walls)
    # print("-"*20)

    init_walls_list.append(walls)


def get_Vals(walls_list, gen=0, t=[]):
    """
    func to get all u-values and gwp-values of all the wallAssemblies

    EASIER IDENTIFICATION:
    for generation:0, keep it wall-0, wall-1, wall-2,....
    for generation:n, keep it g{n}_child-0, g{n}_child-1, g{n}_child-2,...

    INPUTS:
    "walls_list": list of wall assemblies (list of lists of dicts)
    "gen": generation number (int)
        
    """
    # temp dicts for u, gwp, fitness values
    u_dict = {}
    gwp_dict = {}
    fitness_dict = {}

    # Loop through each wall assembly and calculate U-val, Gwp, fitness
    for wall_idx, wall in enumerate (walls_list):

        # logging.debug(type(wall))

        # for m in wall:
        #     logging.debug(m["name"])


        # print(wall)

        "call u_val func"
        this_u, this_gwp, this_wall_t = calc_U_val_Gwp_total(wall, gen, t, wall_idx)

        # print("u_total" , u_total, "gwp_total", gwp_total)

        

        # if its initial generation
        if gen ==0:
            wall_key = f"wall-{wall_idx}"
        else:
            # for further generations
            wall_key = f"g{gen}_child-{wall_idx}"


        "call fitness func"
        this_fitness = fitness (this_u, this_gwp)

        # update dicts
        u_dict [wall_key] = this_u
        gwp_dict [wall_key] = this_gwp
        fitness_dict [wall_key] = this_fitness

        # allWalls_t is list only for initial generation
        if gen ==0:
            # update allWalls_t
            init_walls_t.append(this_wall_t)


    # update main lists
    all_U.append(u_dict)
    all_Gwp.append(gwp_dict)
    all_fitness.append(fitness_dict)

    #debug
    # print("\n")
    # print(f"all_U -> {all_U}")
    # print("-"*20)
    # print(f"all_Gwp -> {all_Gwp}")
    # print("-"*20)
    # print(f"all_fitness -> {all_fitness}")

    # return values based on generation
    if gen ==0:
        # as we define random thickns only for initial generation, so we need to return allWalls_t too
        return all_fitness, init_walls_t
    else:
        return all_fitness
    

init_walls_fitness, init_walls_t = get_Vals(init_walls_list)

# print(allWalls_t)



def wall_to_string(wall, wall_t, parent_toggle=False):
    """
    func to convert wall assembly to string for easy comparison for dups

    INPUTS:
    "wall": wall assembly (list of dicts)
    "wall_t": thicknesses of wall assembly (list of dicts)
    "parent_toggle": explicitly to add parent walls to seenWalls set, so that children can be compared against them
    """
    

    # alternative way
    signature_parts = []

    # zip() -> loop thru both lists simultaneously
    for layer, thick in zip(wall, wall_t):
        mat = layer["name"]
        mat_thick = str(thick[mat])
        signature_parts.append(f"{mat}:{mat_thick}")

    signature = "|".join(signature_parts)
    # print(signature)

    # if it is a parent wall, directly add to seenWalls set
    if parent_toggle:
        seenWalls.add(signature)
        # print(seenWalls)
    else:
        # return the signature for child walls
        return signature

"""
NEEDS TO BE UPDATED -----------------------------------------------------------------------
parents[] should be called again inside the function, to only contain the current gen parents
"""
def selectParents(all_fitness_vals, walls_list, allWalls_t, gen=0):
    """
    func to select top 2 wall assemblies as parents, based on fitness values

    INPUTS:
    "all_fitness_vals": list of dicts of fitness values of all wall assemblies
    "walls_list": wall assemblies (list of lists of dicts)
    "allWalls_t": list of thicknesses of all wall assemblies (list of lists of dicts)
    "gen": generation number: used for getting specific gen Walls fitness from the 'all_fitness' list
    """

    # # temp dicts for parents_U and parents_Gwp
    p_U_dict = {}
    p_Gwp_dict = {}

    # # temp list for storing dicts before appending to main lists
    # p_U_list = []
    # p_Gwp_list = []

    # define which gen parents we are selecting
    this_gen_fitness_vals = all_fitness[gen]

    # no of parents to select
    num_parents = 3

    # get the top 3 max fitness values
    sorted_fitness = sorted(this_gen_fitness_vals.items(), key= lambda x: x[1], reverse=True)
    top_parents = sorted_fitness[:num_parents]
    # print("\n")
    # print(top_2)


    # debug
    print(f"\nTop {num_parents} fitness values:")
    for i, (wall, fit_val) in enumerate(top_parents):
        print("parent",i+1 )
        logging.info(f"{wall}: fitness -> {fit_val}")
        # get respective u and gwp values
        u_val = all_U[gen][wall]
        gwp_val = all_Gwp[gen][wall]
        logging.info(f"U-value: {u_val}, GWP-value: {gwp_val}")

        # update temp dicts
        p_U_dict[f"p{i+1}"] = u_val
        p_Gwp_dict[f"p{i+1}"] = gwp_val


    # # update temp lists
    # p_U_list.append(p_U_dict)
    # p_Gwp_list.append(p_Gwp_dict)

    # append to main lists
    all_parents_U.append(p_U_dict)
    all_parents_Gwp.append(p_Gwp_dict)

    # # debug
    # print("\n")
    # logging.info("Selected Parents U and Gwp values:")
    # print(all_parents_U)
    # print(all_parents_Gwp)

    # get materials of the best wall assemblies
    for wall_no, fit_val in top_parents:

        # split wall name to get index
        wall_index = int(wall_no.split("-")[1])
        # get the wall assemblies from the initial walls_list
        best_wall = walls_list[wall_index]
        # print(best_wall)

        # get respective thicknesses from allWalls_t
        pW_t = allWalls_t[wall_index]

        # get wall signature and add to seenWalls set
        wall_to_string(best_wall, pW_t, True)

        # add the parent walls to parents list
        parents.append(best_wall)
        # append both parentWalls thicknesses to parentWalls_t
        parentWalls_t.append(pW_t)

    # debug
    print("\n")
    logging.info("Selected Parents for Crossover:")
    for i, parent in enumerate(parentWalls_t):
        print(f"Parent {i+1}:")
        for layer_idx, layer in enumerate(parents[i]):
            print(f"- {layer['name']} with thickness {parent[layer_idx][layer['name']]}m")

    # debug
    # print("\nParent Walls Thicknesses:")
    # for i, p_t in enumerate(parentWalls_t):
    #     print(f"Parent {i+1} Thicknesses: {p_t}")

    "list of lists of dicts"
    return parents, parentWalls_t

# call selectParents func
parents, parentWalls_t = selectParents(init_walls_fitness, init_walls_list, init_walls_t)

# print(parents)

# print(parents[0][0])


def crossOver(parents, parentWalls_t, idx=0):

    """
    func to perform crossover between 2 parents and create a child wall assembly

    INPUTS:
    "parents": list of parent wall assemblies (list of lists of dicts)
    "parentWalls_t": list of thicknesses of parent wall assemblies (list of lists of dicts)
    "idx": index of the child wall assembly (for debugging purposes)
    """
    
    # lists to store child mats and their thickness
    child = []
    child_t = []

    # get number of parents
    num_parents = len(parents)

    # number of layers in a wall assembly
    num_layers = len(parents[0]) 


    # for each layer, select randomly from any parent
    for layer_idx in range(num_layers):

        # choose a random parent
        parent_idx = random.randint(0, num_parents-1)

        # get material and thickness from parent
        mat = parents[parent_idx][layer_idx]
        thick = parentWalls_t[parent_idx][layer_idx]

        # append to child wall assembly
        child.append(mat)
        child_t.append(thick)


    # # debug
    # print(f"\nChild Wall-{idx}:")
    print("\n")
    print("child ->", child[0])
    # print("child_T ->", child_t)

    # for i, layer in enumerate(child):
    #     print(f"- {layer['name']} with thickness {child_t[i][layer['name']]}m")

    "list of dicts"
    return child, child_t






# initialize list to store wall assemblies
childWalls_list = []
childWalls_t = []


"NEEDS TO BE UPDATEDDD -----------------------------------------------------------------------"
def create_uniqueWalls(sourceWalls_list, gen):
    """
    func to create unique  wall assemblies 
    gen_0: create initial unique population
    gen_n: create children from parents until desired population of unique walls is reached
    """
    pass

# loop until we have desired population of unique walls
i = 0
max_attempts = population * 50  # to avoid infinite loop

while len(childWalls_list) < population and i < max_attempts:

    # perform crossover to create child wall
    childWall, childWall_t = crossOver(parents, parentWalls_t, len(childWalls_list))
    # get wall signature
    wall_signature = wall_to_string(childWall, childWall_t)

    # check for duplicates
    if wall_signature not in seenWalls:
        # add to seen set and child walls list
        seenWalls.add(wall_signature)
        childWalls_list.append(childWall)
        # store thicknesses
        childWalls_t.append(childWall_t)
        # print(f"Child Wall Signature: {wall_signature}")
    else:
        # print("Duplicate child wall found. Retrying...")
        pass
    
    i += 1

# a generation created
gen += 1



# logging.info(childWalls_t)

for idx, child in enumerate(childWalls_t):
    print("\n")
    logging.info(f"Child Wall-{idx}:")
    for layer_idx, layer in enumerate(childWalls_list[idx]):
        print(f"- {layer['name']} with thickness {child[layer_idx][layer['name']]}m")
     
child_fitness = get_Vals(childWalls_list, gen, childWalls_t)

# select parents for next generation
g2_parents, g2_parentWalls_t = selectParents(child_fitness, childWalls_list, childWalls_t, gen)

# print("\n")
# print(f"all_U -> {all_U}")
# print("-"*20)
# print(f"all_Gwp -> {all_Gwp}")
# print("-"*20)
# print(f"child_fitness -> {child_fitness}")

print("\n")
logging.info("All Parents U and Gwp values:")
print(f"U-vals->{all_parents_U}")
print(f"Gwp-vals->{all_parents_Gwp}")

# print("\n")
# print(parents[5])



# print("\n")
# print(f"Parents for next generation: {g2_parents}")

# print("\n")
# print(f"Thicknesses for next generation: {g2_parentWalls_t}")




# print(all_parents_U[0])
# for p, v in all_parents_U[0].items():
#     print(p)
#     print(v)

# print(childWalls_list)