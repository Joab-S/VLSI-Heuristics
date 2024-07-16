from VLSI import VLSI
from Replacer import Replacer
from Representation import relpos
import copy

def sliding_window(I:VLSI, size:int, order:list[int]):
  M: Replacer
  if size+1 < len(order):
    for k in range(size+1, len(order)+1):
      R = relpos(len(order))
      window = order[:k]
      #print(window)
      if (k > size+1):
        #R = copy.deepcopy(M.R)
        #for i in range(len(order)):
        #  for j in range(k-size, len(order)):
        #    R.H[order[i]][order[j]] = 0
        #    R.V[order[i]][order[j]] = 0
        #    R.H[order[j]][order[i]] = 0
        #    R.V[order[j]][order[i]] = 0
        for i in range(k):
          for j in range(k):
            R.H[order[i]][order[j]] = M.R.H[order[i]][order[j]]
            R.V[order[i]][order[j]] = M.R.V[order[i]][order[j]]
      else:
        pass
      M = Replacer(I, R, window)
      I = M.placement()
  else:
    R = relpos(len(order))
    M = Replacer(I, R, order)
    I = M.placement()
  print(order, " -> ", I.hpwl_value)
  return I