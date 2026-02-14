
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

class VLSI_Block:
  def __init__(self):
    self.ID: str = ""                         # Block ID
    self.TYPE: str = ""                       # Block TYPE
    self.index = -1
    self.minw = 0                             # Minimum width
    self.maxw = 0                             # Maximum width
    self.minl = 0                             # Minimum length
    self.maxl = 0                             # Maximum length
    self.terminal: list[VLSI_Terminal] = []   # List of terminals
    self.x: int = 0                           # Horizontal position (solution)
    self.y: int = 0                           # Vertical position (solution)
    self.w: int = 0                           # Width (solution)
    self.l: int = 0                           # Length (solution)

class VLSI_Network:
  def __init__(self):
    self.ID: str                             # Network ID
    self.index = -1
    self.terminal: list[VLSI_Terminal] = []  # List of terminals in the network

  def hpwl(self):
    minx = min(self.terminal, key = lambda t : t.xpos())
    maxx = max(self.terminal, key = lambda t : t.xpos())
    miny = min(self.terminal, key = lambda t : t.ypos())
    maxy = max(self.terminal, key = lambda t : t.ypos())
    return maxx + maxy - minx - miny

class VLSI_Terminal:
  def __init__(self):
    self.ID: str = ""                   # Terminal ID
    self.TYPE: str = ""                 # Terminal TYPE
    self.x: float = 0.5                 # Relative x position
    self.y: float = 0.5                 # Relative y position
    self.block: VLSI_Block              # Holder block
    self.network: VLSI_Network          # Network associated

  def xpos(self):
    return self.block.x + self.x * self.block.w

  def ypos(self):
    return self.block.y + self.y * self.block.l