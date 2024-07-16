from yal_file_reader import read
import math
from VLSI_Clustering import VLSIClustering
from Representation import relpos
from Raplacer import Replacer
from plot_VLSI import plot_VLSI
import time
import json
import datetime

def run(instance: str, is_fixed_edge: bool, log_file):
    # Ler o arquivo YAL
    I = read(f"yal_instances/{instance}.yal", is_fixed_edge)

    # Calcular número de blocos
    num_blocks = len(I.block)
    print(f"{instance} - Blocks = {num_blocks}, Nets = {len(I.network)}")

    k = int(math.sqrt(num_blocks))
    start = time.time()

    # Realizar clustering
    clustering = VLSIClustering(I, k)
    print(f"Entrou no k-means às {(datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=-3)))).strftime('%H:%M')}")

    # Obter grupos de blocos
    n_clusters = round((num_blocks-1)/k)
    print(f"n_clusters: {n_clusters}")
    groups = clustering.build_kmeans_grouping(n_clusters)

    print(groups, '\n')
    groups_copy = groups.copy()

    # Posicionar os grupos de blocos
    R = relpos(num_blocks)
    print(len(groups), " ", groups)
    for group in groups:
        M = Replacer(I, R, group) 
        I = M.placement()["vlsi"]
        R = M.R
    # Posicionar os blocos restantes
    print("Posições Relativas completa para os grupos.")
                                                                 
    print(f"Começando às {(datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=-3)))).strftime('%H:%M')}")

    response = Replacer(I, R).placement() #timelimit=timelimit)
    I = response["vlsi"]

    end = time.time()
    duration = end - start
    image_name = f"i_{instance}_malleable_{is_fixed_edge}"
    name = plot_VLSI(I, range(len(I.block)-1), image_name)

    print(f"Instance {instance}.yal resolved in ", duration, " seconds\n\n")
    print(response)

    result = {
        "instance": instance,
        "is_fixed_edge": is_fixed_edge,
        "image_name": name,
        "hpwl": f"{I.hpwl_value}",
        "time": duration,
        "status": response["status"],
        "termination_condition": response["termination_condition"],
        "infeasible": response["infeasible"],
        "k": k,
        "groups": f"{groups_copy}"
    }
    
    log_file.write(json.dumps(result, indent=4) + "\n")

    return 0

def main():
    instances = ["hp", "xerox", "apte", "ami33", "ami49"]
    log_file_path = "vlsi_results_log.json"

    # Abrir arquivo de log para escrita
    with open(log_file_path, 'w') as log_file:
        for instance in instances:
            run(instance, True, log_file)
            
    return 0

if __name__ == "__main__":
    main() 