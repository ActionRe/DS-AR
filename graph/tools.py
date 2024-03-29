import numpy as np


def get_sgp_mat(num_in, num_out, link):
    A = np.zeros((num_in, num_out))
    for i, j in link:
        A[i, j] = 1
    A_norm = A / np.sum(A, axis=0, keepdims=True)
    return A_norm


def edge2mat(link, num_node):
    A = np.zeros((num_node, num_node))
    for i, j in link:
        A[j, i] = 1
    return A


def get_k_scale_graph(scale, A):
    if scale == 1:
        return A
    An = np.zeros_like(A)
    A_power = np.eye(A.shape[0])
    for k in range(scale):
        A_power = A_power @ A
        An += A_power
    An[An > 0] = 1
    return An


def compute_weighted_graph(x, sigma):
    pairwise_distances_ = pairwise_distances(x)
    weighted_graph = np.exp(-pairwise_distances_ / sigma)
    return weighted_graph

def pairwise_distances(x):
    instances_norm = np.sum(x ** 2, axis=-1).reshape((x.shape[0], 1, x.shape[1]))
    return -2 * np.matmul(x, x.transpose((0, 2, 1))) + instances_norm + instances_norm.transpose((0, 2, 1))



def get_part_based_graph(num_node, self_link, parts):
    stack = []
    stack.append(edge2mat(self_link, num_node))
    for p in parts:
        opp = [(y, x) for (x, y) in p]
        stack.append(normalize_digraph(edge2mat(opp, num_node)))
        # stack.append(normalize_digraph(edge2mat(opp2, num_node)))
    A = np.stack(stack)
    return A


def normalize_digraph(A):
    Dl = np.sum(A, 0)
    h, w = A.shape
    Dn = np.zeros((w, w))
    for i in range(w):
        if Dl[i] > 0:
            Dn[i, i] = Dl[i] ** (-1)
    AD = np.dot(A, Dn)
    return AD


def compute_weighted_adjacency_matrix(adjacency_matrix, sigma):
    # 创建一个空数组来存储结果
    weighted_adjacency_matrix = np.zeros_like(adjacency_matrix)

    # 计算每个切片的带权重的邻接矩阵
    for i in range(adjacency_matrix.shape[0]):
        # 计算带权重的图
        weighted_graph = compute_weighted_graph(adjacency_matrix[i], sigma)
        # 将权重图与当前切片相乘
        weighted_adjacency_matrix[i] = adjacency_matrix[i] * weighted_graph

    return weighted_adjacency_matrix



def get_spatial_graph(num_node, self_link, inward, outward):
    I = edge2mat(self_link, num_node)
    In = normalize_digraph(edge2mat(inward, num_node))
    Out = normalize_digraph(edge2mat(outward, num_node))
    A = np.stack((I, In, Out))
    return A


def get_spatial_neigh(num_node, self_link, inward, outward):
    I = edge2mat(self_link, num_node)
    In = normalize_digraph(edge2mat(inward, num_node))
    Out = normalize_digraph(edge2mat(outward, num_node))
    A = np.stack((In, Out))
    return A


def get_self_loop(num_node, self_link):
    I = edge2mat(self_link, num_node)
    I = normalize_digraph(I)
    A = I
    return A


def normalize_adjacency_matrix(A):
    node_degrees = A.sum(-1)
    degs_inv_sqrt = np.power(node_degrees, -0.5)
    norm_degs_matrix = np.eye(len(node_degrees)) * degs_inv_sqrt
    return (norm_degs_matrix @ A @ norm_degs_matrix).astype(np.float32)


def k_adjacency(A, k, with_self=False, self_factor=1):
    assert isinstance(A, np.ndarray)
    I = np.eye(len(A), dtype=A.dtype)
    if k == 0:
        return I
    Ak = np.minimum(np.linalg.matrix_power(A + I, k), 1) \
         - np.minimum(np.linalg.matrix_power(A + I, k - 1), 1)
    if with_self:
        Ak += (self_factor * I)
    return Ak


def get_multiscale_spatial_graph(num_node, self_link, inward, outward):
    I = edge2mat(self_link, num_node)
    A1 = edge2mat(inward, num_node)
    A2 = edge2mat(outward, num_node)
    A3 = k_adjacency(A1, 2)
    A4 = k_adjacency(A2, 2)
    A1 = normalize_digraph(A1)
    A2 = normalize_digraph(A2)
    A3 = normalize_digraph(A3)
    A4 = normalize_digraph(A4)
    A = np.stack((I, A1, A2, A3, A4))
    return A


def get_uniform_graph(num_node, self_link, neighbor):
    A = normalize_digraph(edge2mat(neighbor + self_link, num_node))
    return A
