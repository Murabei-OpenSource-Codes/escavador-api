"""General calls to Escavador API.

Calls to ends points that will return information about the API, like credit
balance and monthly limit, but not related to any specific process, people or
companies.
"""
from escavador_api.fetch.base import FetchBaseMixin


class FetchGeneralMixin(FetchBaseMixin):
    """Mixin to handle general calls to Escavador API."""

    def get_credit_balance(self) -> dict:
        """Returns current credit balance.

        Returns:
            dict:
                JSON response returned by the Escavador API with current
                credit balance and monthly limit.

        Raises:
            EscavadorAPIAuthenticationError:
                HTTP 401.
            EscavadorAPIInsufficientCreditsException:
                HTTP 402.
            EscavadorAPINotFoundException:
                HTTP 404 or code ``NOT_FOUND``.
            EscavadorAPIInvalidDocumentException:
                Code ``NUMERO_CNJ_INVALIDO``, not the generic 422.
            EscavadorAPIInvalidParametersException:
                HTTP 422 or code ``UNPROCESSABLE_ENTITY``.
            EscavadorAPIRateLimitException:
                HTTP 429.
            EscavadorAPIUnmappedErrorException:
                When no class lists the status or ``code``.
        """
        url = "v1/quantidade-creditos"
        return self.get(url=url)
