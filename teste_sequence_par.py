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

instance = "hp"
is_fixed_edge = True
I = read(f"yal_instances/{instance}.yal", is_fixed_edge)

num_blocks = len(I.block)
print(f"{instance} - Blocks = {num_blocks}, Nets = {len(I.network)}")

start = time.time()

# Posicionar os grupos de blocos
R = relpos(num_blocks)

response = Replacer(I, R).placement()
I = response["vlsi"]

end = time.time()
duration = end - start
image_name = f"i_Sequence_Par_{instance}_is_fixed_edge_{is_fixed_edge}"
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