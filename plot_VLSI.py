import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from VLSI_class import VLSI

plt.rcParams['figure.figsize'] = [8, 8]
plt.rcParams['figure.dpi'] = 100

def plot_VLSI(I: VLSI, S: list[int] = None, image_name = 'plot'):
  
  if S is None:
    S = list(range(len(I.block)))
    
  # Geração da paleta de cores
  palette = sns.color_palette("colorblind", len(S))
  fig, ax = plt.subplots()

  # Desenha o retângulo exterior representando o layout do VLSI
  ax.add_patch(Rectangle(xy=(0, 0), width=I.W, height=I.L, angle=0.0, color="black", alpha=1))
    
  # Desenha cada bloco e seus terminais
  for j in S:
    B = I.block[j]
    ax.add_patch(Rectangle(xy=(B.x, B.y), width=B.w, height=B.l, angle=0.0, alpha=1, color=palette[j]))
    plt.annotate(text=f'{B.ID} ({j})', xy=(B.x + B.w / 2, B.y + B.l / 2), ha='center', va='center')
    for t in B.terminal:
      plt.plot(t.xpos(), t.ypos(), marker='+', color="gray")

  # Ajuste de aspecto baseado nas dimensões do VLSI
  ax.set_aspect(I.W / I.L)

  import math
  hpwl_str = ''
  if math.isinf(I.hpwl_value):
    hpwl_str = "inf"
  else:
    hpwl_str = str(int(I.hpwl_value))


  name = f'{image_name}_hpwl_{hpwl_str}.png'
  plt.savefig(f'/home/cplex/{name}')
  
  return name