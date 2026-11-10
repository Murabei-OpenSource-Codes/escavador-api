"""Lock the public-document request body and the documents route."""
import unittest
from unittest.mock import MagicMock

from escavador_api.data import EscavadorAPI


def valid_cnj() -> str:
    """Build one CNJ number that passes the local check digits."""
    sequence = "0000001"
    remaining = "20268010001"
    number_without_vd = sequence + remaining
    remainder = int(number_without_vd) * 100 % 97
    verification = 98 - remainder
    return "{sequence}{verification:02d}{remaining}".format(
        sequence=sequence, verification=verification, remaining=remaining)


class TestPublicDocumentMethods(unittest.TestCase):
    """New document methods keep the JSON body and the documents route."""

    def setUp(self):
        """Open a client with a dummy token."""
        self.api = EscavadorAPI("token")
        self.process_number = valid_cnj()

    def test_request_posts_json_documentos_publicos(self):
        """POST sends the public-document flag as JSON."""
        self.api.post = MagicMock(
            return_value={"id": 9, "status": "PENDENTE"})

        result = self.api.request_process_public_documents(
            self.process_number)

        self.assertEqual(result["id"], 9)
        kwargs = self.api.post.call_args.kwargs
        self.assertEqual(kwargs["json"], {"documentos_publicos": 1})
        self.assertNotIn("data", kwargs)
        self.assertIn("/solicitar-atualizacao", kwargs["url"])

    def test_get_process_documents_uses_public_documents_route(self):
        """The generator reads GET .../documentos-publicos."""
        seen = {}

        def fake_get(url, params=None):
            seen["url"] = url
            return {
                "items": [{
                    "key": "abc",
                    "movimentacoes_relacionadas": [{"id": 1}],
                }],
                "links": {},
            }

        self.api.get = fake_get
        items = list(self.api.get_process_documents(self.process_number))

        self.assertIn("/documentos-publicos", seen["url"])
        self.assertFalse(seen["url"].rstrip("/").endswith("/documentos"))
        self.assertEqual(items[0]["key"], "abc")
        self.assertEqual(items[0]["movimentacoes_relacionadas"][0]["id"], 1)
