from .u_val import calc_U_val_Gwp_total
from .__name import main
# from wall_assembly import wall_assem
import logging

debug = False

# u_total, gwp_total = calc_U_val_Gwp_total(wall_assem)




def fitness (u_actual, gwp_actual):

    """
    LOWER THE FITNESS => BETTER GENOME

    Constraint:
    u_min <= u_total <= u_max
    
    if constraint:
    fitness= gwp_total
    else:
    fitness= gwp_total + penalty

    penalty => depends on the amount of violation of the constraint

    """

    u_target = 0.14
    buffer = 0.1 #10%

    u_min = u_target * (1 - buffer) 
    u_max = u_target * (1 + buffer)

    # u_actual = u_total
    # gwp_actual = gwp_total

    if u_min <= u_actual <= u_max:
        
        u_debug = "in range..."

        # round off to 2 decimal places
        # fitness = round((1/gwp_actual), 2)
        fitness = round(1/gwp_actual, 4)
    else:
        
        u_debug = "out of range..."

        violation = (u_actual - u_max) if u_actual > u_max else (u_min - u_actual)
        weight = 1000
        penalty = weight * violation
        fitness = round(1/(gwp_actual + penalty), 4)

    if debug:

        print("U is :", u_debug)
        logging.info(f"fitness: {fitness}")



    return fitness


if __name__ == "__main__":
    debug = True

    wall_assem = main()

    u_total, gwp_total, wall_t = calc_U_val_Gwp_total(wall_assem)

    print("fitness file executed......")
    print ("=="*50)
    print ("u_total:",u_total)
    print ("gwp_total:",gwp_total)
    print("-"*50)

    fitness (u_total, gwp_total)

    