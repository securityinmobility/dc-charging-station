"""Keeps the SECC leaf certificate of this charging station up to date.

The certificate is issued by the Hubject Open Plug&Charge Protocol (OPCP) PKI.
Running :func:`obtain_certificate` does the following:

1. log in to the Hubject API (OAuth2 client credentials)
2. ``GetAllCpoByUserName`` to list the end entities already registered
3. ``PutCpo`` in case our common name / EVSE ID is not registered yet
4. if no valid certificate is stored locally: create a private key + CSR and
   enroll it via the EST endpoint ``/.well-known/cpo/simpleenroll``
5. download the current CA certificates via ``/.well-known/cpo/cacerts`` and
   assemble ``cpoCertChain.pem`` (leaf + all parent certificates)

The files are written into the PKI directory used by the iso15118 stack, i.e.
``<PKI_PATH>/iso15118_2/{certs,csrs,private_keys}``.
"""

import base64
import json
import logging
import os
import re
import secrets
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)

# Hubject uses a single Auth0 host for both environments, the requested
# audience selects the environment.
DEFAULT_TOKEN_URL = "https://auth.eu.plugncharge.hubject.com/oauth/token"
OPCP_URLS = {
    "qa": "https://eu.plugncharge-qa.hubject.com",
    "prod": "https://eu.plugncharge.hubject.com",
}

# ISO 15118-2 SECC leaf certificates are only valid for three months, so renew
# them a while before they actually expire.
DEFAULT_RENEW_BEFORE_DAYS = 14


@dataclass
class HubjectConfig:
    """Everything needed to talk to the Hubject API, taken from the environment."""

    client_id: str
    client_secret: str
    token_url: str
    opcp_url: str
    audience: str
    organization: str
    country: str
    renew_before: timedelta
    # metadata sent with PutCpo, purely informational for Hubject
    end_entity_info: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "HubjectConfig":
        environment = os.environ.get("HUBJECT_ENV", "qa").lower()
        if environment not in OPCP_URLS:
            raise ValueError(
                f"HUBJECT_ENV must be one of {sorted(OPCP_URLS)}, got {environment!r}"
            )

        client_id = os.environ.get("HUBJECT_CLIENT_ID")
        client_secret = os.environ.get("HUBJECT_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise ValueError(
                "HUBJECT_CLIENT_ID and HUBJECT_CLIENT_SECRET need to be set in order "
                "to request a certificate from Hubject"
            )

        opcp_url = os.environ.get("HUBJECT_OPCP_URL", OPCP_URLS[environment]).rstrip("/")

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            token_url=os.environ.get("HUBJECT_TOKEN_URL", DEFAULT_TOKEN_URL),
            opcp_url=opcp_url,
            audience=os.environ.get("HUBJECT_AUDIENCE", opcp_url),
            organization=os.environ.get(
                "HUBJECT_ORGANIZATION", "Technische Hochschule Ingolstadt"
            ),
            country=os.environ.get("HUBJECT_COUNTRY", "DE"),
            renew_before=timedelta(
                days=int(
                    os.environ.get(
                        "HUBJECT_RENEW_BEFORE_DAYS", str(DEFAULT_RENEW_BEFORE_DAYS)
                    )
                )
            ),
            end_entity_info={
                "manufacture": os.environ.get("HUBJECT_MANUFACTURER", "chargebyte"),
                "deviceName": os.environ.get("HUBJECT_DEVICE_NAME", "EVAcharge SE"),
                "deviceSWVersion": os.environ.get("HUBJECT_DEVICE_SW_VERSION", "1.0"),
                "evseSerialNumber": os.environ.get("HUBJECT_EVSE_SERIAL", "1"),
                "ocppVersion": os.environ.get("HUBJECT_OCPP_VERSION", "2.0.1"),
            },
        )


class PkiPaths:
    """The file names the iso15118 stack expects, see its `shared/security.py`."""

    def __init__(self, pki_path: Path):
        self.root = pki_path
        self.certs = pki_path / "iso15118_2" / "certs"
        self.csrs = pki_path / "iso15118_2" / "csrs"
        self.private_keys = pki_path / "iso15118_2" / "private_keys"

        self.leaf_pem = self.certs / "seccLeafCert.pem"
        self.leaf_der = self.certs / "seccLeafCert.der"
        self.chain_pem = self.certs / "cpoCertChain.pem"
        self.sub_ca2_pem = self.certs / "cpoSubCA2Cert.pem"
        self.sub_ca2_der = self.certs / "cpoSubCA2Cert.der"
        self.sub_ca1_pem = self.certs / "cpoSubCA1Cert.pem"
        self.sub_ca1_der = self.certs / "cpoSubCA1Cert.der"
        self.root_pem = self.certs / "v2gRootCACert.pem"
        self.root_der = self.certs / "v2gRootCACert.der"

        self.csr_pem = self.csrs / "seccLeafCert.csr"
        self.csr_der = self.csrs / "seccLeafCert.csr.der"

        self.key = self.private_keys / "seccLeaf.key"
        self.key_password = self.private_keys / "seccLeafPassword.txt"

    def create_directories(self) -> None:
        for directory in (self.certs, self.csrs, self.private_keys):
            directory.mkdir(parents=True, exist_ok=True)


def get_pki_path() -> Path:
    """Where the certificates live - the same location the iso15118 stack uses."""
    pki_path = os.environ.get("PKI_PATH")
    if pki_path:
        return Path(pki_path)

    import iso15118.shared as iso15118_shared

    return Path(iso15118_shared.__file__).parent / "pki"


# Hubject only accepts EVSE IDs (and common names) matching this regex, see the
# error message of PutCpo. Note the mandatory 'E' after the operator ID, as
# required by DIN SPEC 91286. The alternative Hubject accepts as a common name
# is a SECC ID '[a-zA-Z]{2}-?[a-zA-Z0-9]{3}-?[S]-?[a-zA-Z0-9]{32,59}-?[a-zA-Z0-9]?',
# which can be used via SECC_COMMON_NAME.
EVSE_ID_PATTERN = re.compile(r"^[A-Z]{2}\*?[A-Z0-9]{3}\*?E[A-Z0-9*]{1,59}$")


def hubject_evse_id(evse_id: str) -> str:
    """Brings an EVSE ID into the notation Hubject expects ('DE*THI*E1234567').

    A type identifier other than 'E' (as in the ISO 15118 default EVSE ID
    'DE*THI*H007000000') is replaced, everything else is kept.
    """
    override = os.environ.get("HUBJECT_EVSE_ID")
    if override:
        return override.upper()

    evse_id = evse_id.upper()
    if EVSE_ID_PATTERN.match(evse_id):
        return evse_id

    parts = [part for part in re.split(r"[*\-]", evse_id) if part]
    if len(parts) < 3:
        raise ValueError(
            f"Cannot derive a Hubject EVSE ID from {evse_id!r}, expected something "
            "like 'DE*THI*E1234567' - or set HUBJECT_EVSE_ID"
        )

    country, operator, rest = parts[0], parts[1], parts[2:]
    # The character right after the operator ID is the type identifier
    if rest[0][0].isalpha():
        rest[0] = rest[0][1:]

    hubject_id = f"{country}*{operator}*E{''.join(rest)}"
    if not EVSE_ID_PATTERN.match(hubject_id):
        raise ValueError(
            f"{hubject_id!r} (derived from {evse_id!r}) is not a valid EVSE ID for "
            "Hubject - set HUBJECT_EVSE_ID"
        )

    logger.info("Using %s as the EVSE ID for Hubject", hubject_id)
    return hubject_id


def secc_common_name(evse_id: str) -> Tuple[str, str]:
    """Derives the common name of the SECC certificate from an EVSE ID.

    Hubject wants the common name with separators (``DE*THI*E1234567``) while
    the certificate itself carries it without them (``DETHIE1234567``).

    Returns:
        A tuple of (common name for Hubject, common name for the certificate).
    """
    override = os.environ.get("SECC_COMMON_NAME")
    if override:
        return override, _normalize(override)

    hubject_id = hubject_evse_id(evse_id)
    return hubject_id, _normalize(hubject_id)


def _normalize(common_name: str) -> str:
    """Strips everything but letters and digits, e.g. for comparing common names."""
    return re.sub(r"[^A-Z0-9]", "", common_name.upper())


def _request(
    url: str,
    method: str = "GET",
    body: Optional[bytes] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> bytes:
    request = urllib.request.Request(
        url, data=body, method=method, headers=headers or {}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"{method} {url} failed with HTTP {error.code}: {details}"
        ) from error


def login(config: HubjectConfig) -> str:
    """Step 1: get an OAuth2 access token for the Hubject API."""
    body = json.dumps(
        {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "audience": config.audience,
            "grant_type": "client_credentials",
        }
    ).encode()

    response = _request(
        config.token_url,
        method="POST",
        body=body,
        headers={"Content-Type": "application/json"},
    )
    access_token = json.loads(response)["access_token"]
    logger.debug("Got an access token for %s", config.audience)
    return access_token


def _auth_headers(access_token: str, **extra: str) -> Dict[str, str]:
    headers = {"Authorization": f"Bearer {access_token}"}
    headers.update(extra)
    return headers


def get_registered_common_names(config: HubjectConfig, access_token: str) -> Set[str]:
    """Step 2: GetAllCpoByUserName, returns the normalized common names."""
    response = _request(
        f"{config.opcp_url}/v1/vra/cpo/endEntities",
        headers=_auth_headers(access_token, Accept="application/json"),
    )
    payload = json.loads(response) if response.strip() else []

    common_names: Set[str] = set()
    _collect_common_names(payload, common_names)
    logger.debug("Hubject knows %d end entities", len(common_names))
    return common_names


def _collect_common_names(payload, common_names: Set[str]) -> None:
    """Walks the (loosely specified) JSON response and picks up all identifiers."""
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, str) and key.lower() in (
                "commonname",
                "id",
                "seccid",
                "endentityid",
            ):
                common_names.add(_normalize(value))
            else:
                _collect_common_names(value, common_names)
    elif isinstance(payload, list):
        for item in payload:
            _collect_common_names(item, common_names)


def register_cpo(
    config: HubjectConfig, access_token: str, common_name: str, evse_id: str
) -> None:
    """Step 3: PutCpo, registers the common name / EVSE ID at Hubject."""
    body: Dict[str, object] = dict(config.end_entity_info)
    body["commonName"] = common_name
    body["evseID"] = [evse_id]

    _request(
        f"{config.opcp_url}/v1/vra/cpo/endEntities",
        method="PUT",
        body=json.dumps(body).encode(),
        headers=_auth_headers(access_token, **{"Content-Type": "application/json"}),
    )
    logger.info("Registered %s (EVSE ID %s) at Hubject", common_name, evse_id)


def simple_enroll(
    config: HubjectConfig, access_token: str, csr_pem: bytes
) -> x509.Certificate:
    """Step 4: EST simpleenroll, returns the issued SECC leaf certificate."""
    response = _request(
        f"{config.opcp_url}/.well-known/cpo/simpleenroll",
        method="POST",
        body=csr_pem,
        headers=_auth_headers(access_token, **{"Content-Type": "application/pkcs10"}),
    )

    certificates = _parse_certificates(response)
    if not certificates:
        raise RuntimeError("simpleenroll did not return a certificate")
    if len(certificates) > 1:
        # Some deployments return the whole chain, the leaf is the one that is
        # not a CA certificate.
        leafs = [cert for cert in certificates if not _is_ca(cert)]
        if leafs:
            return leafs[0]
    return certificates[0]


def get_ca_certificates(
    config: HubjectConfig, access_token: str
) -> List[x509.Certificate]:
    """Step 5a: EST cacerts, returns all CA certificates Hubject currently uses."""
    response = _request(
        f"{config.opcp_url}/.well-known/cpo/cacerts",
        headers=_auth_headers(access_token),
    )
    certificates = _parse_certificates(response)
    logger.debug("Downloaded %d CA certificates", len(certificates))
    return certificates


def _parse_certificates(payload: bytes) -> List[x509.Certificate]:
    """Reads certificates from PEM, DER, PKCS#7 or base64 encoded PKCS#7."""
    candidates = [payload.strip()]
    try:
        # EST answers are base64 encoded DER (RFC 7030), possibly line wrapped
        candidates.append(base64.b64decode(payload, validate=False))
    except Exception:  # noqa: BLE001 - the payload simply is not base64
        pass

    for candidate in candidates:
        if not candidate:
            continue
        for loader in (
            pkcs7.load_der_pkcs7_certificates,
            pkcs7.load_pem_pkcs7_certificates,
            lambda data: x509.load_pem_x509_certificates(data)
            if hasattr(x509, "load_pem_x509_certificates")
            else [x509.load_pem_x509_certificate(data)],
            lambda data: [x509.load_der_x509_certificate(data)],
        ):
            try:
                certificates = loader(candidate)
            except Exception:  # noqa: BLE001 - try the next encoding
                continue
            if certificates:
                return list(certificates)

    raise RuntimeError("Could not read any certificate from the response")


def _is_ca(certificate: x509.Certificate) -> bool:
    try:
        return certificate.extensions.get_extension_for_class(
            x509.BasicConstraints
        ).value.ca
    except x509.ExtensionNotFound:
        return False


def _not_valid_after(certificate: x509.Certificate) -> datetime:
    """Expiry date as an aware datetime, independent of the cryptography version."""
    not_after = getattr(certificate, "not_valid_after_utc", None)
    if not_after is None:
        not_after = certificate.not_valid_after.replace(tzinfo=timezone.utc)
    return not_after


def _common_name_of(certificate: x509.Certificate) -> str:
    attributes = certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if not attributes:
        return ""
    value = attributes[0].value
    return value if isinstance(value, str) else value.decode()


def build_chain(
    leaf: x509.Certificate, ca_certificates: Sequence[x509.Certificate]
) -> List[x509.Certificate]:
    """Step 5b: orders leaf -> sub CA 2 -> sub CA 1 -> ... -> root.

    Raises:
        RuntimeError: if the chain cannot be completed up to a self signed root.
    """
    by_subject: Dict[bytes, x509.Certificate] = {}
    for certificate in ca_certificates:
        by_subject[certificate.subject.public_bytes()] = certificate

    chain = [leaf]
    current = leaf
    while current.issuer != current.subject:
        issuer = by_subject.get(current.issuer.public_bytes())
        if issuer is None:
            raise RuntimeError(
                f"No issuer certificate for '{_common_name_of(current)}' in the "
                "certificates returned by cacerts"
            )
        chain.append(issuer)
        current = issuer

    return chain


def _load_key_password(paths: PkiPaths) -> bytes:
    """Reads (or creates) the password protecting the private key.

    The iso15118 stack reads this file with `readline().rstrip()`, so the file
    contains exactly one line.
    """
    if paths.key_password.exists():
        password = paths.key_password.read_text().splitlines()[0].rstrip()
        if password:
            return password.encode()

    password = secrets.token_hex(16)
    paths.key_password.write_text(f"{password}\n")
    paths.key_password.chmod(0o600)
    logger.info("Created a new private key password at %s", paths.key_password)
    return password.encode()


def _load_private_key(
    paths: PkiPaths, password: bytes
) -> Optional[ec.EllipticCurvePrivateKey]:
    if not paths.key.exists():
        return None
    key_bytes = paths.key.read_bytes()
    for key_password in (password, None):
        try:
            key = serialization.load_pem_private_key(key_bytes, password=key_password)
        except (ValueError, TypeError):
            continue
        if isinstance(key, ec.EllipticCurvePrivateKey):
            return key
        logger.warning("The private key %s is not an EC key", paths.key)
        return None
    logger.warning("Cannot read the existing private key %s", paths.key)
    return None


def _create_private_key(
    paths: PkiPaths, password: bytes
) -> ec.EllipticCurvePrivateKey:
    """ISO 15118-2 requires secp256r1 keys."""
    key = ec.generate_private_key(ec.SECP256R1())
    paths.key.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        )
    )
    paths.key.chmod(0o600)
    logger.info("Created a new private key at %s", paths.key)
    return key


def _create_csr(
    config: HubjectConfig,
    paths: PkiPaths,
    key: ec.EllipticCurvePrivateKey,
    common_name: str,
) -> bytes:
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, config.organization),
                    x509.NameAttribute(NameOID.COUNTRY_NAME, config.country),
                ]
            )
        )
        .sign(key, hashes.SHA256())
    )

    csr_pem = csr.public_bytes(serialization.Encoding.PEM)
    paths.csr_pem.write_bytes(csr_pem)
    paths.csr_der.write_bytes(csr.public_bytes(serialization.Encoding.DER))
    return csr_pem


def _keys_match(
    certificate: x509.Certificate, key: Optional[ec.EllipticCurvePrivateKey]
) -> bool:
    if key is None:
        return False

    def public_bytes(public_key) -> bytes:
        return public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    return public_bytes(certificate.public_key()) == public_bytes(key.public_key())


def _certificate_is_usable(
    config: HubjectConfig,
    paths: PkiPaths,
    common_name: str,
    key: Optional[ec.EllipticCurvePrivateKey],
) -> bool:
    """Step 4 (check): is the stored certificate ours, valid and complete?"""
    if not paths.leaf_pem.exists() or not paths.chain_pem.exists():
        return False

    try:
        certificate = x509.load_pem_x509_certificate(paths.leaf_pem.read_bytes())
    except ValueError:
        logger.warning("Cannot read the existing certificate %s", paths.leaf_pem)
        return False

    if _normalize(_common_name_of(certificate)) != _normalize(common_name):
        logger.info(
            "The stored certificate belongs to '%s', we need '%s'",
            _common_name_of(certificate),
            common_name,
        )
        return False

    if not _keys_match(certificate, key):
        logger.info("The stored certificate does not match the stored private key")
        return False

    expires_in = _not_valid_after(certificate) - datetime.now(timezone.utc)
    if expires_in <= config.renew_before:
        logger.info(
            "The stored certificate expires in %d days, renewing it", expires_in.days
        )
        return False

    # A chain file that only contains the leaf is of no use for TLS
    if len(_parse_certificates(paths.chain_pem.read_bytes())) < 2:
        logger.info("The stored certificate chain is incomplete")
        return False

    logger.info(
        "The stored certificate for %s is valid until %s",
        common_name,
        _not_valid_after(certificate).isoformat(),
    )
    return True


def _write_certificates(paths: PkiPaths, chain: List[x509.Certificate]) -> None:
    """Writes the leaf, the CAs and the chain file used for the TLS handshake."""
    leaf, parents = chain[0], chain[1:]

    paths.leaf_pem.write_bytes(leaf.public_bytes(serialization.Encoding.PEM))
    paths.leaf_der.write_bytes(leaf.public_bytes(serialization.Encoding.DER))

    # The chain handed to the EVCC contains the leaf and the sub CAs, but not
    # the root - the EVCC has to have the V2G root itself.
    intermediates = [cert for cert in parents if cert.issuer != cert.subject]
    chain_pem = b"".join(
        cert.public_bytes(serialization.Encoding.PEM) for cert in [leaf] + intermediates
    )
    paths.chain_pem.write_bytes(chain_pem)

    # cpoSubCA2 is the direct issuer of the leaf, cpoSubCA1 the one above
    for certificate, pem_path, der_path in zip(
        intermediates,
        (paths.sub_ca2_pem, paths.sub_ca1_pem),
        (paths.sub_ca2_der, paths.sub_ca1_der),
    ):
        pem_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        der_path.write_bytes(certificate.public_bytes(serialization.Encoding.DER))

    roots = [cert for cert in parents if cert.issuer == cert.subject]
    for root in roots[:1]:
        paths.root_pem.write_bytes(root.public_bytes(serialization.Encoding.PEM))
        paths.root_der.write_bytes(root.public_bytes(serialization.Encoding.DER))

    logger.info(
        "Wrote the certificate chain (%s) to %s",
        " <- ".join(_common_name_of(cert) for cert in chain),
        paths.chain_pem,
    )


def obtain_certificate(evse_id: str, force: bool = False) -> str:
    """Makes sure this station has a valid SECC leaf certificate from Hubject.

    Args:
        evse_id: The EVSE ID of this charging point, e.g. ``DE*THI*E1234567``.
        force: Request a new certificate even if the stored one is still valid.

    Returns:
        The path to the SECC leaf certificate.
    """
    config = HubjectConfig.from_env()
    paths = PkiPaths(get_pki_path())
    paths.create_directories()

    registered_name, common_name = secc_common_name(evse_id)
    password = _load_key_password(paths)
    key = _load_private_key(paths, password)

    if not force and _certificate_is_usable(config, paths, common_name, key):
        return str(paths.leaf_pem)

    access_token = login(config)

    if common_name not in get_registered_common_names(config, access_token):
        register_cpo(
            config, access_token, registered_name, hubject_evse_id(evse_id)
        )
    else:
        logger.info("%s is already registered at Hubject", registered_name)

    key = _create_private_key(paths, password)
    csr_pem = _create_csr(config, paths, key, common_name)
    leaf = simple_enroll(config, access_token, csr_pem)
    logger.info(
        "Hubject issued a certificate for '%s', valid until %s",
        _common_name_of(leaf),
        _not_valid_after(leaf).isoformat(),
    )

    chain = build_chain(leaf, get_ca_certificates(config, access_token))
    _write_certificates(paths, chain)

    return str(paths.leaf_pem)


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    print(
        obtain_certificate(
            os.environ.get("EVSE_ID", "DE*THI*H007000000"),
            force=os.environ.get("FORCE_CERTIFICATE_ENROLLMENT", "").lower()
            in ("1", "true", "yes"),
        )
    )
