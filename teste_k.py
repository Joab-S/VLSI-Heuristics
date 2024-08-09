from yal_file_reader import read
import math
from Kmeans_Clustering import VLSI_Clustering_K
from Representation import relpos
from Raplacer import Replacer
from plot_VLSI import plot_VLSI
import time
import json
import datetime

instance = "ami33"
is_fixed_edge = True
I = read(f"yal_instances/{instance}.yal", is_fixed_edge)

num_blocks = len(I.block)
print(f"{instance} - Blocks = {num_blocks}, Nets = {len(I.network)}")

start = time.time()

clustering = VLSI_Clustering_K(I)
k = clustering.elbow_method(max_k=int((num_blocks-1)))#/2))

print(k)
grupos = clustering.k_means(20)
print(grupos)


print(f"Entrou nas posições relativas às {(datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=-3)))).strftime('%H:%M')}")

# Posicionar os grupos de blocos
R = relpos(num_blocks)
print(len(grupos), " ", grupos)
for group in grupos:
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
    "groups": f"{grupos}"
}