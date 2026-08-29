import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.carrier import Carrier
from app.models.carrier_connection import CarrierConnection
from app.schemas.shipping import (
    CarrierResponse,
    ConnectionCreate,
    ConnectionPatch,
    ConnectionResponse,
)
from app.services.credential_crypto import (
    EncryptionError,
    decrypt_credentials,
    encrypt_credentials,
)
from app.services.providers.mock import verify as provider_verify

router = APIRouter()


def _error(code: str, http_status: int) -> JSONResponse:
    return JSONResponse(
        content={"code": code},
        status_code=http_status,
    )


def _carrier_keys(schema: list) -> list[str]:
    return [
        field["key"]
        for field in schema
        if isinstance(field, dict) and field.get("key")
    ]


def _to_response(connection: CarrierConnection) -> ConnectionResponse:
    schema = (
        connection.carrier.credential_schema
        if connection.carrier is not None
        else []
    )
    return ConnectionResponse(
        id=str(connection.id),
        carrierId=connection.carrier_id,
        status=connection.status,
        lastErrorCode=connection.last_error_code,
        credentialKeys=_carrier_keys(schema),
    )


def _validate_schema(
    credentials: dict[str, str],
    schema: list,
) -> str | None:
    """Returns an error code when credentials do not satisfy the schema."""
    for field in schema:
        if not isinstance(field, dict):
            continue
        if field.get("required"):
            value = (credentials.get(field.get("key"), "") or "").strip()
            if len(value) < 4:
                return "invalid_credentials"
    return None


@router.get(
    "/shipping/carriers",
    response_model=list[CarrierResponse],
)
def list_carriers():
    db: Session = SessionLocal()

    try:
        carriers = (
            db.query(Carrier)
            .filter(Carrier.is_active.is_(True))
            .order_by(Carrier.sorted_order)
            .all()
        )

        return carriers

    finally:
        db.close()


@router.get(
    "/shipping/connections",
    response_model=list[ConnectionResponse],
)
def list_connections():
    db: Session = SessionLocal()

    try:
        connections = (
            db.query(CarrierConnection)
            .all()
        )

        return [_to_response(connection) for connection in connections]

    finally:
        db.close()


@router.post(
    "/shipping/connections",
    response_model=ConnectionResponse,
    status_code=201,
)
def create_connection(data: ConnectionCreate):
    db: Session = SessionLocal()

    try:
        carrier = (
            db.query(Carrier)
            .filter(Carrier.id == data.carrierId)
            .first()
        )

        if carrier is None:
            return _error("carrier_not_found", 404)

        if not carrier.is_active:
            return _error("carrier_inactive", 400)

        schema_error = _validate_schema(
            data.credentials,
            carrier.credential_schema,
        )
        if schema_error is not None:
            return _error(schema_error, 400)

        ok, code = provider_verify(data.credentials)

        if not ok:
            http_status = 502 if code == "timeout" else 400
            return _error(code, http_status)

        encrypted = encrypt_credentials(
            json.dumps(data.credentials)
        )

        connection = CarrierConnection(
            carrier_id=carrier.id,
            status="connected",
            credentials_encrypted=encrypted,
            last_error_code=None,
        )

        db.add(connection)
        db.commit()
        db.refresh(connection)

        return _to_response(connection)

    except EncryptionError:
        db.rollback()
        return _error("internal", 500)

    except Exception:
        db.rollback()
        return _error("internal", 500)

    finally:
        db.close()


@router.post(
    "/shipping/connections/{connection_id}/test",
    response_model=ConnectionResponse,
)
def test_connection(connection_id: int):
    db: Session = SessionLocal()

    try:
        connection = (
            db.query(CarrierConnection)
            .filter(CarrierConnection.id == connection_id)
            .first()
        )

        if connection is None:
            return _error("connection_not_found", 404)

        if connection.carrier is not None and not connection.carrier.is_active:
            return _error("carrier_inactive", 400)

        plaintext = decrypt_credentials(
            connection.credentials_encrypted
        )
        credentials = json.loads(plaintext)

        ok, code = provider_verify(credentials)

        if ok:
            connection.status = "connected"
            connection.last_error_code = None
        else:
            connection.status = "error"
            connection.last_error_code = code

        db.commit()
        db.refresh(connection)

        return _to_response(connection)

    except EncryptionError:
        db.rollback()
        return _error("internal", 500)

    except Exception:
        db.rollback()
        return _error("internal", 500)

    finally:
        db.close()


@router.patch(
    "/shipping/connections/{connection_id}",
    response_model=ConnectionResponse,
)
def update_connection(
    connection_id: int,
    data: ConnectionPatch,
):
    db: Session = SessionLocal()

    try:
        connection = (
            db.query(CarrierConnection)
            .filter(CarrierConnection.id == connection_id)
            .first()
        )

        if connection is None:
            return _error("connection_not_found", 404)

        carrier = connection.carrier

        if carrier is not None and not carrier.is_active:
            return _error("carrier_inactive", 400)

        schema_error = _validate_schema(
            data.credentials,
            carrier.credential_schema if carrier is not None else [],
        )
        if schema_error is not None:
            return _error(schema_error, 400)

        ok, code = provider_verify(data.credentials)

        if not ok:
            http_status = 502 if code == "timeout" else 400
            return _error(code, http_status)

        encrypted = encrypt_credentials(
            json.dumps(data.credentials)
        )

        connection.credentials_encrypted = encrypted
        connection.status = "connected"
        connection.last_error_code = None

        db.commit()
        db.refresh(connection)

        return _to_response(connection)

    except EncryptionError:
        db.rollback()
        return _error("internal", 500)

    except Exception:
        db.rollback()
        return _error("internal", 500)

    finally:
        db.close()


@router.delete(
    "/shipping/connections/{connection_id}",
    status_code=204,
)
def delete_connection(connection_id: int):
    db: Session = SessionLocal()

    try:
        connection = (
            db.query(CarrierConnection)
            .filter(CarrierConnection.id == connection_id)
            .first()
        )

        if connection is None:
            return _error("connection_not_found", 404)

        db.delete(connection)
        db.commit()

        return None

    except Exception:
        db.rollback()
        return _error("internal", 500)

    finally:
        db.close()
