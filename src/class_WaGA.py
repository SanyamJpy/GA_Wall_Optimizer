from src.dataBase_loader import getDataBase
from src.mutation import mutate_child
from src.wall_assembly import wallAssembly
from src.u_val import calc_U_val_Gwp_total
from src.fitness import fitness
import logging
import random


class WallAssemblyGA:
    def __init__(self, dataBase_path, population=20, generations=10, mutation_rate=0.2):
        """
        Initialize the Genetic Algorithm for wall assembly optimization.

        INPUTS:
        - dataBase_path: path to JSON file (e.g., "dataBase/test_dataBase_2.json")
        - population: number of wall assemblies per generation
        - mutation_rate: percentage of layers to mutate (e.g., 0.2 = 20%)
        - max_generations: total number of generations to run
        """
    
        self.dataBase = getDataBase(dataBase_path)
        self.population = population
        self.generations = generations
        self.mutation_rate = mutation_rate
        
        if not self.dataBase:
            raise RuntimeError("Data Base not loaded from the provided path.")
        
        # State tracking
        self.gen = 0 # current generation
        self.seenWalls = set() # to track unique wall assemblies
        self.all_results = [] # to store results of all generations

        # lists to store history
        self.all_U = []             # list of dicts: {wall_key: u_value}
        self.all_gwp = []           # list of dicts: {wall_key: gwp_value}
        self.all_fitness = []       # list of dicts: {wall_key: fitness_value}
        self.all_parents = []       # [ [[{},{}..], [{},{}..]], ... ] list of parents per generation
        self.all_parents_t = []     # [ [[{},{}..], [{},{}..]], ... ] list of parents' thicknesses per generation
        self.all_parents_U = []     # [ {p1, p2, p3}, {p1, p2, p3}, ... ] list of parents' U-values per generation
        self.all_parents_gwp = []   # [ {p1, p2, p3}, {p1, p2, p3}, ... ] list of parents' GWP-values per generation

        # final results
        self.best_wall = None
        self.best_fitness = float('-inf')
        self.best_gen = -1


    def create_init_population(self):
        """Create the initial population of wall assemblies."""

        init_walls = []

        for i in range(self.population):
            walls = wallAssembly(self.dataBase, i)
            init_walls.append(walls)

        return init_walls
    

    def get_Vals(self, walls_list, gen=0, t=[]):

        """
        Calc u-value, gwp, and fitness of all the wallAssemblies

        EASIER IDENTIFICATION:
        for generation:0, keep it wall-0, wall-1, wall-2,....
        for generation:n, keep it g{n}_child-0, g{n}_child-1, g{n}_child-2,...

        INPUTS:
        "walls_list": list of wall assemblies (list of lists of dicts)
        "gen": generation number (int)
        "t": list of thicknesses of wall assemblies (list of lists of dicts): only for further(children) generations
        
        RETURNS:
        "all_fitness": list of dicts of fitness values of all wall assemblies
        For gen=0: also returns init_walls_t: list of thicknesses of all init_wall assemblies
        """
        # temp dicts for u, gwp, fitness values
        u_dict = {}
        gwp_dict = {}
        fitness_dict = {}

        # list for initial generation thicknesses
        init_walls_t = []

        # Loop through each wall assembly and calculate U-val, Gwp, fitness
        for wall_idx, wall in enumerate (walls_list):

            # logging.debug(type(wall))

            # for m in wall:
            #     logging.debug(m["name"])


            # print(wall)

            "call u_val func"
            this_u, this_gwp, this_wall_t = calc_U_val_Gwp_total(wall, gen, t, wall_idx)

            """Key naming convention: wall-0, wall-1, ....  or g{n}_child-0, g{n}_child-1, ...."""
            wall_key = f"wall-{wall_idx}" if gen == 0 else f"g{gen}_child-{wall_idx}"

            "call fitness func"
            this_fitness = fitness (this_u, this_gwp, gen, self.generations)

            # update dicts
            u_dict [wall_key] = this_u
            gwp_dict [wall_key] = this_gwp
            fitness_dict [wall_key] = this_fitness

            # allWalls_t is list only for initial generation
            if gen ==0:
                # update allWalls_t
                init_walls_t.append(this_wall_t)


        # update history 
        self.all_U.append(u_dict)
        self.all_gwp.append(gwp_dict)
        self.all_fitness.append(fitness_dict)

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
            return self.all_fitness, init_walls_t
        else:
            return self.all_fitness
        

    def wall_to_string(self, wall, wall_t, parent_toggle=False):

        """
        Convert wall assembly to string for easy comparison for dups

        INPUTS:
        "wall": wall assembly (list of dicts)
        "wall_t": thicknesses of wall assembly (list of dicts)
        "parent_toggle": explicitly to add parent walls to seenWalls set, so that children can be compared against them
        """

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
            self.seenWalls.add(signature)
        else:
            # return the signature for child walls
            return signature
        

    def selectParents(self, walls_list, walls_t, gen=0):

        """
        Select top 'n' wall assemblies as parents, based on fitness values

        INPUTS:
        "all_fitness_vals": list of dicts of fitness values of all wall assemblies
        "walls_list": wall assemblies (list of lists of dicts)
        "walls_t": list of thicknesses of wall assemblies (list of lists of dicts)
        "gen": generation number: used for getting specific gen Walls fitness from the 'all_fitness' list
        """
        # temp lists only for this gen parents
        parents = []
        parentWalls_t = []

        #  temp dicts for parents_U and parents_Gwp
        p_U_dict = {}
        p_Gwp_dict = {}

        # define which gen parents we are selecting
        this_gen_fitness_vals = self.all_fitness[gen]

        # no of parents to select
        num_parents = 3

        # get the top 3 max fitness values
        sorted_fitness = sorted(this_gen_fitness_vals.items(), key= lambda x: x[1], reverse=True)
        top_parents = sorted_fitness[:num_parents]
        # print("\n")
        # print(top_2)


        print(f"\nTop {num_parents} fitness values:")
        
        for i, (wall_key, fit_val) in enumerate(top_parents):
            print("parent",i+1 )
            logging.info(f"{wall_key}: fitness -> {fit_val}")

            # get respective u and gwp values
            u_val = self.all_U[gen][wall_key]
            gwp_val = self.all_gwp[gen][wall_key]

            logging.info(f"U-value: {u_val}, GWP-value: {gwp_val}")

            # update temp dicts
            p_U_dict[f"p{i+1}"] = u_val
            p_Gwp_dict[f"p{i+1}"] = gwp_val

            "Get the wallassembly and thicknesses corresponding to this wall_key"
            # split wall name to get index
            wall_index = int(wall_key.split("-")[1])
            # get the wall assemblies from the initial walls_list
            best_wall = walls_list[wall_index]

            # get respective thicknesses from allWalls_t
            pW_t = walls_t[wall_index]

            # get wall signature and add to seenWalls set
            # self.wall_to_string(best_wall, pW_t, True)

            # add the parent walls and their thicknesses to respective lists
            parents.append(best_wall)
            parentWalls_t.append(pW_t)



        # update history
        self.all_parents.append(parents)
        self.all_parents_t.append(parentWalls_t)
        self.all_parents_U.append(p_U_dict)
        self.all_parents_gwp.append(p_Gwp_dict)

        # update best wall
        best_fit = top_parents[0][1]
        if best_fit > self.best_fitness:
            self.best_fitness = best_fit
            self.best_wall = parents[0]
            self.best_gen = gen


        # debug
        print("\n")
        logging.info(f"Selected Parents for {gen+1}-Crossover:")
        for i, parent in enumerate(parentWalls_t):
            print(f"Parent {i+1}:")
            for layer_idx, layer in enumerate(parents[i]):
                print(f"- {layer['name']} with thickness {parent[layer_idx][layer['name']]}m")


        "list of lists of dicts"
        return parents, parentWalls_t
    

    def crossOver(self, parents, parentWalls_t, idx=0):

        """
        Perform crossover and mutation to create a child wall assembly

        INPUTS:
        "parents": list of parent wall assemblies (list of lists of dicts)
        "parentWalls_t": list of thicknesses of parent wall assemblies (list of lists of dicts)
        "idx": index of the child wall assembly (for debugging purposes)

        RETURNS:
        "mutated_child": mutated child wall assembly (list of material dicts)
        "mutated_child_t": mutated thicknesses of the child wall assembly (list of dicts)
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

        " Perform mutation"
        mutated_child, mutated_child_t = mutate_child(self.dataBase, child, child_t, self.gen, self.generations)

        # # debug------------------------------------------------------------------
        # print("Before Mutation:")
        # # print(f"\nChild Wall-{idx}:")
        # for i, layer in enumerate(child):
        #     print(f"- {layer['name']} with thickness {child_t[i][layer['name']]}m")

        # print("\n")    
        # print("After Mutation:")
        # for i, layer in enumerate(mutated_child):
        #     print(f"- {layer['name']} with thickness {mutated_child_t[i][layer['name']]}m")
        

        "list of dicts"
        return mutated_child, mutated_child_t
    

    def create_unique_children(self, parents, parentWalls_t, gen):
        """
        Create unique child walls until population is met

        INPUTS:
        "parents": list of parent wall assemblies (list of lists of dicts)
        "parentWalls_t": list of thicknesses of parent wall assemblies (list of lists of dicts)
        "gen": current generation number (int)

        RETURNS:
        "childWalls_list": list of unique child wall assemblies (list of lists of dicts)
        "childWalls_t": list of thicknesses of unique child wall assemblies (list of lists of dicts)
        """

        childWalls_list = []
        childWalls_t = []

        "ELITISM: preserve the parents walls----------------------------------"
        # taking the latest parents
        for p_idx, parent in enumerate(self.all_parents[-1]):
            childWalls_list.append(parent)
            childWalls_t.append(self.all_parents_t[-1][p_idx])
            # add parent wall signatures to seenWalls set
            self.wall_to_string(parent, self.all_parents_t[-1][p_idx], True)

        # loop until we have desired population of unique walls
        attempts = 0
        max_attempts = self.population * 50  # to avoid infinite loop

        while len(childWalls_list) < self.population and attempts < max_attempts:

            # perform crossover to create child wall
            childWall, childWall_t = self.crossOver(parents, parentWalls_t)
            # get wall signature
            wall_signature = self.wall_to_string(childWall, childWall_t)

            # check for duplicates
            if wall_signature not in self.seenWalls:
                # add to seen set and child walls list
                self.seenWalls.add(wall_signature)
                childWalls_list.append(childWall)
                # store thicknesses
                childWalls_t.append(childWall_t)
                # print(f"Child Wall Signature: {wall_signature}")
            else:
                # print("Duplicate child wall found. Retrying...")
                pass
            
            attempts += 1


        logging.info(f"Generated {len(childWalls_list)} unique children in generation {gen}")

        return childWalls_list, childWalls_t
    
    """NEED TO ADD THE THICKNESS OF THE BEST WALL AS WELL---------FOR THAT STORE ALL THE THICKNESS--------------------------------------------"""
    def get_best_wall_info(self):
        """
        Get the best wall assembly information
        """

        best_gen = self.best_gen

        for key, value in self.all_fitness[best_gen].items():
            if value == self.best_fitness:
                # print(f"Best Wall key: {key}")
                best_wall_key = key

        best_u = self.all_U[best_gen][best_wall_key]
        best_gwp = self.all_gwp[best_gen][best_wall_key]

        return {
            "best_gen": best_gen,
            "best_wall_key": best_wall_key,
            "best_u": best_u,
            "best_gwp": best_gwp,
            "best_fitness": self.best_fitness
        }

    def run_generation(self,gen):
        """
        Run one full generation
        1. Create children
        2. Calc fitness
        3. Select parents for next gen
        """
        print("\n")
        logging.info(f"---Starting Generation {gen} ---")

        # ========= Generations = 0 =========
        if gen == 0:
            # create initial population
            walls_list = self.create_init_population()

            # calc fitness and get thicknesses
            all_fitness, walls_t = self.get_Vals(walls_list, gen)

            # select parents
            parents, parentWalls_t = self.selectParents(walls_list, walls_t, gen)

            self.gen += 1

        # ========= Generations > 0: Crossover, Mutation, Selection ==========
        else:
            # get parents from previous gen
            parents = self.all_parents[-1]
            parentWalls_t = self.all_parents_t[-1]

            # create children
            childWalls_list, childWalls_t = self.create_unique_children(parents, parentWalls_t, gen)

            # calc fitness
            all_fitness = self.get_Vals(childWalls_list, gen, childWalls_t)

            # select parents for next gen
            parents, parentWalls_t = self.selectParents(childWalls_list, childWalls_t, gen)

            self.gen += 1

            # return child walls and their thicknesses for next gen
            return childWalls_list, childWalls_t


    def run(self):
        """
        Run the full GA for max_generations
        """
        logging.info("\n=== Starting Wall Assembly Genetic Algorithm ===")

        for gen in range(self.generations):
            self.run_generation(gen)

        print("\n")
        logging.info("\n=== Genetic Algorithm Completed ===")
        logging.info(f"Best Wall Assembly found in Generation {self.best_gen} with Fitness: {self.best_fitness}")

        return {
            "best_gen": self.best_gen,
            "best_wall": self.best_wall,
            "best_fitness": self.best_fitness,
            "all_U": self.all_U,
            "all_gwp": self.all_gwp,
            "all_fitness": self.all_fitness,
            "all_parents": self.all_parents,
            "all_parents_t": self.all_parents_t,
            "all_parents_U": self.all_parents_U,
            "all_parents_Gwp": self.all_parents_gwp,
            "all_results": self.all_results,
            "SeenWalls": self.seenWalls
        }








