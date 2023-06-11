import numpy as np
import pandas as pd
from tuprolog.theory import Theory

from psyke import Target
from psyke.extraction.hypercubic import HyperCubeExtractor
from psyke.extraction.hypercubic.hypercube import Point, GenericCube, HyperCube

from sklearn.neighbors import BallTree


class DiViNE(HyperCubeExtractor):
    """
    Explanator implementing DiViNE algorithm.
    """

    def __init__(self, predictor, k: int = 5, patience: int = 15, close_to_center: bool = True,
                 discretization=None, normalization=None):
        super().__init__(predictor, Target.CLASSIFICATION, discretization, normalization)
        self.k = k
        self.patience = patience
        self.vicinity_function = DiViNE.__closest_to_center if close_to_center else DiViNE.__closest_to_corners

    @staticmethod
    def __pop(data: pd.DataFrame, idx: int = None) -> (Point, pd.DataFrame):
        if idx is None:
            idx = data.sample(1).index.values[0]
        t = data.T
        return DiViNE.__to_point(t.pop(idx)), t.T.reset_index(drop=True)

    @staticmethod
    def __to_point(instance) -> Point:
        point = Point(instance.index.values, instance.values)
        return point

    def __to_cube(self, point: Point) -> GenericCube:
        cube = HyperCube.cube_from_point(point.dimensions, self._output)
        cube._output = list(point.dimensions.values())[-1]
        return cube

    def __clean(self, data: pd.DataFrame) -> pd.DataFrame:
        tree = BallTree(data.iloc[:, :-1], leaf_size=2)
        _, idx = tree.query(data.iloc[:, :-1], k=self.k)
        # how many output classes are associated with the k neighbors
        count = np.array(list(map(lambda indices: len(data.iloc[indices].iloc[:, -1].unique()), idx)))
        # instances with neighbors of different classes are discarded
        return data[count == 1]

    def __sort_cubes(self):
        cubes = [(cube.diversity, i, cube) for i, cube in enumerate(self._hypercubes)]
        cubes.sort()
        self._hypercubes = [cube[2] for cube in cubes]

    def __closest(self, data: pd.DataFrame, cube: GenericCube) -> (Point, pd.DataFrame):
        tree = BallTree(data.iloc[:, :-1], leaf_size=2)
        return DiViNE.__pop(data,self.vicinity_function(tree, cube))

    @staticmethod
    def __closest_to_center(tree: BallTree, cube: GenericCube):
        return tree.query([list(cube.center().dimensions.values())], k=1)[1][0][-1]

    @staticmethod
    def __closest_to_corners(tree: BallTree, cube: GenericCube):
        distance, idx = tree.query([list(point.dimensions.values()) for point in cube.corners()], k=1)
        return idx[np.argmin(distance)][-1]

    def _extract(self, dataframe: pd.DataFrame, mapping: dict[str: int] = None, sort: bool = True) -> Theory:
        data = self.__clean(dataframe)

        while len(data) > 0:
            discarded = []
            patience = self.patience
            point, data = self.__pop(data)
            cube = self.__to_cube(point)

            while patience > 0 and len(data) > 0:
                other, data = self.__closest(data, cube)
                if cube.output == list(other.dimensions.values())[-1]:
                    cube = cube.merge_with_point(other)
                    data = data[~(cube.filter_indices(data.iloc[:, :-1]))].reset_index(drop=True)
                else:
                    patience -= 1
                    discarded.append(other)
            if cube.volume() > 0:
                cube.update(dataframe, self.predictor)
                self._hypercubes.append(cube)
            if len(discarded) > 0:
                data = pd.concat([data] + [d.to_dataframe() for d in discarded]).reset_index(drop=True)
        self.__sort_cubes()
        return self._create_theory(dataframe, sort)
