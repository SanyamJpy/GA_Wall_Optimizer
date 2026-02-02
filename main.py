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

    # Run the GA
    results = ga.run()
    # Print the best wall info
    ga.print_best_wall_info()
    # Plot the graphs
    ga.plot_graphs()



        



# python main.py