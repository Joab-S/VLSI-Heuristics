import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import cplex as cpx
import math

import VLSI
from Representation import relpos

class Replacer:
  def __init__(self, I:VLSI, R:relpos, S:list[int]=None):

    if S == None:
      S = [i for i in range(len(I.block)-1)]

    self.I = I
    self.R = R
    self.S = S
    self.S.append(len(I.block)-1)
    #print(self.S)
    self.model:pyo.Model = None

  def placement(self):
    """Given an instance and a (possibly partial) sequence pair,
    calculates the ideal placement and measurement of the blocks"""
    self.build_model()
    return self.solve_model()

  def build_model(self):
    """Builds the IP model to solve the placement problem"""
    self.model = pyo.ConcreteModel()

    ### Variables ###

    # Sets
    self.model.Networks = pyo.RangeSet(0,len(self.I.network))
    self.model.Blocks = pyo.RangeSet(0,len(self.S)-1)

    # Large area variables
    #self.model.W = pyo.Var(bounds=(0, None))
    #self.model.L = pyo.Var(bounds=(0, None))

    # WN & LN: HPWL variables
    self.model.WN = pyo.Var(self.model.Networks, bounds=(0, None))
    self.model.LN = pyo.Var(self.model.Networks, bounds=(0, None))

    # WB & LB: Width and Length of blocks
    def width_stretch(model, i): return (self.I.block[self.S[i]].minw, self.I.block[self.S[i]].maxw)
    def length_stretch(model, i):return (self.I.block[self.S[i]].minl, self.I.block[self.S[i]].maxl)
    self.model.WB = pyo.Var(self.model.Blocks, bounds=width_stretch)
    self.model.LB = pyo.Var(self.model.Blocks, bounds=length_stretch)
    
    # XB & YB: Block (X,Y) coordinates
    self.model.XB = pyo.Var(self.model.Blocks, bounds=(0, None))
    self.model.YB = pyo.Var(self.model.Blocks, bounds=(0, None))

    # ALPHA_(AB) & BETA_(AB): Decision variables to position blocks A & B
    self.model.alpha = pyo.Var(self.model.Blocks, self.model.Blocks, domain=pyo.Boolean)
    self.model.beta = pyo.Var(self.model.Blocks, self.model.Blocks, domain=pyo.Boolean)

    ### Constraints ###

    self.model.constraints = pyo.ConstraintList()

    # HPWL Constraint
    for n in range(len(self.I.network)):
      for t in self.I.network[n].terminal:
        try:
          i = self.S.index(t.block.index)
        except:
          continue
        for tp in self.I.network[n].terminal:
          if t != tp:
            try:
              j = self.S.index(tp.block.index)
            except:
              continue
            self.model.constraints.add(self.model.WN[n] >= self.model.XB[i] + self.model.WB[i]*t.x - self.model.XB[j] - self.model.WB[j]*tp.x)
            self.model.constraints.add(self.model.LN[n] >= self.model.YB[i] + self.model.LB[i]*t.y - self.model.YB[j] - self.model.LB[j]*tp.y)

    # Maximum Area Constraint
    for b in range(len(self.S)-1):
      self.model.constraints.add(self.model.XB[b] + self.model.WB[b] <= self.model.WB[len(self.S)-1])
      self.model.constraints.add(self.model.YB[b] + self.model.LB[b] <= self.model.LB[len(self.S)-1])

    self.model.constraints.add(self.model.XB[len(self.S)-1] <= 0)
    self.model.constraints.add(self.model.YB[len(self.S)-1] <= 0)
    # Horizontal & Vertical relation constraints
    # Pairs ordered by the relative position (linear constraints)
    for a in range(len(self.S)-1):
      for b in range(len(self.S)-1):
        if self.R.H[self.S[a]][self.S[b]]:
          self.model.constraints.add(self.model.XB[a] + self.model.WB[a] <= self.model.XB[b])
        elif self.R.V[self.S[a]][self.S[b]]:
          self.model.constraints.add(self.model.YB[a] + self.model.LB[a] <= self.model.YB[b])
    # Unordered pairs (integer BIGM constrains)
    BIGM = 2*(self.I.block[-1].w + self.I.block[-1].l) + 1 #Define BIGM
    for b in range(len(self.S)-1):
      for a in range(b):
        if (self.R.H[self.S[a]][self.S[b]] + self.R.H[self.S[b]][self.S[a]]
          + self.R.V[self.S[a]][self.S[b]] + self.R.V[self.S[b]][self.S[a]]) == 0:
          self.model.constraints.add( self.model.XB[a] + self.model.WB[a] <= self.model.XB[b] + (2 - self.model.alpha[a,b] - self.model.beta[a,b])*BIGM )
          self.model.constraints.add( self.model.YB[a] + self.model.LB[a] <= self.model.YB[b] + (1 + self.model.alpha[a,b] - self.model.beta[a,b])*BIGM )
          self.model.constraints.add( self.model.YB[b] + self.model.LB[b] <= self.model.YB[a] + (1 - self.model.alpha[a,b] + self.model.beta[a,b])*BIGM )
          self.model.constraints.add( self.model.XB[b] + self.model.WB[b] <= self.model.XB[a] + (0 + self.model.alpha[a,b] + self.model.beta[a,b])*BIGM )

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
    opt.options['threads'] = 1
    opt.options['timelimit'] = 3600
    opt.options['lpmethod'] = 3
    results = opt.solve(self.model, tee=False)
    #self.model.solutions.store_to(results)

    #print(results)
    #self.model.pprint()

    if (results.solver.status == SolverStatus.ok): #and (results.solver.termination_condition == TerminationCondition.optimal):
        # Do something when the solution in optimal and feasible
      for j in range(len(self.S)):
        self.I.block[self.S[j]].w = self.model.WB[j].value
        self.I.block[self.S[j]].l = self.model.LB[j].value
        self.I.block[self.S[j]].x = self.model.XB[j].value
        self.I.block[self.S[j]].y = self.model.YB[j].value
      self.I.W = self.model.WB[len(self.S)-1].value
      self.I.L = self.model.LB[len(self.S)-1].value
      self.I.hpwl_value = self.model.obj()

      for b in range(len(self.S)-1):
        for a in range(b):
          if   (self.model.alpha[a,b].value == 1 and self.model.beta[a,b].value == 1):
            self.R.H[self.S[a]][self.S[b]] = 1
          elif (self.model.alpha[a,b].value == 0 and self.model.beta[a,b].value == 0):
            self.R.H[self.S[b]][self.S[a]] = 1
          elif (self.model.alpha[a,b].value == 0 and self.model.beta[a,b].value == 1):
            self.R.V[self.S[a]][self.S[b]] = 1
          elif (self.model.alpha[a,b].value == 1 and self.model.beta[a,b].value == 0):
            self.R.V[self.S[b]][self.S[a]] = 1

    elif (results.solver.termination_condition == TerminationCondition.infeasible):
      print(" ** Infeasible ** ")
      self.I.hpwl_value = math.inf
      self.model.write("model.lp", io_options={'symbolic_solver_labels': True})
      exit(0)
    else:
      # Something else is wrong
      print("Solver Status: ",  results.solver.status)
      exit(0)


    return self.I
