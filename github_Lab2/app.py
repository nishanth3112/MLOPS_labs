import math
import os

from flask import Flask, jsonify, request

SERVICE_NAME = "ml-model-monitoring-api"
VERSION = "1.0.0"
DESCRIPTION = (
    "Rules-based evaluation of model metrics supplied by the caller. "
    "It does not compute drift or train models."
)


def _read_threshold(env_name, default):
    raw = os.environ.get(env_name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"{env_name} must be a number, got {raw!r}")
    if not math.isfinite(value):
        raise ValueError(f"{env_name} must be finite, got {raw!r}")
    return value


# Demonstration defaults; override with env vars (e.g. --set-env-vars on Cloud Run).
ACCURACY_THRESHOLD = _read_threshold("ACCURACY_THRESHOLD", 0.80)
PSI_THRESHOLD = _read_threshold("PSI_THRESHOLD", 0.20)

ENDPOINTS = {
    "GET /": "Service information",
    "GET /health": "Liveness check",
    "POST /evaluate": "Evaluate accuracy and drift_psi against thresholds",
}

app = Flask(__name__)


def _validate_number(payload, field):
    """Return (value, error). Booleans are rejected because bool subclasses int."""
    if field not in payload:
        return None, f"'{field}' is required"
    value = payload[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None, f"'{field}' must be a number"
    value = float(value)
    if not math.isfinite(value):
        return None, f"'{field}' must be a finite number"
    return value, None


def _bad_request(errors):
    return jsonify({"error": "invalid_request", "details": errors}), 400


@app.get("/")
def index():
    return jsonify(
        {
            "service": SERVICE_NAME,
            "version": VERSION,
            "description": DESCRIPTION,
            "endpoints": ENDPOINTS,
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": SERVICE_NAME})


@app.post("/evaluate")
def evaluate():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _bad_request(["request body must be a JSON object"])

    accuracy, acc_error = _validate_number(payload, "accuracy")
    psi, psi_error = _validate_number(payload, "drift_psi")
    errors = [e for e in (acc_error, psi_error) if e]

    if acc_error is None and not 0.0 <= accuracy <= 1.0:
        errors.append("'accuracy' must be between 0 and 1")
    if psi_error is None and psi < 0.0:
        errors.append("'drift_psi' must be greater than or equal to 0")
    if errors:
        return _bad_request(errors)

    accuracy_ok = accuracy >= ACCURACY_THRESHOLD
    psi_ok = psi < PSI_THRESHOLD

    reasons = []
    if accuracy_ok:
        reasons.append(f"accuracy {accuracy} meets the minimum of {ACCURACY_THRESHOLD}")
    else:
        reasons.append(f"accuracy {accuracy} is below the minimum of {ACCURACY_THRESHOLD}")
    if psi_ok:
        reasons.append(f"drift_psi {psi} is below the maximum of {PSI_THRESHOLD}")
    else:
        reasons.append(f"drift_psi {psi} is at or above the maximum of {PSI_THRESHOLD}")

    return jsonify(
        {
            "result": "pass" if accuracy_ok and psi_ok else "review",
            "metrics": {"accuracy": accuracy, "drift_psi": psi},
            "thresholds": {
                "min_accuracy": ACCURACY_THRESHOLD,
                "max_drift_psi_exclusive": PSI_THRESHOLD,
            },
            "checks": {"accuracy_ok": accuracy_ok, "drift_psi_ok": psi_ok},
            "reasons": reasons,
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8080")))
