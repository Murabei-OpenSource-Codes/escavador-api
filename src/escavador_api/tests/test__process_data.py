"""Test EscavadorAPI."""
import os
import unittest
from escavador_api.data import EscavadorAPI
from escavador_api.exceptions import EscavadorAPIInvalidDocumentException

ESCAVADOR_AUTH_TOKEN = os.getenv("ESCAVADOR_AUTH_TOKEN")
TEST_PROCESS_NUMBER = os.getenv("TEST_PROCESS_NUMBER")


class TestEscavadorAPI(unittest.TestCase):
    """Test EscavadorAPI methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.escavador_api = EscavadorAPI(ESCAVADOR_AUTH_TOKEN)

    def test_init(self):
        """Test EscavadorAPI initialization."""
        self.assertEqual(
            self.escavador_api.escavador_auth_token, ESCAVADOR_AUTH_TOKEN)
        self.assertEqual(
            self.escavador_api.BASE_URL, "https://api.escavador.com/api/")
        self.assertIn(
            "Authorization", self.escavador_api.headers)
        self.assertIn(
            "X-Requested-With", self.escavador_api.headers)

    def test_validate_process_number_valid(self):
        """Test _validate_process_number with valid input."""
        # Valid CNJ number
        result = self.escavador_api._validate_process_number(
            TEST_PROCESS_NUMBER)
        self.assertTrue(
            result)

    def test_validate_process_number_invalid(self):
        """Test _validate_process_number with invalid inputs."""
        with self.assertRaises(
            EscavadorAPIInvalidDocumentException):
            self.escavador_api._validate_process_number("invalid")

        with self.assertRaises(
            EscavadorAPIInvalidDocumentException):
            self.escavador_api._validate_process_number("Z1234567890123456789")

        with self.assertRaises(
            EscavadorAPIInvalidDocumentException):
            self.escavador_api._validate_process_number("94373466920263006300")

    def test_get_credit_balance(self):
        """Test get_credit_balance method."""
        result = self.escavador_api.get_credit_balance()
        self.assertEqual(
            list(result.keys()),
            ['quantidade_creditos', 'saldo',
             'saldo_descricao', 'limite_mensal'])

    def test_get_process_info(self):
        """Test get_process_info method."""
        result = self.escavador_api.get_process_info(
            process_number=TEST_PROCESS_NUMBER)
        self.assertEqual(
            list(result.keys()),
            ['numero_cnj', 'titulo_polo_ativo', 'titulo_polo_passivo',
             'ano_inicio', 'data_inicio', 'estado_origem', 'unidade_origem',
             'data_ultima_movimentacao', 'quantidade_movimentacoes',
             'fontes_tribunais_estao_arquivadas', 'data_ultima_verificacao',
             'tempo_desde_ultima_verificacao', 'processos_relacionados',
             'fontes'])

    def test_get_process_movements(self):
        """Test get_process_movements method."""
        result = self.escavador_api.get_process_movements(
            process_number=TEST_PROCESS_NUMBER)
        self.assertEqual(
            len(result), 17)
        self.assertEqual(
            list(result[0].keys()),
            ['id', 'data', 'tipo', 'pagina', 'tipo_publicacao',
             'classificacao_predita', 'conteudo', 'texto_categoria', 'fonte'])

    def test_request_process_update_public(self):
        """Test process update methods."""
        result = self.escavador_api.get_process_update_status(
            process_number=TEST_PROCESS_NUMBER)
        self.assertEqual(
            list(result.keys()),
            ['numero_cnj', 'data_ultima_verificacao',
             'tempo_desde_ultima_verificacao', 'ultima_verificacao', 'opcoes'])

    def test_request_ai_summary(self):
        """Test request_ai_summary method."""
        summary_id = self.escavador_api.request_ai_summary(
            process_number=TEST_PROCESS_NUMBER).get('id')

        if summary_id is not None:
            result = self.escavador_api.get_ai_summary_status(
                process_number=TEST_PROCESS_NUMBER, summary_id=summary_id)
            self.assertEqual(
                list(result.keys()),
                ['id', 'status', 'criado_em', 'numero_cnj', 'concluido_em'])

    def test_monitoring_new_process(self):
        """Test methods associated with new process monitoring."""
        # Create monitoring
        keyword = "TEST"
        keyword_variations = ["testing"]
        aux_keywords = [{"condicao": "NAO_CONTEM", "termo": "tested"}]
        courts = ["TJSP", "TJRJ", "TJMG"]

        result = self.escavador_api.create_monitoring_new_process(
            keyword=keyword,
            keyword_variations=keyword_variations,
            aux_keywords=aux_keywords,
            courts=courts)
        monitoring_id = result.get('id')
        self.assertEqual(
            list(result.keys()),
            ['id', 'termo', 'criado_em', 'variacoes', 'termos_auxiliares',
             'tribunais_especificos'])
        self.assertEqual(
            keyword, result.get('termo'))
        self.assertEqual(
            keyword_variations, result.get('variacoes'))
        self.assertEqual(
            set(courts), set(result.get('tribunais_especificos')))

        # Edit monitoring
        new_keyword_variations = ["testing_edit"]
        new_aux_keywords = [
            {"condicao": "CONTEM", "termo": "tested_edit"},
            {"condicao": "NAO_CONTEM", "termo": "tested_edit2"}]
        new_courts = ["TJRS", "TJSC"]
        result = self.escavador_api.edit_monitoring_new_process(
            monitoring_id=monitoring_id,
            keyword_variations=new_keyword_variations,
            aux_keywords=new_aux_keywords,
            courts=new_courts)
        self.assertEqual(
            list(result.keys()),
            ['id', 'termo', 'criado_em', 'variacoes', 'termos_auxiliares',
             'tribunais_especificos'])
        self.assertEqual(
            new_keyword_variations, result.get('variacoes'))
        self.assertEqual(
            set(new_courts), set(result.get('tribunais_especificos')))

        # Delete monitoring
        result = self.escavador_api.delete_monitoring_new_process(
            monitoring_id)
        self.assertTrue(
            result)

    def test_monitoring_existing_process(self):
        """Test methods associated with existing process monitoring."""
        # Create monitoring
        court = "TJSP"
        frequency = "SEMANAL"

        result = self.escavador_api.create_monitoring_existing_process(
            process_number=TEST_PROCESS_NUMBER,
            court=court,
            frequency=frequency)
        monitoring_id = result.get('id')
        self.assertEqual(
            list(result.keys()),
            ['id', 'numero', 'criado_em', 'data_ultima_verificacao',
             'tribunais', 'frequencia', 'status'])
        self.assertEqual(
            court, result.get('tribunais')[0].get('sigla'))
        self.assertEqual(
            frequency, result.get('frequencia'))

        # Delete monitoring
        result = self.escavador_api.delete_monitoring_existing_process(
            monitoring_id)
        self.assertTrue(
            result)
