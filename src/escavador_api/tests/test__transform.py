"""Test EscavadorAPI."""
import os
import unittest
from escavador_api.data import EscavadorAPI
from escavador_api.transform import TransformProcessData


ESCAVADOR_AUTH_TOKEN = os.getenv("ESCAVADOR_AUTH_TOKEN")
"""Escavador API authentication token."""
TEST_CPF_NUMBER = os.getenv("TEST_CPF_NUMBER")
"""CPF used by related-process tests."""


escavador_api = EscavadorAPI(ESCAVADOR_AUTH_TOKEN)
"""Escavador API instance."""


class TestEscavadorProcessAPI(unittest.TestCase):
    """Test EscavadorAPI methods."""

    def test_get_related_cpf_processes(self):
        """Test get related processes for a CPF number."""
        process_results = escavador_api.get_related_processes(
            cpf_cnpj=TEST_CPF_NUMBER)
        transformed_data = TransformProcessData.process_list(
            process_list=process_results)
        self.assertEqual(
            set(transformed_data.keys()), {'court_grades', 'involved'})
