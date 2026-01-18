import logging
from src.class_WaGA import WallAssemblyGA

if __name__ == "__main__":

    filePath = "dataBase/test_dataBase_2.json"

    ga = WallAssemblyGA(
        filePath, 
        population=50, 
        generations=20,
        mut_start=0.5,
        mut_end=0.1
    )

    # print(ga)

    results = ga.run()
    best_wall_info = ga.get_best_wall_info()

    print("\n")
    logging.info(best_wall_info)

    # best_gen = results["best_gen"]
    # print(best_gen)
    # best_wall_key = best_wall_info["best_wall_key"]

    # get_idx = int(best_wall_key.split("-")[-1])
    # logging.info(f"IDX of the best wall in the database: {get_idx}")

    # print("\n")
    # logging.info(results["all_t"][best_gen][get_idx])
    # print("\n")
    # logging.info(results["best_wall"])



    # plot = input("Do you want to plot the results? (y/n): ")
    # if plot.lower() == 'y':
    # ga.plot_graphs()


        



# python main2.py