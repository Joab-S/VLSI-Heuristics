from yal_file_reader import read
import math
from Kmeans_Clustering import VLSI_Clustering_K
from Representation import relpos
from Raplacer import Replacer
from plot_VLSI import plot_VLSI
import time
import json
import datetime
import random

instance = "ami49"
is_fixed_edge = True
I = read(f"yal_instances/{instance}.yal", is_fixed_edge)

num_blocks = len(I.block)
print(f"{instance} - Blocks = {num_blocks}, Nets = {len(I.network)}")

start = time.time()

clustering = VLSI_Clustering_K(I)
#k = clustering.elbow_method(max_k=int((num_blocks-1)))#/2))
k = 5
#clusters = clustering.k_means(6)
clustering.plot_dendrogram()
clusters = clustering.hierarchical_clustering(k)
#clusters = clustering.dbscan()

#clusters = clustering.perform_clustering(k)
grupos = clusters.get_groups()
print(f"Para k = {k} temos: {grupos}")


# Posicionar os grupos de blocos
R = relpos(num_blocks)
print(len(grupos), " ", grupos)

clustering.calculate_internal_external_connectivity()

internal_connectivity = clusters.get_normalized_internal_connectivity()
external_connectivity = clusters.get_normalized_external_connectivity()


print("\nForça Interna Normalizada: ", internal_connectivity)
print("Força Externa Normalizada: ", external_connectivity)
print('\n')

g = sorted(grupos, key=lambda group: internal_connectivity[grupos.index(group)], reverse=True) # ordena com base na conectividade interna do grupo

# print(clustering.calculate_hpwl())

print(f"Entrou nas posições relativas às {(datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=-3)))).strftime('%H:%M')}")
for group in g:
  M = Replacer(I, R, group) 
  I = M.placement(1800)["vlsi"]
  R = M.R
# Posicionar os blocos restantes
print("Posições Relativas completa para os grupos.")
                                                              
print(f"Começando às {(datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=-3)))).strftime('%H:%M')}")

response = Replacer(I, R).placement() #timelimit=timelimit)
I = response["vlsi"]

end = time.time()
duration = end - start
image_name = f"i_CH_{instance}_is_fixed_edge_{is_fixed_edge}"
name = plot_VLSI(I, range(len(I.block)-1), image_name)

print(f"Instance {instance}.yal resolved in {duration} seconds com hpwl_value = {I.hpwl_value}\n\n")
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
    "groups": f"{grupos}"
}

# Fazer uma análise de centralidade de bloco. O quanto um bloco tem conexões com outros blocos