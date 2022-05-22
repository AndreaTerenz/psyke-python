from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from psyke.schema import DiscreteFeature
from psyke.utils import get_default_random_seed
from tuprolog.theory import Theory
from typing import Iterable
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('psyke')


class Extractor(object):
    """
    An explanator capable of extracting rules from trained black box.

    Parameters
    ----------
    predictor : the underling black box predictor.
    discretization : A collection of sets of discretised features.
        Each set corresponds to a set of features derived from a single non-discrete feature.
    """

    def __init__(self, predictor, discretization: Iterable[DiscreteFeature] = None):
        self.predictor = predictor
        self.discretization = [] if discretization is None else list(discretization)

    def extract(self, dataframe: pd.DataFrame) -> Theory:
        """
        Extracts rules from the underlying predictor.

        :param dataframe: is the set of instances to be used for the extraction.
        :return: the theory created from the extracted rules.
        """
        raise NotImplementedError('extract')

    def predict(self, dataframe: pd.DataFrame) -> Iterable:
        """
        Predicts the output values of every sample in dataset.

        :param dataframe: is the set of instances to predict.
        :return: a list of predictions.
        """
        raise NotImplementedError('predict')

    def mae(self, dataframe: pd.DataFrame, predictor=None) -> float:
        """
        Calculates the predictions' MAE w.r.t. the instances given as input.

        :param dataframe: is the set of instances to be used to calculate the mean absolute error.
        :return: the mean absolute error (MAE) of the predictions.
        """
        predictions = np.array(self.predict(dataframe.iloc[:, :-1]))
        idx = ~np.isnan(predictions)
        return mean_absolute_error(dataframe.iloc[idx, -1] if predictor is None else
                                   predictor.predict(dataframe.iloc[idx, :-1]),
                                   predictions[idx])

    def mse(self, dataframe: pd.DataFrame, predictor=None) -> float:
        """
        Calculates the predictions' MSE w.r.t. the instances given as input.

        :param dataframe: is the set of instances to be used to calculate the mean squared error.
        :return: the mean squared error (MSE) of the predictions.
        """
        predictions = np.array(self.predict(dataframe.iloc[:, :-1]))
        idx = ~np.isnan(predictions)
        return mean_squared_error(dataframe.iloc[idx, -1] if predictor is None else
                                  predictor.predict(dataframe.iloc[idx, :-1]),
                                  predictions[idx])

    def r2(self, dataframe: pd.DataFrame, predictor=None) -> float:
        """
        Calculates the predictions' R2 score w.r.t. the instances given as input.

        :param dataframe: is the set of instances to be used to calculate the R2 score.
        :return: the R2 score of the predictions.
        """
        predictions = np.array(self.predict(dataframe.iloc[:, :-1]))
        idx = ~np.isnan(predictions)
        return r2_score(dataframe.iloc[idx, -1] if predictor is None else
                        predictor.predict(dataframe.iloc[idx, :-1]),
                        predictions[idx])

    @staticmethod
    def cart(predictor: cart.CartPredictor, discretization=None) -> Extractor:
        """
        Creates a new Cart extractor.
        """
        from psyke.cart import Cart
        return Cart(predictor, discretization)

    @staticmethod
    def iter(predictor, min_update: float = 0.1, n_points: int = 1, max_iterations: int = 600, min_examples: int = 250,
             threshold: float = 0.1, fill_gaps: bool = True, seed: int = get_default_random_seed()) -> Extractor:
        """
        Creates a new ITER extractor.
        """
        from psyke.regression.iter import ITER
        return ITER(predictor, min_update, n_points, max_iterations, min_examples, threshold, fill_gaps, seed)

    @staticmethod
    def gridex(predictor, grid, min_examples: int = 250, threshold: float = 0.1,
               seed: int = get_default_random_seed()) -> Extractor:
        """
        Creates a new GridEx extractor.
        """
        from psyke.regression.gridex import GridEx
        return GridEx(predictor, grid, min_examples, threshold, seed)

    @staticmethod
    def gridrex(predictor, grid, min_examples: int = 250, threshold: float = 0.1,
                seed: int = get_default_random_seed()) -> Extractor:
        """
        Creates a new GridREx extractor.
        """
        from psyke.regression.gridrex import GridREx
        return GridREx(predictor, grid, min_examples, threshold, seed)

    @staticmethod
    def cream(predictor, depth: int, dbscan_threshold: float,
              error_threshold: float, constant: bool = False) -> Extractor:
        """
        Creates a new CREAM extractor.
        """
        from psyke.regression.cream import CREAM
        return CREAM(predictor, depth, dbscan_threshold, error_threshold, constant)

    @staticmethod
    def creepy(predictor, depth: int, dbscan_threshold: float,
               error_threshold: float, constant: bool = False) -> Extractor:
        """
        Creates a new CReEPy extractor.
        """
        from psyke.regression.creepy import CReEPy
        return CReEPy(predictor, depth, dbscan_threshold, error_threshold, constant)

    @staticmethod
    def real(predictor, discretization=None) -> Extractor:
        """
        Creates a new REAL extractor.
        """
        from psyke.classification.real import REAL
        return REAL(predictor, [] if discretization is None else discretization)

    @staticmethod
    def trepan(predictor, discretization=None, min_examples: int = 0, max_depth: int = 3,
               split_logic=None) -> Extractor:
        """
        Creates a new Trepan extractor.
        """
        from psyke.classification.trepan import Trepan, SplitLogic
        if split_logic is None:
            split_logic = SplitLogic.DEFAULT
        return Trepan(predictor, [] if discretization is None else discretization, min_examples, max_depth, split_logic)
