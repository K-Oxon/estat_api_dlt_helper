from typing import Any, Dict, Generator, Optional

import requests

from ..utils.logging import get_logger
from .endpoints import ESTAT_ENDPOINTS

logger = get_logger(__name__)


class EstatApiClient:
    """e-Stat API クライアント"""

    def __init__(
        self,
        app_id: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """Initialize e-Stat API client.

        Args:
            app_id: e-Stat API application ID
            base_url: Base URL for API (defaults to official endpoint)
            timeout: Request timeout in seconds
        """
        self.app_id = app_id
        self.base_url = base_url or ESTAT_ENDPOINTS["base_url"]
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"accept": "application/json"})

    def _make_request(
        self, endpoint: str, params: Dict[str, Any], **kwargs: Any
    ) -> requests.Response:
        """Make HTTP request to e-Stat API.

        Args:
            endpoint: API endpoint name
            params: Query parameters
            **kwargs: Additional arguments for requests

        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"

        # Add appId to params
        params = {"appId": self.app_id, **params}

        logger.debug(f"Making request to {url} with params: {params}")

        response = self.session.get(url, params=params, timeout=self.timeout, **kwargs)

        response.raise_for_status()
        return response

    def get_stats_data(
        self,
        stats_data_id: str,
        start_position: int = 1,
        limit: int = 100000,
        meta_get_flg: str = "Y",
        cnt_get_flg: str = "N",
        explanation_get_flg: str = "Y",
        annotation_get_flg: str = "Y",
        replace_sp_chars: str = "0",
        lang: str = "J",
        **additional_params: Any,
    ) -> Dict[str, Any]:
        """Get statistical data from e-Stat API.

        Args:
            stats_data_id: Statistical data ID
            start_position: Start position for data retrieval (1-based)
            limit: Maximum number of records to retrieve
            meta_get_flg: Whether to get metadata (Y/N)
            cnt_get_flg: Whether to get count only (Y/N)
            explanation_get_flg: Whether to get explanations (Y/N)
            annotation_get_flg: Whether to get annotations (Y/N)
            replace_sp_chars: Replace special characters (0: No, 1: Yes, 2: Remove)
            lang: Language (J: Japanese, E: English)
            **additional_params: Additional query parameters

        Returns:
            API response as dictionary
        """
        params = {
            "statsDataId": stats_data_id,
            "startPosition": start_position,
            "limit": limit,
            "metaGetFlg": meta_get_flg,
            "cntGetFlg": cnt_get_flg,
            "explanationGetFlg": explanation_get_flg,
            "annotationGetFlg": annotation_get_flg,
            "replaceSpChars": replace_sp_chars,
            "lang": lang,
            **additional_params,
        }

        response = self._make_request(ESTAT_ENDPOINTS["stats_data"], params)
        return response.json()

    def get_stats_data_generator(
        self, stats_data_id: str, limit_per_request: int = 100000, **kwargs: Any
    ) -> Generator[Dict[str, Any], None, None]:
        """Get statistical data as a generator for pagination.

        Args:
            stats_data_id: Statistical data ID
            limit_per_request: Number of records per request
            **kwargs: Additional parameters for get_stats_data

        Yields:
            Response data for each page
        """
        start_position = 1

        while True:
            response_data = self.get_stats_data(
                stats_data_id=stats_data_id,
                start_position=start_position,
                limit=limit_per_request,
                **kwargs,
            )

            # Extract data info
            stats_data = response_data.get("GET_STATS_DATA", {})
            statistical_data = stats_data.get("STATISTICAL_DATA", {})
            result_inf = statistical_data.get("RESULT_INF", {})

            # Get total number of records
            total_number = int(result_inf.get("TOTAL_NUMBER", 0))
            from_number = int(result_inf.get("FROM_NUMBER", 0))
            to_number = int(result_inf.get("TO_NUMBER", 0))

            logger.info(
                f"Retrieved records {from_number} to {to_number} of {total_number}"
            )

            yield response_data

            # Check if we've retrieved all records
            if to_number >= total_number:
                break

            # Update start position for next request
            start_position = to_number + 1

    def get_stats_list(
        self,
        search_word: Optional[str] = None,
        survey_years: Optional[str] = None,
        stats_code: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get list of available statistics.

        Args:
            search_word: Search keyword
            survey_years: Survey years (YYYY or YYYYMM-YYYYMM)
            stats_code: Statistics code
            **kwargs: Additional query parameters

        Returns:
            API response as dictionary
        """
        params = {}

        if search_word:
            params["searchWord"] = search_word
        if survey_years:
            params["surveyYears"] = survey_years
        if stats_code:
            params["statsCode"] = stats_code

        params.update(kwargs)

        response = self._make_request(ESTAT_ENDPOINTS["stats_list"], params)
        return response.json()

    def close(self) -> None:
        """Close the session."""
        self.session.close()
