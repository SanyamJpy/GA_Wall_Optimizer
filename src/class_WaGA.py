from src.dataBase_loader import getDataBase
from src.mutation import mutate_child
from src.wall_assembly import wallAssembly
from src.u_val import calc_U_val_Gwp_total
from src.fitness import fitness
import logging
import random
import os
import time
# os.environ['MPLBACKEND'] = 'TkAgg'
# matplotlib.use('TkAgg')
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PngImagePlugin').setLevel(logging.WARNING)
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


class WallAssemblyGA:
    def __init__(self, dataBase_path, population=30, generations=20, mut_start=0.5, mut_end=0.1):
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
        self.mutation_start_rate = mut_start
        self.mutation_end_rate = mut_end
        
        if not self.dataBase:
            raise RuntimeError("Data Base not loaded from the provided path.")
        
        # State tracking
        self.gen = 0 # current generation
        self.seenWalls = set() # to track unique wall assemblies

        # lists to store history
        self.all_U = []             # list of dicts: {wall_key: u_value}
        self.all_gwp = []           # list of dicts: {wall_key: gwp_value}
        self.all_fitness = []       # list of dicts: {wall_key: fitness_value}
        self.all_parents = []       # [ [[{},{}..], [{},{}..]], ... ] list of parents per generation
        self.all_parents_t = []     # [ [[{},{}..], [{},{}..]], ... ] list of parents' thicknesses per generation
        self.all_parents_U = []     # [ {p1, p2, p3}, {p1, p2, p3}, ... ] list of parents' U-values per generation
        self.all_parents_gwp = []   # [ {p1, p2, p3}, {p1, p2, p3}, ... ] list of parents' GWP-values per generation

        # list of thicknesses of ALL the wall assemblies per generation
        self.all_thicknesses = []   # [ [[{"L1": val},{"L2": val}..], [{},{}..]], ... ] (list of lists of lists of dicts) 

        # final results
        self.best_wall = None
        self.best_fitness = float('-inf')
        self.best_gen = -1


    def create_init_population(self):
        """
        Create the initial population of wall assemblies.

        RETURNS:
        "init_walls": list of initial wall assemblies (list of lists of dicts)
        """

        init_walls = []

        for i in range(self.population):
            wall = wallAssembly(self.dataBase, i)
            init_walls.append(wall)

        return init_walls
    

    def get_Vals(self, walls_list, gen=0, t=[]):

        """
        Calc u-value, gwp, of all the wallAssemblies

        EASIER IDENTIFICATION:
        for generation:0, keep it wall-0, wall-1, wall-2,....
        for generation:n, keep it g{n}_child-0, g{n}_child-1, g{n}_child-2,...

        INPUTS:
        "walls_list": list of wall assemblies (list of lists of dicts)
        "gen": generation number (int)
        "t": list of thicknesses of wall assemblies (list of lists of dicts): only for further(children) generations
        
        RETURNS:
        For gen=0:
        "init_walls_t": list of thicknesses of initial wall assemblies (list of lists of dicts)
        """
        # temp dicts for u, gwp values
        u_dict = {}
        gwp_dict = {}
        # fitness_dict = {}

        # list for initial generation thicknesses
        init_walls_t = []

        # Loop through each wall assembly and calculate U-val, Gwp
        for wall_idx, wall in enumerate (walls_list):

            "call u_val func"
            this_u, this_gwp, this_wall_t = calc_U_val_Gwp_total(wall, gen, t, wall_idx)

            """Key naming convention: wall-0, wall-1, ....  or g{n}_child-0, g{n}_child-1, ...."""
            wall_key = f"wall-{wall_idx}" if gen == 0 else f"g{gen}_child-{wall_idx}"


            # update dicts
            u_dict [wall_key] = this_u
            gwp_dict [wall_key] = this_gwp

            # This list only for initial generation
            if gen ==0:
                # update allWalls_t
                init_walls_t.append(this_wall_t)

        # logging.info(init_walls_t)

        # update history 
        self.all_U.append(u_dict)
        self.all_gwp.append(gwp_dict)

        #debug
        # print("\n")
        # print(f"all_U -> {all_U}")
        # print("-"*20)
        # print(f"all_Gwp -> {all_Gwp}")
        # print("-"*20)
        # print(f"all_fitness -> {all_fitness}")

        # return values based on generation
        if gen ==0:
            # as we define random thickns only for initial generation, so we need to return them
            return init_walls_t
        else:
            return None
        

    def calc_fitness(self, gen, max_gen):
        """
        Calculate fitness based on u-value and gwp
        

        """
        # temp dict
        fitness_dict = {}

        for wall_idx, (key, value) in enumerate(self.all_U[gen].items()):
            # get the u and gwp values for current wall for running gen
            this_u = value
            this_gwp = self.all_gwp[gen][key]

            "call fitness func"
            this_fitness = fitness (this_u, this_gwp, gen, self.generations)

            """Key naming convention: wall-0, wall-1, ....  or g{n}_child-0, g{n}_child-1, ...."""
            wall_key = f"wall-{wall_idx}" if gen == 0 else f"g{gen}_child-{wall_idx}"

            # update dict
            fitness_dict [wall_key] = this_fitness

        # update history
        self.all_fitness.append(fitness_dict)

        return None



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
        num_parents = 2

        # get the top n max fitness values
        sorted_fitness = sorted(this_gen_fitness_vals.items(), key= lambda x: x[1], reverse=True)
        top_parents = sorted_fitness[:num_parents]
        # print("\n")
        # print(top_2)


        print(f"\nTop {num_parents} fitness values:")
        
        for i, (wall_key, fit_val) in enumerate(top_parents):

            # get respective u and gwp values
            u_val = self.all_U[gen][wall_key]
            gwp_val = self.all_gwp[gen][wall_key]

            print("parent",i+1 )
            logging.info(f"{wall_key}: fitness -> {fit_val}")
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
        mutated_child, mutated_child_t = mutate_child(
            dataBase=self.dataBase, 
            child=child, 
            child_t=child_t, 
            mut_start=self.mutation_start_rate,
            mut_end=self.mutation_end_rate, 
            gen=self.gen, 
            max_gen=self.generations)

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

            # # pass only 1 parent as it is
            # if p_idx >0:
            #     print("Elitism: Added only 1 parent wall to next generation as is.")
            #     break

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

        # update history
        # self.all_thicknesses.append(childWalls_t)

        logging.info(f"Generated {len(childWalls_list)} unique children in generation {gen}")

        return childWalls_list, childWalls_t
    
    def get_best_wall_info(self):
        """
        Get the best wall assembly information
        """

        best_gen = self.best_gen

        # extract best wall key
        for key, value in self.all_fitness[best_gen].items():
            if value == self.best_fitness:
                # print(f"Best Wall key: {key}")
                best_wall_key = key

        # with best wall key, get respective u and gwp values
        best_u = self.all_U[best_gen][best_wall_key]
        best_gwp = self.all_gwp[best_gen][best_wall_key]

        # extract the index of the best wall from its key
        bw_idx = int(best_wall_key.split("-")[-1])

        # get the thicknesses of the best wall from all_thicknesses history
        all_layers_t = self.all_thicknesses[best_gen][bw_idx] 

        # total all the layer thicknesses
        total_wall_thickness = round(sum([list(layer_t.values())[0] for layer_t in all_layers_t]), 2)

        return {
            "best_gen": best_gen,
            "best_wall_key": best_wall_key,
            "best_u": best_u,
            "best_gwp": best_gwp,
            "best_fitness": self.best_fitness,
            "all_layers_t": all_layers_t,
            "total_best_wall_thickness": total_wall_thickness
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

            # calc u, gwp and get thicknesses
            walls_t = self.get_Vals(walls_list, gen)

            # calc fitness
            self.calc_fitness(gen, self.generations)

            # select parents
            parents, parentWalls_t = self.selectParents(walls_list, walls_t, gen)

            self.gen += 1

            # update history
            self.all_thicknesses.append(walls_t)

        # ========= Generations > 0: Crossover, Mutation, Selection ==========
        else:
            # get parents from previous gen
            parents = self.all_parents[-1]
            parentWalls_t = self.all_parents_t[-1]

            # create children
            childWalls_list, childWalls_t = self.create_unique_children(parents, parentWalls_t, gen)

            # calc u and gwp of children
            self.get_Vals(childWalls_list, gen, childWalls_t)

            "NEed a function for optimizing U-val"

            # calc fitness of children
            self.calc_fitness(gen, self.generations)

            # select parents for next gen
            parents, parentWalls_t = self.selectParents(childWalls_list, childWalls_t, gen)

            self.gen += 1

            # update history
            self.all_thicknesses.append(childWalls_t)   

            # return child walls and their thicknesses for next gen
            return childWalls_list, childWalls_t


    def run(self):
        """
        Run the full GA for max_generations
        """
        logging.info("======= Starting Wall Assembly Genetic Algorithm =======")

        "Record Time elapsed"
        # start the clock
        start_time = time.time()

        # run generations
        for gen in range(self.generations):
            self.run_generation(gen)

        # stop the clock
        end_time = time.time()

        # calculate time elapsed
        time_elapsed = end_time - start_time

        # print time elapsed
        print("\n")
        print(f"Time elapsed: {time_elapsed:.2f} seconds")

        print("\n")
        logging.info("=================Genetic Algorithm Completed =====================")
        logging.info(f">>>>>> Best Wall Assembly found in Generation {self.best_gen} with Fitness: {self.best_fitness}<<<<<<<<<")

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
            "all_parents_gwp": self.all_parents_gwp,
            "all_t": self.all_thicknesses,
            "SeenWalls": self.seenWalls
        }
    

    def plot_graphs(self):
        """
        Plots GWP and U of all parents over generations
        - X-axis: generations
        - Y-axis: GWP and U values
        - Each dot: a parent wall in that generation
        - Gold star: best wall assembly found
        """

        # get the best wall info 
        best_info = self.get_best_wall_info()
        best_allLayers_t = best_info["all_layers_t"]
        best_total_thickness = best_info["total_best_wall_thickness"]
        
        # check data availability
        if not self.all_parents_gwp or not self.all_parents_U:
            print("No GWP or U data available to plot.")
            return
        
        if not best_allLayers_t or best_total_thickness is None:
            print("No best wall thickness data available to plot.")
            return
        
        # number of generations
        generations = len(self.all_parents_gwp)

        # create subplots: ax1 = GWP, ax2 = U
        # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14,6))
        fig = plt.figure(figsize=(12, 7))
        gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], hspace=0.4, wspace=0.3)

        # left top: GWP evolution
        ax_gwp = fig.add_subplot(gs[0, 0])
        # right top: U evolution
        ax_u = fig.add_subplot(gs[0, 1])
        # bottom whole: Best wall thicknesses
        ax_wall = fig.add_subplot(gs[1, :])


        # adjust spacing between subplots
        # fig.tight_layout(pad=4.0)

        # color map
        cmap = plt.get_cmap("viridis", generations)

        # highlight best wall assembly
        best_info = self.get_best_wall_info()
        best_gen = best_info["best_gen"]
        best_gwp = best_info["best_gwp"]
        best_wall_key = best_info["best_wall_key"]
        best_U = best_info["best_u"]

        "-- Plot GWP Evolution -----------------------------"

        for gen_num, gwp_dict in enumerate(self.all_parents_gwp):
            color = cmap((gen_num-1)%10)

            for parent_key, gwp_val in gwp_dict.items():
                ax_gwp.scatter(gen_num, gwp_val, color=color, label=f"{parent_key}", marker='o', s=30, edgecolors='black', linewidth=0.5)

                # label under the dot
                ax_gwp.annotate(parent_key, (gen_num, gwp_val), textcoords="offset points", xytext=(0,-14), ha='center', fontsize=8)


        ax_gwp.scatter(best_gen, best_gwp, color='gold', marker='*', s=200, edgecolors='black', linewidth=2, zorder= 5)

        ax_gwp.annotate(f"Best: {best_wall_key}\n GWP= {best_gwp}", (best_gen, best_gwp), textcoords="offset points", xytext=(0,20), ha='center', fontsize=8, fontweight='bold', color= "darkred")

        # Final formatting
        ax_gwp.set_xticks(range(generations))

        ax_gwp.set_xlabel("Generations", fontsize=12)
        ax_gwp.set_ylabel("GWP Values", fontsize=12)
        ax_gwp.set_title("GWP Evolution Over Generations", fontsize=14, fontweight='bold')
        ax_gwp.grid(True, axis='y',linestyle='--', alpha=0.4)

        "-- Plot U Evolution -----------------------------"

        # loop through generations and plot each parent as dot
        for gen_num, U_dict in enumerate(self.all_parents_U):
            color = cmap((gen_num-1)%10)

            for parent_key, U_val in U_dict.items():
                ax_u.scatter(gen_num, U_val, color=color, label=f"{parent_key}", marker='o', s=30, edgecolors='black', linewidth=0.5)
                # label under the dot
                ax_u.annotate(parent_key, (gen_num, U_val), textcoords="offset points", xytext=(0,-14), ha='center', fontsize=8)
        

        ax_u.scatter(best_gen, best_U, color='gold', marker='*', s=200, edgecolors='black', linewidth=2, zorder= 5)

        ax_u.annotate(f"Best: {best_wall_key}\n U= {best_U}", (best_gen, best_U), textcoords="offset points", xytext=(0,20), ha='center', fontsize=8, fontweight='bold', color= "darkred")

        # Final formatting
        ax_u.set_xticks(range(generations))

        ax_u.set_xlabel("Generations", fontsize=12)
        ax_u.set_ylabel("U Values", fontsize=12)
        ax_u.set_title("U Evolution Over Generations", fontsize=14, fontweight='bold')
        ax_u.grid(True, axis='y',linestyle='--', alpha=0.4)
        
        "-- Plot Best Wall Assembly Thicknesses -----------------------------"
        # start stacking from y=0
        current_y = 0
        layer_colors = plt.get_cmap("tab20")
        width = 3  # fixed width for all layers
        x_text = width + width * 0.05  # x-position for text (right side)
        n_layers = len(best_allLayers_t)
        # precalc y-positions
        y_top = best_total_thickness * 0.95
        y_bottom = best_total_thickness * 0.05
        # evenly spaced y-positions for text
        y_positions = np.linspace(y_bottom, y_top, n_layers)

        for idx, layer in enumerate(best_allLayers_t):
            color = layer_colors(idx%20)

            mat, thick = list(layer.items())[0]
            rect = Rectangle((0, current_y), width, thick, color=color, edgecolor='black', linewidth=1)
            ax_wall.add_patch(rect)

            # # Text on right
            # y_center = current_y + thick / 2
            # # y_center = current_y + 0.1
            # if idx==0:
            #     ax_wall.text(width + width*0.05, y_center-0.05, f"Layer-{idx+1}:{mat}: {thick*1000}mm (Interior)", va='center',ha='left', fontsize=8, color= color)
            # else:
            #     ax_wall.text(width + width*0.05, y_center, f"Layer-{idx+1}:{mat}: {thick*1000}mm", va='center',ha='left', fontsize=8, color= color)

            # # update current_y for next layer
            # current_y += thick

            # get the respective idx pos for the text
            y_text = y_positions[idx] 
            # Add label with consistent style
            label = f"Layer-{idx+1}: {mat}: {thick*1000:.1f}mm"

            if idx == 0:
                label += " (Interior)"

            ax_wall.text(
                x_text, y_text,
                label,
                va="center", ha="left",
                fontsize=8, fontweight="normal", wrap=True, color=color,
                clip_on=False  # prevents clipping outside plot
            )

            # Update current_y for next rectangle
            current_y += thick

        # Annotate total thickness at the top center
        ax_wall.annotate(f"Total Thickness: {best_total_thickness * 1000}mm", (width/2, best_total_thickness*1.05), ha='center', fontsize=8, fontweight='bold')
        
        # Axis formatting
        ax_wall.set_xlim(0, width*1.35)
        ax_wall.set_ylim(0, best_total_thickness*1.1)
        ax_wall.set_title("Best Wall Assembly Layers", fontsize=14, fontweight='bold')

        # remove ticks and spines
        ax_wall.set_xticks([])
        ax_wall.set_yticks([])
        for spine in ax_wall.spines.values():
            spine.set_visible(False)

        # Add a thin outline around the entire wall
        outline = Rectangle((0, 0), width, best_total_thickness, fill=False, edgecolor='black', linewidth=1.2)
        ax_wall.add_patch(outline)

        "--- Show Plots --------------------------------------"

        plt.show()
        plt.close() # close the plot to free memory



        








