from .u_val import calc_U_val_Gwp_total
from .__name import main
# from wall_assembly import wall_assem
import logging

debug = False

# u_total, gwp_total = calc_U_val_Gwp_total(wall_assem)




def fitness (u_actual, gwp_actual, gen, max_gen):

    """
    LOWER THE FITNESS => BETTER GENOME

    Constraint:
    u_min <= u_total <= u_max
    
    adaptive penalty => depends on the amount of violation of the constraint and 
    increases with each generation

    """
    u_target = 0.14
    buffer = 0.1 #10%

    u_min = u_target * (1 - buffer) 
    u_max = u_target * (1 + buffer)

    # small constant to avoid division by zero
    const = 10**-2

    # adaptive penalty factors
    penalty_base = 10
    penalty_max = 1000

    # check if u_actual is within the target range
    if u_min <= u_actual <= u_max:
        
        u_debug = "in range..."

        # Feasbile solution
        fitness = round(1/(gwp_actual + const), 4)  
    else:
        
        u_debug = "out of range..."
       
        violation = (u_actual - u_max) if u_actual > u_max else (u_min - u_actual)
        
        " Adaptive penalty calculation -------------------------------------------"
        progress = gen/max_gen
        penalty_factor = penalty_base + (penalty_max - penalty_base) * progress

        # add penalty factor to gwp
        penalized_gwp = gwp_actual + penalty_factor * violation

        # to test for no adpative penalty
        # penalized_gwp = gwp_actual + violation

        fitness = round(1/(penalized_gwp + const), 4)

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

    # fitness (u_total, gwp_total)

    