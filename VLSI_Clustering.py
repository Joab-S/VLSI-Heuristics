from pyomo.environ import ConcreteModel, Var, Objective, ConstraintList, maximize, Binary, SolverFactory
from pyomo.opt import TerminationCondition
import numpy as np
from VLSI_class import VLSI
import os

class VLSIClustering:
    def __init__(self, I, k):
        if not isinstance(I, VLSI):
            raise ValueError("I precisa ser um objeto VLSI")
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k precisa ser um valor inteiro positivo")

        self.I = I
        self.k = k
        self.model = None
        self.result = None
    
    def build_minimax_cg_vlsi_model(self, min_group_size_factor=1, max_group_size_factor=1.5):
        """
        mmcg: Minimun and Maximum Cardinality Grouping
        """
        n_blocks = len(self.I.block) - 1        
        self.model = ConcreteModel()
        self.model.x = Var(range(n_blocks), range(n_blocks), within=Binary)

        mu, sigma = self._mu_sigma(self._network_count())

        self.model.obj = Objective(expr=sum(self.model.x[i, j] * ((self._network_count()[i][j] - mu) / sigma)
                                for i in range(n_blocks) for j in range(i + 1, n_blocks)),
                        sense=maximize)

        self.model.constraints = ConstraintList()   
        # Adicionando restrições de tamanho mínimo e máximo para os grupos
        for k in range(2, n_blocks):
            for j in range(1, k):
                for i in range(j):
                    self.model.constraints.add(self.model.x[i, k] + 1 >= self.model.x[i, j] + self.model.x[j, k])

        min_group_size = int(self.k * min_group_size_factor)
        max_group_size = int(self.k * max_group_size_factor)
        print(f"min_group_size_factor: {min_group_size}, max_group_size_factor {max_group_size}")

        for i in range(n_blocks):
            self.model.constraints.add(sum(self.model.x[i, j] for j in range(n_blocks) if i != j) >= min_group_size)
            self.model.constraints.add(sum(self.model.x[i, j] for j in range(n_blocks) if i != j) <= max_group_size)


    def build_mcg_vlsi_model(self):
        """
        mcg: Maximum Cardinality Grouping
        """
        n_blocks = len(self.I.block) - 1
        self.model = ConcreteModel()
        self.model.x = Var(range(n_blocks), range(n_blocks), within=Binary)

        mu, sigma = self._mu_sigma(self._network_count())

        self.model.obj = Objective(expr=sum(self.model.x[i, j] * ((self._network_count()[i][j] - mu) / sigma)
                                  for i in range(n_blocks) for j in range(i + 1, n_blocks)),
                          sense=maximize)

        self._add_constraints(self.model, n_blocks)

    def _add_constraints(self, model, n_blocks):
        self.model.constraints = ConstraintList()
        for k in range(2, n_blocks):
            for j in range(1, k):
                for i in range(j):
                    self.model.constraints.add(self.model.x[i, k] + 1 >= self.model.x[i, j] + self.model.x[j, k])

        for i in range(n_blocks):
            self.model.constraints.add(sum(self.model.x[i, j] for j in range(n_blocks) if i != j) <= self.k - 1)


    def _network_count(self):
        n_blocks = len(self.I.block) - 1
        N = [[0 for _ in range(n_blocks)] for _ in range(n_blocks)]
        for r in self.I.network:
            for j in range(n_blocks):
                for i in range(j):
                    if self._has_block(r, self.I.block[i]) and self._has_block(r, self.I.block[j]):
                        N[i][j] += 1
        return N

    def _has_block(self, r, b):
        return any(t.block.ID == b.ID for t in r.terminal)

    def _mu_sigma(self, networks):
        not_null, lines_sum = [], []
        for i in networks:
            not_null.extend([j for j in i if j > 0])
            lines_sum.append(sum(i))

        mu = np.mean(not_null)
        sigma = np.std(not_null)
        return mu, sigma

    def solve_cbc(self, tee = False):
        solver = SolverFactory('cbc')
        self.result = solver.solve(self.model, tee=tee)
        
    def solve_cplex(self, tee = False):
        #solver = SolverFactory('cplex', executable=os.environ.get('CPLEX_EXECUTABLE'))
        solver = SolverFactory('cplex_direct')
        self.result = solver.solve(self.model, tee=tee)

    def get_groups(self):
        if self.result.solver.termination_condition == TerminationCondition.optimal:
            n_blocks = len(self.I.block) - 1
            return self._generate_groups_uni(n_blocks)
            #return self.organize_groups(all_groups)
        else:
            print('Não foi possível encontrar uma solução ótima.')
            return None

    def get_groups2(self):
        if self.result.solver.termination_condition == TerminationCondition.optimal:
            n_blocks = len(self.I.block) - 1
            all_groups = self._generate_groups(n_blocks)
            return self.organize_groups(all_groups)
        else:
            print('Não foi possível encontrar uma solução ótima.')
            return None

    def _generate_groups_uni(self, n_blocks):
        groups = set()
        used_elements = set()
        for i in range(n_blocks):
          group = {i}
          is_subset = any(group.issubset(existing_group) for existing_group in groups)
          for j in range(i + 1, n_blocks):
            if self.model.x[i, j].value == 1 and j not in used_elements:
              group.add(j)
              used_elements.add(j)
          if not is_subset:
            groups.add(tuple(group))
        return [list(g) for g in groups]

    def _generate_groups(self, n_blocks):
      all_groups = []
      for i in range(n_blocks):
        g = [i]
        is_subset = any(set(g).issubset(set(existing_group)) for existing_group in all_groups)
        for j in range(i + 1, n_blocks):
          if self.model.x[i, j].value == 1:
            g.append(j)
        if not is_subset:
          all_groups.append(g)
      print(f"all_groups: {all_groups}")
      return all_groups

    def organize_groups(self, all_groups):
      groups = [all_groups[0]]
      for g in all_groups[1:]:
        groups = self._checking(g, groups)
      return groups

    def _checking(self, g, groups):
        added_to_existing_group = False
        for group in groups:
            if set(g).intersection(group):
                new_group = list(set(g) - set(group))
                if new_group:
                  if (len(group) + len(new_group) <= self.k):
                    group.extend(new_group)
                  else:
                    groups.append(new_group)
                added_to_existing_group = True
                break
        if not added_to_existing_group:
            groups.append(g)
        return groups