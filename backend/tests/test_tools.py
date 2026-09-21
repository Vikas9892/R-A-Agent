from unittest.mock import MagicMock, patch
from app.tools.calculator import calculator
from app.tools.weather import get_weather
from app.tools.web_search import web_search


def test_calculator_basic_arithmetic() -> None:
    assert calculator.invoke({"expression": "2 + 2"}) == "4"
    assert calculator.invoke({"expression": "10 * 5 - 8"}) == "42"
    assert calculator.invoke({"expression": "100 / 4"}) == "25.0"
    assert calculator.invoke({"expression": "2 ** 3"}) == "8"
    assert calculator.invoke({"expression": "(10 + 5) * 2"}) == "30"


def test_calculator_division_by_zero() -> None:
    result = calculator.invoke({"expression": "10 / 0"})
    assert "Division by zero" in result


def test_calculator_rejects_unsafe_code() -> None:
    result = calculator.invoke({"expression": "__import__('os').system('dir')"})
    assert "Error evaluating" in result or "Unsupported" in result


def test_weather_empty_city() -> None:
    result = get_weather.invoke({"city": "   "})
    assert "cannot be empty" in result


def test_weather_success_mocked() -> None:
    mock_geo_response = MagicMock()
    mock_geo_response.json.return_value = {
        "results": [{"name": "Paris", "country": "France", "latitude": 48.85, "longitude": 2.35}]
    }
    mock_geo_response.raise_for_status.return_value = None

    mock_weather_response = MagicMock()
    mock_weather_response.json.return_value = {
        "current_weather": {"temperature": 18.5, "windspeed": 12.0}
    }
    mock_weather_response.raise_for_status.return_value = None

    with patch("httpx.Client.get") as mock_get:
        mock_get.side_effect = [mock_geo_response, mock_weather_response]
        result = get_weather.invoke({"city": "Paris"})
        assert "Paris" in result
        assert "18.5°C" in result


def test_weather_city_not_found_mocked() -> None:
    mock_geo_response = MagicMock()
    mock_geo_response.json.return_value = {"results": []}
    mock_geo_response.raise_for_status.return_value = None

    with patch("httpx.Client.get", return_value=mock_geo_response):
        result = get_weather.invoke({"city": "UnknownCityXYZ"})
        assert "Could not locate weather data" in result


def test_web_search_empty_query() -> None:
    result = web_search.invoke({"query": ""})
    assert "cannot be empty" in result


def test_web_search_mocked_results() -> None:
    mock_results = [
        {
            "title": "FastAPI Framework",
            "body": "Modern, fast web framework for building APIs with Python.",
            "href": "https://fastapi.tiangolo.com",
        }
    ]

    with patch("app.tools.web_search.DDGS") as mock_ddgs_cls:
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = mock_results
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs_instance

        result = web_search.invoke({"query": "FastAPI"})
        assert "FastAPI Framework" in result
        assert "https://fastapi.tiangolo.com" in result
