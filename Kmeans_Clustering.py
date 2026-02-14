from VLSI_class import VLSI
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.cluster import KMeans, DBSCAN
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, dendrogram

class Groups:
  def __init__(self):
    self.inertia_ = 0
    self.labels_ = None
    self.groups = []
    self.hpwl = {}
    self.internal_connectivity = {}

  def set_groups(self, new_group):
    self.groups = new_group

  def get_groups(self):
    return self.groups

  def inertia_update(self, new_inertia):
    self.inertia_ = new_inertia

  def get_inertia(self):
    return self.inertia_
  
  def fit_predict(self, labels):
    self.labels_ = labels
    return self.labels_

  def set_hpwl(self, new_hpwl):
    self.hpwl = new_hpwl

  def get_hpwl(self):
    return self.hpwl
  
  def set_normalized_internal_connectivity(self, internal_connectivity):
    self.internal_connectivity = internal_connectivity

  def get_normalized_internal_connectivity(self):
    return self.internal_connectivity
  
  def set_normalized_external_connectivity(self, external_connectivity):
    self.external_connectivity = external_connectivity

  def get_normalized_external_connectivity(self):
    return self.external_connectivity

class VLSI_Clustering_K:
  def __init__(self, I):
    if not isinstance(I, VLSI):
      raise ValueError("I precisa ser um objeto VLSI")
    
    self.I = I
    self.connection_matrix = self._network_count()
    self.adjacency_matrix = self.calculate_connection_strength_matrix()
    self.groups = Groups()

  def k_means(self, n_clusters, max_iterations=1000):
    # Aplicar K-means++ clustering
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42, max_iter=max_iterations)
    labels = kmeans.fit_predict(self.adjacency_matrix)

    self.groups.inertia_update(kmeans.inertia_)

    # Transformar os labels de volta para uma representação de grupos
    grouped = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(labels):
      grouped[label].append(idx)

    self.groups.set_groups(grouped)
    self.groups.fit_predict(labels)

    return self.groups

  def elbow_method(self, max_k, max_iterations=1000):
    inertia = []
    k_range = range(1, max_k + 1)

    for k in k_range:
      groups_kmeans = self.k_means(k, max_iterations=max_iterations)
      inertia.append(groups_kmeans.get_inertia())

    # Plotando o gráfico do método do cotovelo
    plt.figure(figsize=(8, 5))
    plt.plot(k_range, inertia, marker='o')
    plt.xlabel('Número de Clusters')
    plt.ylabel('Inércia')
    plt.title('Método do Cotovelo')
    plt.xticks(k_range)
    plt.grid(True)
    plt.show()
    plt.savefig(f'/home/cplex/cotovelo.png')
  
  # def _network_count(self):
  #   n_blocks = len(self.I.block) - 1
  #   N = np.zeros((n_blocks, n_blocks), dtype=int)

  #   # Criar um dicionário que mapeia cada bloco aos seus terminais
  #   block_in_network = {i: set() for i in range(n_blocks)}

  #   # Popular o dicionário com os blocos que cada rede contém
  #   for r in self.I.network:
  #     for i in range(n_blocks):
  #       if self._has_block(r, self.I.block[i]):
  #         block_in_network[i].add(r)
    
  #   # Calcular contagem de conexões
  #   for i in range(n_blocks):
  #     for j in range(i + 1, n_blocks): # Só verificar pares únicos, já que N[i][j] == N[j][i]
  #         common_networks = block_in_network[i].intersection(block_in_network[j])
  #         N[i][j] = len(common_networks)
  #         N[j][i] = N[i][j]  # Simetria
    
  #   return N

  def _network_count(self):
    n_blocks = len(self.I.block) - 1
    connection_matrix = np.zeros((n_blocks, n_blocks), dtype=float)

    # Criar um dicionário que mapeia cada bloco aos seus terminais e inicializar pesos de redes
    block_in_network = defaultdict(set)
    network_weights = {r: len(r.terminal) for r in self.I.network}  # Atribui peso com base na contagem de terminais da rede

    # Popular o dicionário com os blocos que cada rede contém
    for r in self.I.network:
      # Para cada bloco, adicione a rede que contém o bloco
      for block_index in range(n_blocks):
        if self._has_block(r, self.I.block[block_index]):
          block_in_network[block_index].add(r)

    # Calcular contagem de conexões com pesos
    for i in range(n_blocks):
      # Utilize um set para armazenar as redes já processadas
      processed_networks = set()
      for j in range(i + 1, n_blocks):  # Só verificar pares únicos
        common_networks = block_in_network[i].intersection(block_in_network[j])
        if common_networks:  # Somente processa se houver redes comuns
          # Calcula a soma dos pesos das redes comuns
          total_weight = sum(network_weights[n] for n in common_networks if n not in processed_networks)
          connection_matrix[i][j] = total_weight
          connection_matrix[j][i] = total_weight  # Simetria
          processed_networks.update(common_networks)  # Adiciona redes processadas

    return connection_matrix

  def _has_block(self, r, b):
    return any(t.block.ID == b.ID for t in r.terminal)

  def _mu_sigma(self, networks):
    network_array = np.array(networks)
    
    # Filtrar os valores que são maiores que zero (ignorar zeros)
    not_null = network_array[network_array > 0]

    mu = np.mean(not_null)
    sigma = np.std(not_null)
    return mu, sigma
  
  def calculate_connection_strength_matrix(self):
    mu, sigma = self._mu_sigma(self.connection_matrix)
    
    # Normaliza a matriz de conexões
    n_blocks = len(self.connection_matrix)
    strength_matrix = np.zeros((n_blocks, n_blocks))
    
    for i in range(n_blocks):
      for j in range(n_blocks):
        if i != j and self.connection_matrix[i][j] > 0:  # Evita normalizar a diagonal e valores nulos
          #strength_matrix[i][j] = (self.connection_matrix[i][j] - mu) / sigma
          
          # Aplica um peso na conexão
          weight = self.connection_matrix[i][j] / (np.sum(self.connection_matrix[i]) + 1e-10)  # Evita divisão por zero
          strength_matrix[i][j] = (self.connection_matrix[i][j] - mu) / sigma * weight

    features_normalized = StandardScaler().fit_transform(strength_matrix)
    return features_normalized

  def _calculate_normalized_internal_connectivity(self):
    """Calcula a conectividade interna normalizada dos grupos"""
    normalized_internal_connectivity_dict = {}
    index = 0

    for cluster in self.groups.get_groups():
      internal_connectivity = 0.0
      for i in range(len(cluster)):
        for j in range(i + 1, len(cluster)):
          internal_connectivity += self.connection_matrix[cluster[i]][cluster[j]]

      normalized_internal_connectivity = internal_connectivity / max((len(cluster) * (len(cluster) - 1)), 1e-10)
      normalized_internal_connectivity_dict[index] = normalized_internal_connectivity
      index += 1
    
    self.groups.set_normalized_internal_connectivity(normalized_internal_connectivity_dict)
    return self.groups.get_normalized_internal_connectivity()
  
  def _calculate_normalized_external_connectivity(self):
    """Calcula a conectividade externa normalizada dos grupos"""
    normalized_external_connectivity_dict = {}
    index = 0

    for cluster in self.groups.get_groups():
      external_connectivity = 0.0
      for i in cluster:
        for j in range(len(self.I.block)-1):
          if j not in cluster and i != j:
            external_connectivity += self.connection_matrix[i][j]
      
      normalized_external_connectivity = external_connectivity / (len(cluster) * ((len(self.I.block)-1) - len(cluster)))
      normalized_external_connectivity_dict[index] = normalized_external_connectivity
      index += 1
    
    self.groups.set_normalized_external_connectivity(normalized_external_connectivity_dict)
    return self.groups.get_normalized_external_connectivity()


  def calculate_internal_external_connectivity(self):
    self._calculate_normalized_internal_connectivity()
    self._calculate_normalized_external_connectivity()

  def dbscan(self, eps=1, min_samples=1):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(self.adjacency_matrix)

    # Transformar os labels de volta para uma representação de grupos
    unique_labels = set(labels)
    grouped = [[] for _ in unique_labels if _ != -1]  # Ignorar ruidosos (label -1)

    for idx, label in enumerate(labels):
      if label != -1:  # Ignorar ruidosos
        grouped[label].append(idx)

    self.groups.set_groups(grouped)
    self.groups.fit_predict(labels)

    return self.groups

  def plot_dendrogram(self, method='ward'):
    # Calcular as ligações para o dendrograma
    Z = linkage(self.adjacency_matrix, method=method)

    # Plotar o dendrograma
    plt.figure(figsize=(10, 7))
    dendrogram(Z, leaf_rotation=90., leaf_font_size=12.)
    plt.title('Dendrograma do Agrupamento Hierárquico')
    plt.xlabel('Índice dos Blocos')
    plt.ylabel('Distância')
    plt.grid(True)
    plt.show()
    plt.savefig(f'/home/cplex/dendrograma.png')
        
  def hierarchical_clustering(self, n_clusters):
    agglomerative = AgglomerativeClustering(n_clusters=n_clusters)
    labels = agglomerative.fit_predict(self.adjacency_matrix)

    # Transformar os labels de volta para uma representação de grupos
    grouped = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(labels):
      grouped[label].append(idx)

    self.groups.set_groups(grouped)
    self.groups.fit_predict(labels)

    return self.groups

  
  def calculate_internal_external_ratio(self):
    """
    Calcula a razão entre conectividade interna e externa.
    """
    self.calculate_internal_external_connectivity()

    ratio_dict = {}
    for group_id, internal in self.groups.get_normalized_internal_connectivity().items():
      external = self.groups.get_normalized_external_connectivity().get(group_id, 1e-10)

      ratio_dict[group_id] = internal / external
      #print(f'razão para o grupo {group_id} é: {internal} / {external} = {ratio_dict[group_id]}')

    return ratio_dict
  
  def calculate_absolute_difference(self):
    """
    Calcula a diferença absoluta ponderada entre conectividade interna e externa
    """

    absolute_diff = {}
    weight = 1.0

    for group_id, internal in self.groups.get_normalized_internal_connectivity().items():
      external = self.groups.get_normalized_external_connectivity().get(group_id)
      absolute_diff[group_id] = weight * abs (internal - external)
      print(f'Diferença Absoluta para o grupo {group_id} é: {weight} * |{internal} - {external}| = {absolute_diff[group_id]}')

    return absolute_diff

  def perform_clustering(self, initial_k, threshold=0.01, max_iter=10):
    """
      Método responsável pelo agrupamento, avaliação, refinamento e realocação dos blocos nos clusters.
      
      Entradas:
        initial_k: quantidade inicial de clusters


      Saída:
        grupos formados após o processo de avaliação, refinamento e realocação de blocos.
    
    """
    self.hierarchical_clustering(initial_k)

    iter = 0
    improvement = float('inf')

    while (iter <= max_iter):
      iter += 1
      #_ratio_dict = self.calculate_internal_external_ratio()    # Calula a relação interna/externa para cada grupo
      
      internal_connectivity_dict = self._calculate_normalized_internal_connectivity()
      print(internal_connectivity_dict)

      # Calcula a média da conectividade interna
      avg_internal_connectivity = np.mean(list(internal_connectivity_dict.values()))


      if iter == 1: 
        prev_avg_internal_connectivity = avg_internal_connectivity

      # Calcula a melhoria com base na diferença entre a conectividade interna atual e anterior
      improvement = abs(avg_internal_connectivity - prev_avg_internal_connectivity)
      print(f'Iteração: {iter}, Melhoria: {improvement}')

      # Atualiza a conectividade interna anterior
      prev_avg_internal_connectivity = avg_internal_connectivity

      # Se a melhoria for menor que o threshold, interrompe o refinamento
      # if improvement < threshold:
          # break

      # Refina os clusters com base na conectividade interna
      self._refine_clusters(internal_connectivity_dict)

    return self.groups
  
  def _refine_clusters(self, internal_connectivity_dict: dict):
    """
    Refina os clusters movendo blocos de grupos com baixa
    conectividade interna para grupos com maior conectividade.
    
    Entrada:
      internal_connectivity_dict: dicionário com conectividades internas de cada grupo
    """
    block_to_remove = {}
    for group_id, internal_connectivity in internal_connectivity_dict.items():
      if internal_connectivity <= 1:
        print(f'group_id: {group_id}: {self.groups.get_groups()[group_id]}')

        # Obtenha os blocos do grupo com baixa conectividade interna
        blocks_to_move = self.groups.get_groups()[group_id]
        
        for block in blocks_to_move:
          # Calcula a força de conexão deste bloco com os outros grupos
          best_group_id = None
          best_score = float('-inf')
          
          for other_group_id in range(len(self.groups.get_groups())):
            if other_group_id != group_id:
              # Calcular conectividade do bloco com o grupo
              score = self.calculate_connection_strength(block, other_group_id)
              
              # Comparar para encontrar o grupo com maior conectividade interna
              if score > best_score:
                best_group_id = other_group_id
                best_score = score
          
          # Se encontrar um grupo melhor, mover o bloco para lá
          if best_group_id is not None:
            best_group = self.groups.get_groups()[best_group_id]
            best_group.append(block)
            #blocks_to_move.remove(block)
            if group_id in block_to_remove:
              block_to_remove[group_id].append(block)           # Se já existir, adiciona o bloco à lista existente
            else:
              block_to_remove[group_id] = [block]               # Se não existir, cria uma nova lista com o bloco
        
    # Após realocar os blocos, elimina quaisquer listas vazias remanescentes
    print(f'Blocos para remover: {block_to_remove}')
    for _group_id, _block in block_to_remove.items():
      print(f'group_id: {_group_id}, block: {_block}')
      for b in _block:
        self.groups.get_groups()[_group_id].remove(b)
    self.groups.set_groups(list(filter(None, self.groups.get_groups())))
        

  def calculate_connection_strength(self, block, group_id):
    """
    Calcula a força de conexão entre um bloco e um grupo de blocos.

    Entrada:
        block: índice do bloco a ser avaliado
        group_id: índice do grupo com o qual a força de conexão será calculada

    Saída:
        score: força de conexão entre o bloco e o grupo
    """
    group_blocks = self.groups.get_groups()[group_id]
    strength = 0.0
    for i in group_blocks:
      strength += self.connection_matrix[block][i]
    
    normalized_strength = strength / len(group_blocks) 
    return normalized_strength
  

  def calculate_hpwl(self):
    """
    Calcula o HPWL de cada grupo de blocos.
    """
    hpwl_group = {}

    for group_id, blocks in enumerate(self.groups.get_groups()):
      total_hpwl = 0.0
      for block_id in blocks:
        block = self.I.block[block_id]
        for net in block.networks:
          terminal_positions = [(term.x, term.y) for term in net.terminals] 

          if not terminal_positions:
            continue  # Pula se a rede não tem terminais

          min_x = min(pos[0] for pos in terminal_positions)
          max_x = max(pos[0] for pos in terminal_positions)
          min_y = min(pos[1] for pos in terminal_positions)
          max_y = max(pos[1] for pos in terminal_positions)

          # Calcular o HPWL para a rede
          hpwl = (max_x - min_x) + (max_y - min_y)
          total_hpwl += hpwl

      hpwl_group[group_id] = total_hpwl

    self.groups.set_hpwl(hpwl_group)
    return self.groups.get_hpwl()