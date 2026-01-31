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
    bw_info = ga.get_best_wall_info()

    print("\n")
    logging.info("===============best_wall_info================")
    print(f"Found in generation: {bw_info["best_gen"]}")
    print(f"U-value: {bw_info["best_u"]}")
    print(f"GWP: {bw_info["best_gwp"]}")
    print(f"Total Thickness: {bw_info["total_best_wall_thickness"] * 1000}mm") 
    print("Wall Layers:")
    for layer_idx, layer in enumerate(bw_info['all_layers_t']):
        for mat, mat_t in layer.items():
            print(f"Layer {layer_idx+1}: {mat}: {mat_t * 1000}mm")

    # Plot the graphs
    ga.plot_graphs()



        



# python main.py