from parameterized import parameterized_class
from psyke import logger
from psyke.utils.logic_utils import pretty_theory
from test import get_in_rule, get_not_in_rule
from test.psyke import initialize, data_to_struct
from tuprolog.solve.prolog import prolog_solver
import unittest


@parameterized_class(initialize('trepan'))
class TestTrepan(unittest.TestCase):

    def test_extract(self):
        logger.info(pretty_theory(self.expected_theory) + '\n')
        logger.info(pretty_theory(self.extracted_theory) + '\n')
        self.assertTrue(self.expected_theory.equals(self.extracted_theory, False))

    def test_predict(self):

        predictions = self.extractor.predict(self.test_set.iloc[:, :-1])
        solver = prolog_solver(static_kb=self.extracted_theory.assertZ(get_not_in_rule()).assertZ(get_in_rule()))

        substitutions = [solver.solveOnce(data_to_struct(data)) for _, data in self.test_set.iterrows()]
        index = self.test_set.shape[1] - 1
        expected = [str(query.solved_query.get_arg_at(index)) for query in substitutions]

        logger.info(expected)
        logger.info(predictions)

        # TODO: check tricky intervals conditions
        # self.assertTrue(predictions == expected)


if __name__ == '__main__':
    unittest.main()
