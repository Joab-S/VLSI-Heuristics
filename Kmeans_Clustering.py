from VLSI_class import VLSI
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

class VLSI_Clustering_K:
  def __init__(self, I):
    if not isinstance(I, VLSI):
      raise ValueError("I precisa ser um objeto VLSI")
    
    self.I = I

  def k_means(self, n_clusters, max_iterations = 10000):
        n_blocks = len(self.I.block) - 1
        adjacency_matrix = self.calculate_connection_strength_matrix()

        features = []
        for i in range(n_blocks):
            features.append(adjacency_matrix[i])
        features = np.array(features)

        # Normalização das features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        # Aplicar K-means++ clustering
        kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=10, max_iter=max_iterations)
        kmeans.fit(features_normalized)
        labels = kmeans.labels_

        # Transformar os labels de volta para uma representação de grupos
        groups = [[] for _ in range(n_clusters)]
        for idx, label in enumerate(labels):
            groups[label].append(idx)

        return groups

  def elbow_method(self, max_k=10):
    n_blocks = len(self.I.block) - 1
    adjacency_matrix = self._network_count()

    features = []
    for i in range(n_blocks):
        features.append(adjacency_matrix[i])
    features = np.array(features)

    # Normalização das features
    scaler = StandardScaler()
    features_normalized = scaler.fit_transform(features)

    inertia = []
    k_range = range(1, max_k + 1)

    for k in k_range:
      kmeans = KMeans(n_clusters=k, init='k-means++', random_state=0)
      kmeans.fit(features_normalized)
      inertia.append(kmeans.inertia_)

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
  
  def calculate_connection_strength_matrix(self):
    connection_matrix = self._network_count()
    mu, sigma = self._mu_sigma(connection_matrix)
    
    # Normaliza a matriz de conexões
    n_blocks = len(connection_matrix)
    strength_matrix = np.zeros((n_blocks, n_blocks))
    
    for i in range(n_blocks):
      for j in range(n_blocks):
        if i != j:  # Evita normalizar a diagonal
          strength_matrix[i][j] = (connection_matrix[i][j] - mu) / sigma
    
    return strength_matrix