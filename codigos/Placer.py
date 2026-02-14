import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import cplex as cpx

import VLSI
from Representation import seqpair

class Placer:
  def __init__(self, I:VLSI, P:seqpair):
    self.I = I
    self.P = P
    self.model:pyo.Model = None

  def placement(self):
    """Given an instance and a (possibly partial) sequence pair,
    calculates the ideal placement and measurement of the blocks"""
    self.build_model()
    return self.solve_model()

  def build_model(self):
    """Builds the LP model to solve the placement problem"""
    self.model = pyo.ConcreteModel()

    ### Variables ###

    # Sets
    self.model.Networks = pyo.RangeSet(0,len(self.I.network)-1)
    self.model.Blocks = pyo.RangeSet(0,len(self.I.block)-1)

    # Large area variables
    #self.model.W = pyo.Var(bounds=(0, None))
    #self.model.L = pyo.Var(bounds=(0, None))

    # WN & LN: HPWL variables
    self.model.WN = pyo.Var(self.model.Networks, bounds=(0, None))
    self.model.LN = pyo.Var(self.model.Networks, bounds=(0, None))

    # WB & LB: Width and Length of blocks
    def width_stretch(model, i): return (self.I.block[i].minw, self.I.block[i].maxw)
    def length_stretch(model, i):return (self.I.block[i].minl, self.I.block[i].maxl)
    self.model.WB = pyo.Var(self.model.Blocks, bounds=width_stretch)
    self.model.LB = pyo.Var(self.model.Blocks, bounds=length_stretch)

    # XB & YB: Block (X,Y) coordinates
    self.model.XB = pyo.Var(self.model.Blocks, bounds=(0, None))
    self.model.YB = pyo.Var(self.model.Blocks, bounds=(0, None))

    ### Constraints ###

    self.model.constraints = pyo.ConstraintList()

    # HPWL Constraint
    for n in range(len(self.I.network)):
      for t in self.I.network[n].terminal:
        i = t.block.index
        for tp in self.I.network[n].terminal:
          if t != tp:
            j = tp.block.index
            self.model.constraints.add(self.model.WN[n] >= self.model.XB[i] + self.model.WB[i]*t.x - self.model.XB[j] - self.model.WB[j]*tp.x)
            self.model.constraints.add(self.model.LN[n] >= self.model.YB[i] + self.model.LB[i]*t.y - self.model.YB[j] - self.model.LB[j]*tp.y)

    # Maximum Area Constraint
    for b in range(len(self.I.block)-1):
      self.model.constraints.add(self.model.XB[b] + self.model.WB[b] <= self.model.WB[len(self.I.block)-1])
      self.model.constraints.add(self.model.YB[b] + self.model.LB[b] <= self.model.WB[len(self.I.block)-1])

    # Horizontal & Vertical relation constraints
    # Pairs ordered by the sequence pair (linear constraints)
    for a in range(len(self.I.block)-1):
      for b in range(len(self.I.block)-1):
        if self.P.LH(a,b):
          self.model.constraints.add(self.model.XB[a] + self.model.WB[a] <= self.model.XB[b])
        elif self.P.LV(a,b):
          self.model.constraints.add(self.model.YB[a] + self.model.LB[a] <= self.model.YB[b])

    ### Objective funcition ###
    # HPWL Objective
    def obj_rule(model):
      objExpr = 0
      for n in range(len(self.I.network)):
        objExpr += self.model.WN[n] + self.model.LN[n]
      return objExpr
    self.model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)


  def solve_model(self):
    #opt = SolverFactory('glpk', executable='/usr/bin/glpsol')
    #opt = SolverFactory('cbc', executable='/usr/bin/cbc')
    opt = SolverFactory('cplex_direct')
    opt.options['lpmethod'] = 3
    results = opt.solve(self.model, tee=False)
    #self.model.solutions.store_to(results)

    #print(results)
    #self.model.pprint()

    #if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        # Do something when the solution in optimal and feasible
    for j in range(len(self.I.block)):
      self.I.block[j].w = self.model.WB[j].value
      self.I.block[j].l = self.model.LB[j].value
      self.I.block[j].x = self.model.XB[j].value
      self.I.block[j].y = self.model.YB[j].value
    self.I.W = self.model.WB[len(self.I.block)-1]
    self.I.L = self.model.LB[len(self.I.block)-1]
    self.I.hpwl_value = self.model.obj()
    #elif (results.solver.termination_condition == TerminationCondition.infeasible):
    #    print(" ** Infeasible ** ")
    #else:
    #    # Something else is wrong
    #    print("Solver Status: ",  result.solver.status)


    return self.I

  def solve(self):
    self.build_model()
    return self.solve_model()