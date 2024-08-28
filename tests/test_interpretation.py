from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_interpret_cron_expression():
    # Define the cron expression to be tested
    cron_expression = "*/15 14 1,15 * 2-5"

    # Send a POST request to the /interpret endpoint with the cron expression
    response = client.post("/interpret", json={"expression": cron_expression})

    # Check that the response status code is 200 OK
    assert response.status_code == 200

    # Parse the response JSON data
    data = response.json()

    # Assert that the "expression" key is in the response data
    assert "expression" in data
    assert data["expression"] == cron_expression

    # Assert that the "valid" key is in the response data and is True
    assert "valid" in data
    assert data["valid"] is True

    # Assert that the "current_time" key is in the response data and matches the format
    assert "current_time" in data
    assert isinstance(data["current_time"], str)
    assert len(data["current_time"]) == 19  # Format should be 'YYYY-MM-DD HH:MM:SS'

    # Assert that the "next_occurrences" key is in the response data
    assert "next_occurrences" in data
    assert isinstance(data["next_occurrences"], list)
    assert len(data["next_occurrences"]) == 5

    # Assert that the "human_readable" key is in the response data
    assert "interpreted_meaning" in data
    assert isinstance(data["interpreted_meaning"], str)
    assert data["interpreted_meaning"].strip() != ""

    # Assert that the "detailed_description" key is in the response data
    assert "detailed_description" in data
    assert isinstance(data["detailed_description"], dict)
    assert "minutes" in data["detailed_description"]
    assert "hours" in data["detailed_description"]
    assert "day_of_month" in data["detailed_description"]
    assert "month" in data["detailed_description"]
    assert "day_of_week" in data["detailed_description"]

    # Assert that the "warnings" key is in the response data
    assert "warnings" in data
    assert isinstance(data["warnings"], list)

    # Optionally, validate the content of the warnings
    if data["warnings"]:
        assert all(isinstance(warning, str) for warning in data["warnings"])