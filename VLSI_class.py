from VLSI_models import VLSI_Block
from VLSI_models import VLSI_Network

class VLSI:
  def __init__(self):
    self.ID: str                            # VLSI ID
    self.block: list[VLSI_Block] = []       # List of blocks (last is the box)
    self.network: list[VLSI_Network] = []   # List of networks
    self.W: int = 0                         # Width of the box
    self.L: int = 0                         # Length of the box
    self.flex_min = 1.0                     # Flexibility of block size [0,1]
    self.flex_max = 1.0                     # [1,inf]
    self.hpwl_value = 0                     # HPWL solution value

  def area(self):
    return self.W*self.L

  def hpwl(self):
    return sum(self.network, key = lambda net : net.hpwl())

  def find_block(self, ID:str):
    j = 0
    while j < len(self.block):
      if self.block[j].ID == ID:
        return j
      j = j + 1
    raise Exception("Block not found")
    return -1

  def find_network(self, ID:str):
    j = 0
    while j < len(self.network):
      if self.network[j].ID == ID:
        return j
      j = j + 1
    raise Exception("Network not found")
    return -1

  def set_flexibility(self, r:float):
    self.flex_min = 1-r
    self.flex_max = 1+r
    for B in self.block:
      B.minw = B.w * self.flex_min
      B.maxw = B.l * self.flex_max
      B.minl = B.w * self.flex_min
      B.maxl = B.l * self.flex_max