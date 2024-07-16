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

    # Calcular tamanho do cluster
    k = int(math.sqrt(num_blocks))
    print(f'k: {k}')

    timelimit = 10800    # 3 horas
    start = time.time()

    # Realizar clustering
    clustering = VLSIClustering(I, k)
    #clustering.build_max_cardinality_grouping(is_max=False)
    clustering.build_minimax_cardinality_grouping(is_max=False)
    print(f"Entrou no clustering às {(datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=-3)))).strftime('%H:%M')}")

    clustering.solve_cplex()

    # Obter grupos de blocos
    groups = clustering.get_groups()

    # Verificar se há componentes sozinhos e chamar o clustering novamente para esses componentes.
    # remove os elementos que estão em um grupo de tamanho menor que o k minimo e passa eles para serem reagrupados.
    # Ajustar a classe VLSIClustering para atender esse propósito. Ela deve receber um campo componentes que pode ser Nulo ou uma lista.
    # Se for Nulo, então a classe usa range(len(I.blocks)) como lista de blocos, c.c. usa a lista de elementos passados.
    # Nesse caso, observar que os indices de I são usados para encontrar a posição do bloco no arquivo de instância yal,
    # Assim, os elementos da lista (caso não nula) serão, também, indices. Nesse caso, os indices estarão saltados, e será necessário uma
    # abordagem para fazer com que seja possível usar o elemento da lista (que é por si só um indice) para encontrar corretamente o elemento
    # dentro do arquivo de maneira correta. Pois não poderemos seguir sequecialmente, mas conforme os indices aparecem.
 
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
    image_name = f"i_{instance}_is_fixed_edge_{is_fixed_edge}"
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
            #run(instance, True, log_file)
            run(instance, False, log_file)
    
    return 0

if __name__ == "__main__":
    main()