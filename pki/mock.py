"""A V2G PKI without any PKI behind it, used when Plug & Charge is not set up.

The certificates stored in the PKI directory are used as they are (which is
enough for TLS with a self made PKI) and no contract certificate is handed out,
so vehicles asking for one are told that none is available.
"""

import logging

from base_classes import NoCertificateAvailable, V2GPki

logger = logging.getLogger(__name__)


class MockV2GPki(V2GPki):
    def update_secc_certificate(self, evse_id: str):
        logger.info(
            "MockV2GPki.update_secc_certificate: using the stored certificates "
            "for %s as they are",
            evse_id,
        )

    def get_contract_certificate(
        self, base64_encoded_cert_installation_req: str, namespace: str
    ) -> str:
        logger.info("MockV2GPki.get_contract_certificate namespace %s", namespace)
        raise NoCertificateAvailable(
            "No PKI provider is configured, so no contract certificate can be "
            "installed in the vehicle"
        )
