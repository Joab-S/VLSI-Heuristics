from pyomo.environ import ConcreteModel, Var, Objective, ConstraintList, maximize, minimize, Binary, SolverFactory
from pyomo.opt import TerminationCondition
import numpy as np
from VLSI_class import VLSI
import os

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

class VLSIClustering:
    def __init__(self, I, k):
        if not isinstance(I, VLSI):
            raise ValueError("I precisa ser um objeto VLSI")
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k precisa ser um valor inteiro positivo")

        self.I = I
        self.k = k
        self.blocks = None
        self.model = None
        self.result = None

    # --------------
    def set_blocks(self, blocks: list):
        self.blocks = blocks

    def _get_blocks(self):
        if (self.blocks):
            return self.blocks

        return range(len(self.I.block) - 1)
    
    def reclustering(self, is_max: bool, min_group_size_factor=1, max_group_size_factor=1.5):
        # Fazer a bunção objetivo considerando apenas os elementos da lista de blocos válidos
        blocks = self._get_blocks()
        self.model = ConcreteModel()
        self.model.x = Var(blocks, blocks, within=Binary)

        mu, sigma = self._mu_sigma(self._network_count_reclustering())

        sense, factor = (minimize, -1) if not is_max else (maximize, 1)

        self.model.obj = Objective(expr=sum(self.model.x[i, j] * ((factor * (self._network_count_reclustering()[i][j] - mu)) / sigma)
                                            for i in blocks for j in blocks[blocks.index(i) + 1:]), sense=sense)
        
        self.model.constraints = ConstraintList()
        for k in range(2, len(blocks)):
            for j in range(1, k):
                for i in range(j):
                    self.model.constraints.add(self.model.x[blocks[i], blocks[j]] + self.model.x[blocks[i], blocks[k]] <= 1 + self.model.x[blocks[j], blocks[k]])
                    self.model.constraints.add(self.model.x[blocks[i], blocks[j]] + self.model.x[blocks[j], blocks[k]] <= 1 + self.model.x[blocks[i], blocks[k]])
                    self.model.constraints.add(self.model.x[blocks[i], blocks[k]] + self.model.x[blocks[j], blocks[k]] <= 1 + self.model.x[blocks[i], blocks[j]])
        
        min_group_size = int(self.k * min_group_size_factor)
        max_group_size = int(self.k * max_group_size_factor)
        #print(f"min_group_size_factor: {min_group_size}, max_group_size_factor {max_group_size}")
        
        for i in range(len(blocks)):
            self.model.constraints.add(sum(self.model.x[blocks[i], blocks[j]] for j in range(len(blocks)) if i != j) >= min_group_size)
            self.model.constraints.add(sum(self.model.x[blocks[i], blocks[j]] for j in range(len(blocks)) if i != j) <= max_group_size)

    def _network_count_reclustering(self):
        blocks = self._get_blocks()

        N = [[0 for _ in blocks] for _ in blocks]
        for r in self.I.network:
            for j in range(len(blocks)):
                for i in range(j):
                    if self._has_block(r, self.I.block[blocks[i]]) and self._has_block(r, self.I.block[blocks[j]]):
                        N[i][j] += 1
        return N
    
    # --------------

    def build_kmeans_grouping(self, n_clusters):
        n_blocks = len(self.I.block) - 1
        adjacency_matrix = self._network_count()

        features = []
        for i in range(n_blocks):
            features.append(adjacency_matrix[i])
        features = np.array(features)

        # Normalização das features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        # Aplicar K-means++ clustering
        kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=0)
        kmeans.fit(features_normalized)
        labels = kmeans.labels_

        # Transformar os labels de volta para uma representação de grupos
        groups = [[] for _ in range(n_clusters)]
        for idx, label in enumerate(labels):
            groups[label].append(idx)

        return groups

    ########################################

    def build_minimax_cardinality_grouping(self, is_max: bool, min_group_size_factor=1, max_group_size_factor=1.5):
        """
        mmcg: Minimun and Maximum Cardinality Grouping
        """
        n_blocks = len(self.I.block) - 1
        self.model = ConcreteModel()
        self.model.x = Var(range(n_blocks), range(n_blocks), within=Binary)

        mu, sigma = self._mu_sigma(self._network_count())

        sense, factor = (minimize, -1) if not is_max else (maximize, 1)
            
        self.model.obj = Objective(expr=sum(self.model.x[i, j] * ((factor * (self._network_count()[i][j] - mu)) / sigma)
                                   for i in range(n_blocks) for j in range(i + 1, n_blocks)), sense=sense)

        self.model.constraints = ConstraintList()
        for k in range(2, n_blocks):
            for j in range(1, k):
                for i in range(j):
                    self.model.constraints.add(self.model.x[i, j] + self.model.x[i, k] <= 1 + self.model.x[j, k])
                    self.model.constraints.add(self.model.x[i, j] + self.model.x[j, k] <= 1 + self.model.x[i, k])
                    self.model.constraints.add(self.model.x[i, k] + self.model.x[j, k] <= 1 + self.model.x[i, j])

        min_group_size = int(self.k * min_group_size_factor)
        max_group_size = int(self.k * max_group_size_factor)
        print(f"min_group_size_factor: {min_group_size}, max_group_size_factor {max_group_size}")

        # Adicionando restrições de tamanho mínimo e máximo para os grupos
        for i in range(n_blocks):
            self.model.constraints.add(sum(self.model.x[i, j] for j in range(n_blocks) if i != j) >= min_group_size)
            self.model.constraints.add(sum(self.model.x[i, j] for j in range(n_blocks) if i != j) <= max_group_size)


    def build_max_cardinality_grouping(self, is_max: bool):
        """
        mcg: Maximum Cardinality Grouping
        """
        n_blocks = len(self.I.block) - 1
        self.model = ConcreteModel()
        self.model.x = Var(range(n_blocks), range(n_blocks), within=Binary)

        mu, sigma = self._mu_sigma(self._network_count())

        sense, factor = (minimize, -1) if not is_max else (maximize, 1)
            
        self.model.obj = Objective(expr=sum(self.model.x[i, j] * ((factor * (self._network_count()[i][j] - mu)) / sigma)
                                for i in range(n_blocks) for j in range(i + 1, n_blocks)),
                        sense=sense)

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
        solver.options['threads'] = 1
        solver.options['timelimit'] = 1800
        solver.options['lpmethod'] = 3
        self.result = solver.solve(self.model, tee=tee)

    def get_groups(self):
        
        if self.result.solver.termination_condition == TerminationCondition.optimal or \
            self.result.solver.termination_condition == TerminationCondition.maxTimeLimit:
            n_blocks = len(self.I.block) - 1
            return self._generate_groups(n_blocks)
        else:
            print('Não foi possível encontrar uma solução ótima.')
            return None
    
    def _generate_groups(self, n_blocks):
        groups = set()
        used_elements = set()
        for i in range(n_blocks):
          if i in used_elements:
              continue
          group = {i}
          is_subset = any(group.issubset(existing_group) for existing_group in groups)
          for j in range(i + 1, n_blocks):
            if self.model.x[i, j].value == 1 and j not in used_elements:
              group.add(j)
              used_elements.add(j)
          if not is_subset:
            groups.add(tuple(group))
        return [list(g) for g in groups]
