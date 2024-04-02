from Raplacer import Replacer
from VLSI_class import VLSI
from relpos import relpos

def sliding_window(I:VLSI, size:int, order:list[int]):
  M: Replacer
  if size+1 < len(order):
    for k in range(size+1, len(order)):
      R = relpos(len(order))
      window = order[:k]
      if (k > size+1):
        R = M.R
        for i in range(k-size, len(order)):
          for j in range(k-size, len(order)):
            R.H[i][j] = 0
            R.V[i][j] = 0
      else:
        pass
      M = Replacer(I, R, window)
      I = M.placement()
  else:
    R = relpos(len(order))
    M = Replacer(I, R, order)
    I = M.placement()