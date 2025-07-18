from unittest.mock import Mock, patch

from estat_api_dlt_helper.api.client import EstatApiClient
from estat_api_dlt_helper.api.endpoints import ESTAT_ENDPOINTS


class TestEstatApiClient:
    """Test cases for EstatApiClient"""

    def test_init(self):
        """Test client initialization"""
        client = EstatApiClient(app_id="test_app_id")

        assert client.app_id == "test_app_id"
        assert client.base_url == ESTAT_ENDPOINTS["base_url"]
        assert client.timeout == 30
        assert client.session is not None

    def test_init_with_custom_params(self):
        """Test client initialization with custom parameters"""
        custom_url = "https://custom.api.url/"
        custom_timeout = 60

        client = EstatApiClient(
            app_id="test_app_id", base_url=custom_url, timeout=custom_timeout
        )

        assert client.base_url == custom_url
        assert client.timeout == custom_timeout

    @patch("requests.Session.get")
    def test_make_request_success(self, mock_get):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = EstatApiClient(app_id="test_app_id")
        response = client._make_request("test_endpoint", {"param1": "value1"})

        assert response == mock_response
        mock_get.assert_called_once()

        # Check that appId was added to params
        call_args = mock_get.call_args
        assert call_args[1]["params"]["appId"] == "test_app_id"
        assert call_args[1]["params"]["param1"] == "value1"

    @patch("requests.Session.get")
    def test_get_stats_data_success(self, mock_get):
        """Test successful statistics data retrieval"""
        # Mock response data
        mock_response_data = {
            "GET_STATS_DATA": {
                "STATISTICAL_DATA": {
                    "RESULT_INF": {
                        "TOTAL_NUMBER": "100",
                        "FROM_NUMBER": "1",
                        "TO_NUMBER": "100",
                    },
                    "TABLE_INF": {
                        "VALUE": [
                            {
                                "@tab": "01",
                                "@cat01": "001",
                                "@area": "00000",
                                "@time": "2020",
                                "$": "12345",
                            }
                        ]
                    },
                }
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = EstatApiClient(app_id="test_app_id")
        result = client.get_stats_data(stats_data_id="0000020202")

        assert result == mock_response_data
        mock_get.assert_called_once()

        # Verify default parameters
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["statsDataId"] == "0000020202"
        assert params["startPosition"] == 1
        assert params["limit"] == 100000
        assert params["metaGetFlg"] == "Y"

    @patch("requests.Session.get")
    def test_get_stats_data_with_custom_params(self, mock_get):
        """Test statistics data retrieval with custom parameters"""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = EstatApiClient(app_id="test_app_id")
        client.get_stats_data(
            stats_data_id="0000020202",
            start_position=10,
            limit=1000,
            meta_get_flg="N",
            cdCat01="001",  # additional parameter
        )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["startPosition"] == 10
        assert params["limit"] == 1000
        assert params["metaGetFlg"] == "N"
        assert params["cdCat01"] == "001"

    @patch("requests.Session.get")
    def test_get_stats_data_generator(self, mock_get):
        """Test statistics data generator for pagination"""
        # Mock first page response
        first_response_data = {
            "GET_STATS_DATA": {
                "STATISTICAL_DATA": {
                    "RESULT_INF": {
                        "TOTAL_NUMBER": "150",
                        "FROM_NUMBER": "1",
                        "TO_NUMBER": "100",
                    }
                }
            }
        }

        # Mock second page response
        second_response_data = {
            "GET_STATS_DATA": {
                "STATISTICAL_DATA": {
                    "RESULT_INF": {
                        "TOTAL_NUMBER": "150",
                        "FROM_NUMBER": "101",
                        "TO_NUMBER": "150",
                    }
                }
            }
        }

        mock_response1 = Mock()
        mock_response1.json.return_value = first_response_data
        mock_response1.raise_for_status.return_value = None

        mock_response2 = Mock()
        mock_response2.json.return_value = second_response_data
        mock_response2.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response1, mock_response2]

        client = EstatApiClient(app_id="test_app_id")
        pages = list(
            client.get_stats_data_generator(
                stats_data_id="0000020202", limit_per_request=100
            )
        )

        assert len(pages) == 2
        assert pages[0] == first_response_data
        assert pages[1] == second_response_data
        assert mock_get.call_count == 2

    @patch("requests.Session.get")
    def test_get_stats_list(self, mock_get):
        """Test statistics list retrieval"""
        mock_response_data = {
            "GET_STATS_LIST": {
                "DATALIST_INF": {
                    "LIST_INF": [
                        {"@id": "0000020202", "STAT_NAME": {"$": "Sample Statistics"}}
                    ]
                }
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = EstatApiClient(app_id="test_app_id")
        result = client.get_stats_list(search_word="人口")

        assert result == mock_response_data

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["searchWord"] == "人口"

    def test_close(self):
        """Test session closing"""
        client = EstatApiClient(app_id="test_app_id")

        with patch.object(client.session, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()


def test_api_client_integration():
    """Integration test with sample parameters (requires actual API key)"""
    import os

    import pytest

    api_key = os.getenv("ESTAT_API_KEY")
    if not api_key:
        pytest.skip("ESTAT_API_KEY environment variable not set")

    client = EstatApiClient(app_id=api_key)

    try:
        # Test with a known stats data ID with small limit
        result = client.get_stats_data(stats_data_id="0000020202", limit=10)

        # Verify the response structure
        assert "GET_STATS_DATA" in result
        assert "STATISTICAL_DATA" in result["GET_STATS_DATA"]

        # Test stats list endpoint
        list_result = client.get_stats_list(search_word="人口", limit=5)

        assert "GET_STATS_LIST" in list_result

    finally:
        client.close()
