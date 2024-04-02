import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns;
from VLSI_class import VLSI

plt.rcParams['figure.figsize'] = [8, 8]
plt.rcParams['figure.dpi'] = 100

def plot_VLSI(I:VLSI, S:list[int]=None):

  if S == None:
    S = [i for i in range(len(I.block))]

  palette = sns.color_palette("colorblind", len(S))
  fig, ax = plt.subplots()

  ax.add_patch(Rectangle(xy=(0,0), width=I.W, height=I.L, angle=0.0,  color="black", alpha=1))
  value = 0
  j = 0
  for j in range(len(S)-1):
    B = I.block[S[j]]
    ax.add_patch(Rectangle(xy=(B.x,B.y), width=B.w, height=B.l, angle=0.0, alpha=1, color=palette[j]))
    plt.annotate(text=B.ID, xy=(B.x + B.w//2 - 50, B.y + B.l//2 - 5))

  for j in range(len(S)):
    B = I.block[S[j]]
    for t in B.terminal:
      plt.plot(t.xpos(), t.ypos(), marker='+', color="gray")


  #ax.autoscale()
  ratio = 1.0
  x_left, x_right = ax.get_xlim()
  y_low, y_high = ax.get_ylim()
  ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)

  plt.show()
  plt.savefig('plot.png')
