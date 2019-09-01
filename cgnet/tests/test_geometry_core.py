# Author: Brooke Husic
# Contributors: Dominik Lemm

import numpy as np
import torch

from cgnet.feature import Geometry

g_numpy = Geometry(method='numpy')
g_torch = Geometry(method='torch')

# Define sizes for a pseudo-dataset
frames = np.random.randint(10, 30)
beads = np.random.randint(5, 10)

# create random linear protein data
coords = np.random.randn(frames, beads, 3).astype(np.float32)

# Calculate redundant distances and create a simple neighbor list in which all
# beads see each other (shape [n_frames, n_beads, n_beads -1]).
_distance_pairs, _ = g_numpy.get_distance_indices(beads, [], [])
redundant_distance_mapping = g_numpy.get_redundant_distance_mapping(
    _distance_pairs)

neighbor_cutoff = np.random.uniform(0, 1)


def test_tile_methods_numpy_vs_torch():
    # Test to make sure geometry.tile is still equivalent between numpy
    # and pytorch

    # Create inputs for a 3d array that will have 24 elements
    A = np.array([np.random.randint(10) for _ in range(24)])

    # Make two likely different shapes for the array and the tiling
    # with friendly factors
    shape_one = [2,3,4]
    np.random.shuffle(shape_one)

    shape_two = [2,3,4]
    np.random.shuffle(shape_two)

    # Reshape A with the first shape
    A = A.reshape(*shape_one).astype(np.float32)

    # Test whether the tiling is equivalent to the second shape
    tile_numpy = g_numpy.tile(A, shape_two)
    tile_torch = g_torch.tile(torch.Tensor(A), shape_two)

    np.testing.assert_array_equal(tile_numpy, tile_torch)


def test_distances_and_neighbors_numpy_vs_torch():
    # Comparison of numpy and torch outputs for getting geometry.get_distances
    # and geometry.get_neighbors

    # Calculate distances, neighbors, and neighbor mask using the numpy
    # version of Geometry
    distances_numpy = g_numpy.get_distances(_distance_pairs,
                                            coords,
                                            norm=True)
    distances_numpy = distances_numpy[:, redundant_distance_mapping]
    neighbors_numpy, neighbors_mask_numpy = g_numpy.get_neighbors(
        distances_numpy,
        cutoff=neighbor_cutoff)

    # Calculate distances, neighbors, and neighbor mask using the torch
    # version of Geometry
    distances_torch = g_torch.get_distances(_distance_pairs,
                                            torch.from_numpy(coords),
                                            norm=True)
    distances_torch = distances_torch[:, redundant_distance_mapping]
    neighbors_torch, neighbors_mask_torch = g_torch.get_neighbors(
        distances_torch,
        cutoff=neighbor_cutoff)

    np.testing.assert_array_equal(distances_numpy, distances_torch)
    np.testing.assert_array_equal(neighbors_numpy, neighbors_torch)
    np.testing.assert_array_equal(neighbors_mask_numpy, neighbors_mask_torch)
