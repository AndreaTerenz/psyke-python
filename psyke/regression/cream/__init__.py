from __future__ import annotations
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numpy import ndarray
from sklearn.linear_model import LinearRegression
from sklearn.mixture import GaussianMixture
from tuprolog.theory import Theory
from psyke.regression import ClusterExtractor, Node, ClosedCube, HyperCubeExtractor


class CREAM(ClusterExtractor):
    """
    Explanator implementing CREAM algorithm.
    """

    def __init__(self, predictor, depth: int, dbscan_threshold: float, error_threshold: float, constant: bool = False):
        super().__init__(predictor, depth, dbscan_threshold, error_threshold, constant)

    def _predict(self, data: dict[str, float]) -> float:
        data = {k: v for k, v in data.items()}
        return HyperCubeExtractor._get_cube_output(self._hypercubes.search(data), data)

    def __split_with_errors(self, right: ClosedCube, outer_cube: ClosedCube, data: pd.DataFrame, indices: ndarray):
        right.update(data.iloc[indices], self.predictor)
        left = outer_cube.copy()
        left.update(data.iloc[~indices], self.predictor)
        return right, self._calculate_error(data.iloc[indices, :-1], right), \
            left, self._calculate_error(data.iloc[~indices, :-1], left)

    def __eligible_cubes(self, gauss_pred: ndarray, node: Node):
        cubes = []
        for inner_cube in [self._create_cube(node.dataframe.iloc[np.where(gauss_pred == i)]) for i in range(2)]:
            indices = self.__indices(inner_cube, node.dataframe)
            if indices is None:
                continue
            right, right_e, left, left_e = self.__split_with_errors(inner_cube, node.cube, node.dataframe, indices)
            cubes.append((
                ((right_e + left_e) / 2, right.volume(), left.volume()),
                (right, indices, right_e), (left, ~indices, left_e)
            ))
        return cubes

    @staticmethod
    def __indices(cube: ClosedCube, data: pd.DataFrame) -> ndarray | None:
        indices = cube.filter_indices(data.iloc[:, :-1])
        if len(data.iloc[indices]) * len(data.iloc[~indices]) == 0:
            return None
        return indices

    def _iterate(self, surrounding: Node) -> None:
        to_split = [(self.error_threshold * 10, 1, surrounding)]
        while len(to_split) > 0:
            to_split.sort(reverse=True)
            (_, depth, node) = to_split.pop()
            gauss_pred = GaussianMixture(n_components=2).fit_predict(node.dataframe)

            cubes = self.__eligible_cubes(gauss_pred, node)
            if len(cubes) < 1:
                continue
            _, right, left = min(cubes)
            node.right = Node(node.dataframe[right[1]], right[0])
            node.cube.update(node.dataframe[left[1]], self.predictor)
            node.left = Node(node.dataframe[left[1]], left[0])

            if depth < self.depth:
                to_split += [
                    (error, depth + 1, n)
                    for (n, error) in zip(node.children, [right[2], left[2]]) if error > self.error_threshold
                ]

            #plt.scatter(node.dataframe.X, node.dataframe.Y,
            #            c=gauss_pred, s=.5)
            #plt.gca().set_aspect('equal')
            #plt.xlim((0, 1))
            #plt.ylim((0, 1))
            #plt.show()

    def _calculate_error(self, dataframe: pd.DataFrame, cube: ClosedCube) -> float:
        output = cube.output
        if isinstance(output, float):
            return abs(self.predictor.predict(dataframe) - output).mean()
        elif isinstance(output, LinearRegression):
            return abs(self.predictor.predict(dataframe) - output.predict(dataframe)).mean()

    @property
    def n_rules(self):
        return self._hypercubes.leaves
