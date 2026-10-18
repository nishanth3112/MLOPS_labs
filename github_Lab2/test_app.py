import pytest

from app import ACCURACY_THRESHOLD, PSI_THRESHOLD, app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def evaluate(client, accuracy, drift_psi):
    return client.post("/evaluate", json={"accuracy": accuracy, "drift_psi": drift_psi})


def test_default_thresholds():
    assert ACCURACY_THRESHOLD == 0.80
    assert PSI_THRESHOLD == 0.20


def test_root_returns_service_info(client):
    response = client.get("/")
    body = response.get_json()
    assert response.status_code == 200
    assert body["service"] == "ml-model-monitoring-api"
    assert body["version"]
    assert body["description"]
    assert "POST /evaluate" in body["endpoints"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "service": "ml-model-monitoring-api"}


def test_passing_metrics(client):
    response = evaluate(client, 0.92, 0.08)
    body = response.get_json()
    assert response.status_code == 200
    assert body["result"] == "pass"
    assert body["metrics"] == {"accuracy": 0.92, "drift_psi": 0.08}
    assert body["thresholds"]["min_accuracy"] == 0.80
    assert body["thresholds"]["max_drift_psi_exclusive"] == 0.20
    assert body["checks"] == {"accuracy_ok": True, "drift_psi_ok": True}
    assert body["reasons"]


@pytest.mark.parametrize(
    "accuracy, drift_psi, accuracy_ok, psi_ok",
    [
        (0.70, 0.08, False, True),
        (0.92, 0.35, True, False),
        (0.60, 0.50, False, False),
    ],
)
def test_metrics_requiring_review(client, accuracy, drift_psi, accuracy_ok, psi_ok):
    response = evaluate(client, accuracy, drift_psi)
    body = response.get_json()
    assert response.status_code == 200
    assert body["result"] == "review"
    assert body["checks"] == {"accuracy_ok": accuracy_ok, "drift_psi_ok": psi_ok}


@pytest.mark.parametrize(
    "accuracy, drift_psi, expected",
    [
        (0.80, 0.0, "pass"),  # accuracy exactly at the minimum passes
        (0.7999, 0.0, "review"),
        (0.95, 0.20, "review"),  # PSI exactly at the limit needs review
        (0.95, 0.1999, "pass"),
        (0.0, 0.0, "review"),
        (1.0, 0.0, "pass"),
        (1, 0, "pass"),  # integers are valid numbers
    ],
)
def test_threshold_boundaries(client, accuracy, drift_psi, expected):
    response = evaluate(client, accuracy, drift_psi)
    assert response.status_code == 200
    assert response.get_json()["result"] == expected


def test_malformed_json(client):
    response = client.post("/evaluate", data="{not json", content_type="application/json")
    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_request"


def test_missing_body(client):
    assert client.post("/evaluate").status_code == 400


def test_non_json_content_type(client):
    response = client.post("/evaluate", data="accuracy=0.9", content_type="text/plain")
    assert response.status_code == 400


@pytest.mark.parametrize("body", [[], [1, 2], "text", 5, None])
def test_body_must_be_object(client, body):
    response = client.post("/evaluate", json=body)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "body, missing",
    [
        ({}, ["accuracy", "drift_psi"]),
        ({"accuracy": 0.9}, ["drift_psi"]),
        ({"drift_psi": 0.1}, ["accuracy"]),
    ],
)
def test_missing_fields(client, body, missing):
    response = client.post("/evaluate", json=body)
    assert response.status_code == 400
    details = " ".join(response.get_json()["details"])
    for field in missing:
        assert f"'{field}' is required" in details


@pytest.mark.parametrize("bad", ["0.9", None, True, False, [0.9], {"v": 1}])
def test_incorrect_types(client, bad):
    assert evaluate(client, bad, 0.1).status_code == 400
    assert evaluate(client, 0.9, bad).status_code == 400


@pytest.mark.parametrize("raw", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_values(client, raw):
    for body in (
        f'{{"accuracy": {raw}, "drift_psi": 0.1}}',
        f'{{"accuracy": 0.9, "drift_psi": {raw}}}',
    ):
        response = client.post("/evaluate", data=body, content_type="application/json")
        assert response.status_code == 400


@pytest.mark.parametrize(
    "accuracy, drift_psi",
    [(-0.01, 0.1), (1.01, 0.1), (0.9, -0.01), (5, 0.1)],
)
def test_out_of_range_values(client, accuracy, drift_psi):
    assert evaluate(client, accuracy, drift_psi).status_code == 400


def test_multiple_errors_reported_together(client):
    response = evaluate(client, 2.0, -1.0)
    assert response.status_code == 400
    assert len(response.get_json()["details"]) == 2


def test_unknown_routes_and_methods(client):
    assert client.get("/nope").status_code == 404
    assert client.get("/evaluate").status_code == 405
