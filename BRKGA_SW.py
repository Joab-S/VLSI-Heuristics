"""## BRKGA with Sliding Windows"""

from pymoo.algorithms.soo.nonconvex.brkga import BRKGA
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

import numpy as np

import VLSI
from SlidingWindow import sliding_window

import copy
def decode_SW(I:VLSI, R:list[float]):
  order = np.argsort(R).tolist()
  J = copy.deepcopy(I)
  return sliding_window(J, 1, order)

class PVLSI_SW(Problem):

  def __init__(self, I:VLSI):
    self.I = I
    self.iter = 0
    super().__init__(n_var = (len(I.block)-1), n_obj=1, n_ieq_constr=0, xl=0, xu=1)


  def _evaluate(self, x, out, *args, **kwargs):
    v = []
    for i in range(len(x)):
      res = decode_SW(self.I, x[i])
      v.append(res.hpwl_value)


    out["F"] = np.column_stack(v)
    self.iter = self.iter + 1
    print(f"Melhor solução na {self.iter}a iteração --> {min(v)}")

def resolver_BRKGA_SW(I:VLSI):
  tam_pop = 10
  algoritmo = BRKGA(n_elites=round(tam_pop*0.2),
                    n_offsprings=round(tam_pop*0.6),
                    n_mutants=round(tam_pop*0.2),
                    bias=0.5,
                    eliminate_duplicates=False)

  res = minimize(PVLSI_SW(I), algoritmo, ("n_gen", 10), seed=1, verbose=False)
  print("Melhor solução encontrada: \nX = %s\nF = %s" % (res.X, res.F))
  J = decode_SW(I, res.X)
  return J