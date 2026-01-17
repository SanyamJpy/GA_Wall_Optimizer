import logging
from src.class_WaGA import WallAssemblyGA

if __name__ == "__main__":

    filePath = "dataBase/test_dataBase_2.json"

    ga = WallAssemblyGA(filePath, population=20, generations=20)

    # print("\n")
    # print(ga)

    results = ga.run()
    best_wall_info = ga.get_best_wall_info()
    logging.info(best_wall_info)

    print("\n")
    # print(results["all_U"])
    # print("\n")
    # print(results["all_gwp"])
    # print("\n")
    # for key, value in results["all_U"][0].items():
    #     print("U-val:", value)
    #     print("GWP:", results["all_gwp"][0][key])

    plot = input("Do you want to plot the results? (y/n): ")
    if plot.lower() == 'y':
        ga.plot_gwp_evolution()
        ga.plot_U_evolution()


        



# python main2.py