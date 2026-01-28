import logging
from src.class_WaGA import WallAssemblyGA

if __name__ == "__main__":

    filePath = "dataBase/test_dataBase_2.json"

    ga = WallAssemblyGA(
        filePath, 
        population=40, 
        generations=20,
        mut_start=0.5,
        mut_end=0.1
    )

    results = ga.run()
    best_wall_info = ga.get_best_wall_info()

    print("\n")
    logging.info(best_wall_info)

    # plot = input("Do you want to plot the results? (y/n): ")
    # if plot.lower() == 'y':
    ga.plot_graphs()



        



# python main2.py