"""General calls to Escavador API.

Calls to ends points that will return information about the API, like credit
balance and monthly limit, but not related to any specific process, people or
companies.
"""
from escavador_api.aux.base import BaseMixin


class GeneralMixin(BaseMixin):
    """Mixin to handle general calls to Escavador API."""

    def get_credit_balance(self):
        """Returns current credit balance.

        Returns:
            dict:
                JSON response returned by the Escavador API with current
                credit balance and monthly limit.

        Raises:
            EscavadorAPIProblemAPIException:
                If the Escavador API returns an HTTP error.
            EscavadorAPIUnmappedErrorException:
                If an unexpected error occurs during the request.
        """
        url = "v1/quantidade-creditos"
        return self.get(url=url)
