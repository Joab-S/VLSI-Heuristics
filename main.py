from yal_file_reader import read
import math
from VLSI_Clustering import VLSIClustering
from relpos import relpos
from Raplacer import Replacer
from plot_VLSI import plot_VLSI


def main():
    # Ler o arquivo YAL
    I = read("yal_instances/ami49.yal")

    # Calcular número de blocos
    num_blocks = len(I.block)
    print(f"Blocks = {num_blocks}, Nets = {len(I.network)}")

    # Calcular tamanho do cluster
    k = int(math.sqrt(num_blocks))

    # Realizar clustering
    clustering = VLSIClustering(I, k)
    clustering.build_mcg_vlsi_model()
    clustering.solve_cplex()

    # Obter grupos de blocos
    groups = clustering.get_groups()
    print("Grupos:", groups)

    # Posicionar os grupos de blocos
    R = relpos(num_blocks)
    for group in groups:
        M = Replacer(I, R, group)
        I = M.placement()
        R = M.R

    # Posicionar os blocos restantes
    I = Replacer(I, R).placement()

#    for i in range(len(R.H)):
#        print(R.H[i])
#
#    print("-------------------------------")
#    for i in range(len(R.V)):
#        print(R.V[i])
#
#    # Plotar o layout VLSI
#    plot_VLSI(I, range(len(I.block)-1))

if __name__ == "__main__":
    main()


"""
import random
from sliding_window import sliding_window

I = read("yal_instances/hp.yal")
print(f"Blocks = {len(I.block)}, Nets = {len(I.network)}")
n_blocks = len(I.block)-1
print(f"n_blocks: {n_blocks}")
order = random.sample(range(n_blocks), n_blocks)
print(f"order: {order}")
sliding_window(I, 1, order)
plot_VLSI(I, order)
"""