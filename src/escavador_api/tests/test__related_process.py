"""Test EscavadorAPI."""
import os
from typing import Any
import unittest
from escavador_api.data import EscavadorAPI


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
        result = escavador_api.get_related_processes(
            cpf_cnpj=TEST_CPF_NUMBER)
        self.assertNotEqual(len(result), 0)
        expected_keys = {
            'numero_cnj', 'titulo_polo_ativo', 'titulo_polo_passivo',
            'ano_inicio', 'data_inicio', 'estado_origem', 'unidade_origem',
            'data_ultima_movimentacao', 'quantidade_movimentacoes',
            'fontes_tribunais_estao_arquivadas', 'data_ultima_verificacao',
            'tempo_desde_ultima_verificacao', 'processos_relacionados',
            'monitoramento_id', 'fontes', 'id'}
        self.assertTrue(expected_keys.issubset(result[0].keys()))
