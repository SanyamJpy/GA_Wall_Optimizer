from .wall_assembly import wallAssembly
from .dataBase_loader import getDataBase
from .__name import main
import random
import logging

"configure debugging with lineno and filename"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s:%(lineno)d - %(message)s'
)


# m to mm conversion
conv = 1/1000
debug = False




"func to calculate total u-value and total gwp"
def calc_U_val_Gwp_total(wallAssembly, gen=0, t=[], wall_idx=0):
    
    """
    u_total = 1 / r_total

    INPUT:
    wallAssembly: list of dicts

    """
    r_total, gwp_all, wall_t =calc_R_val(wallAssembly, gen, t, wall_idx)

    u_total = round(1 / r_total, 4)

    gwp_total = round(sum(gwp_all), 4)
    
    if debug:
        print("--"*20)
        # print("u_total:",u_total)
        # print('gwp_total:',gwp_total)

        # logging.info("u_total:" u_total)
        logging.info(f"gwp_total: {gwp_total}")
        logging.debug(f"U value: {u_total}")
    
    return u_total, gwp_total, wall_t



"func to calculate total r-value"
def calc_R_val(wallAssembly, gen=0, childWalls_t=[], wall_idx=0):

    """
    r_total = r_values + r_si + r_se

    --> r_values : sum of all r-values of all the materials
    --> r_si : 0.13  Internal air resistance
    --> r_se : 0.04  External air resistance

    --> r = thickness / lambda
    
    INPUT:
    wallAssembly: list of dicts (meaning: a single Wall as list with all its materials as dicts)
    gen: generation number (int)
    childWalls_t: list of thickness dicts for each wall assemblies -> for further generations
    wall_idx: index of the wall assembly -> for further generations (int) (tells which wall we are referring to from the list)
    """
    # surface resistance vals
    r_si = 0.13
    r_se = 0.04

    # total r-value
    r_total = r_si + r_se

    # list to store all gwp_sums
    gwp_all =[]

    # list to store thicknesses of all mats in this wall assembly
    wall_t = []

    # print(childWalls_t)

    # print("\n")
    # logging.info("r_func started......")
    
    for mat_idx, mat in enumerate(wallAssembly):

        if debug:
            logging.info(mat['name'])

        # print("\n")
        # print("i:", mat_idx)
        # print("Material:", mat['name'])

        " For initial generation, selc random thickness "
        if gen==0:
            "selc random thickness from list"
            # if no range provided
            if len(mat["thickness_range"]) == 0:

                # selc the init thickness
                mat_t = round(mat["thickness_init"] * conv, 4)
                if debug:
                    print("mat_t_init=", mat_t)
            else:

                # selc random thickness from list
                random_t_int = random.randint(0, len(mat["thickness_range"])-1)
                random_t = mat["thickness_range"][random_t_int]
                # print("random_t=", random_t)

                #convert mm -> m
                mat_t = round(random_t * conv, 4)
                if debug:
                    print("mat_t_chosen=", mat_t)

            # append it as a dict of name:thickness chosen
            wall_t.append({mat['name']: mat_t})

        else:
            "for further generations, take the selected thickness, from the childWalls_t"
            temp_mat_t = []
            # loop for each wall in childWalls_t
            # print("childWalls_t:", childWalls_t)
            # for idx, wall in enumerate(childWalls_t): 
                # print("\n")
                # print("idx:", idx)  

                # loop for each layer in that wall
                # for idx2, layer in enumerate(wall):
                    # print("\n")
                    # print("idx2:", idx2)
                    # print("layer:", layer)

                    # append in a list
                    # temp_mat_t.append(layer)
                    # assign mat and mat_t
                    # mat, mat_t = next(iter(layer.items()))
                    # print(f"mat_name:{mat}, mat_t:{mat_t}")

                    # check if mat name matches
                    # if mat['name'] == list(layer.keys())[0]:
                    #     mat_t = layer[mat['name']]
                    #     # wall_t.append({mat['name']: mat_t})
                        
                    #     print("matched mat name:", mat['name'])
                    #     print("mat_t_selected:", mat_t)

            "Refer pg.6 from notes for undersstanding"

            # print("idx:", wall_idx)
            # logging.info("child walls r-Val calc started.......")
            
            # print(childWalls_t[wall_idx][mat_idx])
            mat_t = childWalls_t[wall_idx][mat_idx][mat['name']]

            # thickness of the mat of the respective child wall
            # print("mat_t_selected:", mat_t)

            # as we reach the last mat of the wall, update wall_idx to point to next wall for next iteration; otherwise, it will keep looking in the same wall
            if mat_idx == len(wallAssembly)-1:
                # print("update idx")
                wall_idx +=1
            
            

        # print("Final mat_t used:", mat_t)
            
        # CCheck if r-value is ND or 0 and lambda is not 0.0
        if (mat['r-value']== None or mat['r-value'] == 0.0) and mat['lambda'] != 0.0 :
            
            # print("using lambda....")
            " r = thickness / lambda "
            r = mat_t / mat["lambda"]
            r_total += r

            if debug:
                print("lambda:", mat["lambda"])
                print("r:",r)

            # if r-val present, take it
        else:
            # print("we have r val")
            r_total += mat["r-value"]
            if debug:
                print("we have r val")
                print("r:",mat["r-value"])
            # print("--"*20)

        """
        Also need to check if no r-val is provided
        dann, use 1/u-val and add to r_total------------------------------------------------------

        """

        # logging.info("matt ", mat_t)
        mat_amt = calc_Mat_amount(mat, mat_t)
        gwp_sum = gwpCalc(mat, mat_amt)
        gwp_all.append(gwp_sum)

    
    if debug:
        print('r_total:',r_total )
        print('gwp_all_mat_sum:',gwp_all)
    

    # return {"r_total":r_total, "gwp_all":gwp_all}

    # logging.info("r_func ended successfully")
    return r_total, gwp_all, wall_t


" func to calculate GWP "
def gwpCalc(material, mat_amt):

    """
    Calculating GWP of the wall assembly

    S1: calc gwp_sum for each mat with t
    gwp_sum_material = (Σ gwp_per_unit) * amount_of_material

    S2: calc total gwp as the sum of all the gwp of the materials in the assembly
    gwp_total = Σgwp_sum_material

    """


    gwp_sum = None

    gwp_per_unit = material["A1-A3"] + material["A5"] + material["C2"] + material["C3"] - material["D"]
    gwp_sum = gwp_per_unit * mat_amt

    if debug:
        # print("gwp_per_unit:",gwp_per_unit)
        print("gwp_mat_sum:",gwp_sum)
        print("--"*20)
 

    return gwp_sum


" func to calculate Amount of mat "
def calc_Mat_amount(mat, mat_t_selc):

    """
    ** To calc the amount of material as per thickness**
    area = 1m^2
    volume = area * thickness
    mass = volume * density (kg)

    """

    # area is 1m2
    area = 1
    # init thickness
    # if its not null, take init thickness
    if mat["thickness_init"] is not None:
        mat_t_init = mat["thickness_init"] * conv
    else:
        # if thickness_init is None, use the selected thickness
        mat_t_init = mat_t_selc

    """ AREA UNIT """
    if mat["unit"] == "m2" or mat["unit"] == "m^2" or mat["unit"] == "area":

        "Calc the scaling factor as per thickness"
        # if same as that of init
        if mat_t_selc == mat_t_init:

            mat_amount = 1
        # get the scale factor as per thickness selcted
        else:
            # m2
            mat_amount = mat_t_selc / mat_t_init


        """ VOLUME UNIT """
    elif mat["unit"] == "m3" or mat["unit"] == "m^3" or mat["unit"] == "volume":

        # m3
        mat_amount = mat_t_selc * area 


        """ WEIGHT UNIT """
    else:
        
        # get volume as per selected thickness
        volume = area * mat_t_selc

        # Now, if func_unit is tonne
        if mat["unit"] == "tonne" or mat["unit"] == "ton":

            # divide by 1000 to get kg
            mat_amount = (volume * mat["density"]) / 1000
        
        else:
            # kg
            volume = area * mat_t_selc
            mat_amount = volume * mat["density"]

    if debug:
        print("mat_amount-{}:".format(mat["unit"]), mat_amount)
        print("--"*20)



    return mat_amount

if __name__ == "__main__":   
    debug = True   
    
    wall_assem = main()

    print("u_val file executed......")
    print ("=="*50)
    
    # calc_U_val_Gwp_total(wall_assem)
    print ("=="*50)



# python -m src.u_val