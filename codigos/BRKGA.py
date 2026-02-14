from pymoo.algorithms.soo.nonconvex.brkga import BRKGA
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

import numpy as np

from Representation import seqpair
from Placer import Placer
from VLSI import VLSI

def decode(I:VLSI, R:list[float]):

  P = seqpair(len(R)//2)
  P.plus = np.argsort(R[:len(R)//2]).tolist()
  P.minus = np.argsort(R[len(R)//2:]).tolist()
  J = (Placer(I, P)).placement()
  print(f"+ = {P.plus}, - = {P.minus} --> {J.hpwl_value}")
  return J

class PVLSI(Problem):

  def __init__(self, I:VLSI):
    self.I = I
    self.iter = 0
    super().__init__(n_var = 2*(len(I.block)-1), n_obj=1, n_ieq_constr=0, xl=0, xu=1)


  def _evaluate(self, x, out, *args, **kwargs):
    v = []
    for i in range(len(x)):
      res = decode(self.I, x[i])
      v.append(res.hpwl_value)


    out["F"] = np.column_stack(v)
    self.iter = self.iter + 1
    print(f"Melhor solução na {self.iter}a iteração --> {min(v)}")

def resolver_BRKGA(I:VLSI):
  tam_pop = 50
  algoritmo = BRKGA(n_elites=round(tam_pop*0.2),
                    n_offsprings=round(tam_pop*0.6),
                    n_mutants=round(tam_pop*0.2),
                    bias=0.5,
                    eliminate_duplicates=False)

  res = minimize(PVLSI(I), algoritmo, ("n_gen", 50), seed=1, verbose=False)
  print("Melhor solução encontrada: \nX = %s\nF = %s" % (res.X, res.F))
  J = decode(I, res.X)
  return J
