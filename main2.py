from src.class_WaGA import WallAssemblyGA

if __name__ == "__main__":

    filePath = "dataBase/test_dataBase_2.json"

    ga = WallAssemblyGA(filePath, population=20, generations=20)

    # print("\n")
    # print(ga)

    results = ga.run()
    best_wall_info = ga.get_best_wall_info()
    print(best_wall_info)

    print("\n")
    # print(f"Best solution found: {results["best_wall"]}")
    # print(f"All U-values: {results['all_fitness'][best_gen]}")
    # print(results["SeenWalls"])

    # for key, value in results["all_fitness"][best_gen].items():
    #     if value == results["best_fitness"]:
    #         print(f"Best solution found: {key}")
    #         best_wall_key = key

    # print(f"U-value of best solution: {results['all_U'][best_gen][best_wall_key]}")
    # print(f"GWP of best solution: {results['all_gwp'][best_gen][best_wall_key]}")
        



# python main2.py