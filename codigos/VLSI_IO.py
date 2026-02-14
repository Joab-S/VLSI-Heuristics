"""## Input and output

### Reading instances

#### YAL file reader
"""


import re
import math

from VLSI import VLSI
from VLSI import VLSI_Block
from VLSI import VLSI_Network
from VLSI import VLSI_Terminal

def remove_all(list, element):
  return [x for x in list if x!=element]

def read(name:str):

  I = VLSI()
  comment = False
  module = False
  iolist = False
  nets = False
  parent = False
  block_index = 0
  network_index = 0

  with open(name) as f:
    lines = f.readlines()
    for line in lines:
      words = re.split(" |;|\n", line)
      words = remove_all(words, "")
      if (len(words) == 0): continue
      cw = 0
      if words[cw].find("/*") >= 0:
        comment = True
      elif comment == True:
        if words[cw].find("*/") >= 0:
          comment = False
        else:
          pass
      elif words[cw] == "MODULE":
        module = True
        B = VLSI_Block()
        block_name = words[cw+1]
        B.ID = block_name
        B.index = block_index
        block_index = block_index + 1
      elif module == True:
        if words[cw] == "ENDMODULE":
          I.block.append(B)
          module = False
        elif words[cw] == "TYPE":
          type_name = words[cw+1]
          B.TYPE = type_name
          if type_name == "PARENT":
            parent = True
          else:
            parent = False
        elif words[cw] == "DIMENSIONS":
          x = []
          y = []
          x.append(int(words[cw+1]))
          x.append(int(words[cw+3]))
          x.append(int(words[cw+5]))
          x.append(int(words[cw+7]))
          y.append(int(words[cw+2]))
          y.append(int(words[cw+4]))
          y.append(int(words[cw+6]))
          y.append(int(words[cw+8]))
          block_width = max(x) - min(x)
          block_length = max(y) - min(y)
          B.w = block_width
          B.l = block_length
          B.x = min(x)
          B.y = min(y)
          if parent :
            I.W = block_width
            I.L = block_length
            B.minw = 0
            B.maxw = math.inf
            B.minl = 0
            B.maxl = math.inf
            #B.minw = block_width
            #B.maxw = block_width
            #B.minl = block_length
            #B.maxl = block_length
            
          else:
            B.minw = block_width * I.flex_min
            B.maxw = block_width * I.flex_max
            B.minl = block_length * I.flex_min
            B.maxl = block_length * I.flex_max
        elif words[cw] == "IOLIST":
          iolist = True
        elif iolist == True:
          if words[cw] == "ENDIOLIST":
            iolist = False
          else:
            T = VLSI_Terminal()
            T.ID = words[cw]
            T.TYPE = words[cw+1]

            xpos = int(words[cw+2])
            ypos = int(words[cw+3])
            T.x = (xpos-B.x)/B.w
            T.y = (ypos-B.y)/B.l
            T.block = B
            B.terminal.append(T)

            if parent == True:
              N = VLSI_Network()
              N.ID = T.ID
              N.index = network_index
              network_index = network_index + 1
              N.terminal.append(T)
              I.network.append(N)
        elif words[cw] == "NETWORK":
          nets = True
          new_block = True
        elif nets == True:
          if words[cw] == "ENDNETWORK":
            nets = False
          else:
            if new_block:
              list_name = words[cw]
              block_name = words[cw+1]
              BL = I.block[I.find_block(block_name)]
              terminal_index = 0
              offset = 2
            else:
              offset = 0
            for i in range(offset,len(words)):
              net_name = words[cw+i]
              try:
                N = I.network[ I.find_network(net_name) ]
              except:
                N = VLSI_Network()
                N.ID = net_name
                N.index = network_index
                network_index = network_index + 1
                I.network.append(N)
              N.terminal.append(BL.terminal[terminal_index])
              terminal_index = terminal_index + 1
              if line.find(";") == -1:
                new_block = False
              else:
                new_block = True
      else:
        pass
  return I

"""### Output solutions

#### Plotting the VLSI
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns;

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
    if S[j] != len(I.block)-1:
      for t in B.terminal:
        plt.plot(t.xpos(), t.ypos(), marker='+', color="gray")
    else:
      for t in B.terminal:
        plt.plot(t.xpos(), t.ypos(), marker='+', color="red")


  ax.autoscale()
  ratio = 1.0
  x_left, x_right = ax.get_xlim()
  y_low, y_high = ax.get_ylim()
  ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)

  plt.show()