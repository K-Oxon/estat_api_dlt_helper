"""Pytest configuration and shared fixtures."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_response_data():
    """Load sample response data for testing."""
    return {
        "GET_STATS_DATA": {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "正常に終了しました。",
                "DATE": "2024-11-15T10:59:51.634+09:00"
            },
            "PARAMETER": {
                "LANG": "J",
                "STATS_DATA_ID": "0000020201",
                "DATA_FORMAT": "J"
            },
            "STATISTICAL_DATA": {
                "TABLE_INF": {
                    "@id": "0000020201",
                    "STAT_NAME": {
                        "@code": "00200502",
                        "$": "社会・人口統計体系"
                    },
                    "GOV_ORG": {
                        "@code": "00200",
                        "$": "総務省"
                    },
                    "STATISTICS_NAME": "市区町村データ 基礎データ（廃置分合処理済）",
                    "TITLE": {
                        "@no": "0000020201",
                        "$": "Ａ　人口・世帯"
                    },
                    "CYCLE": "年度次",
                    "SURVEY_DATE": "0",
                    "OPEN_DATE": "2024-06-21",
                    "SMALL_AREA": 0,
                    "COLLECT_AREA": "市区町村",
                    "MAIN_CATEGORY": {
                        "@code": "99",
                        "$": "その他"
                    },
                    "SUB_CATEGORY": {
                        "@code": "99",
                        "$": "その他"
                    },
                    "OVERALL_TOTAL_NUMBER": 1830033,
                    "UPDATED_DATE": "2024-06-21",
                    "STATISTICS_NAME_SPEC": {
                        "TABULATION_CATEGORY": "市区町村データ",
                        "TABULATION_SUB_CATEGORY1": "基礎データ（廃置分合処理済）"
                    },
                    "DESCRIPTION": {
                        "TABULATION_CATEGORY_EXPLANATION": "社会・人口統計体系の市区町村ごとに集計したデータを提供します。"
                    },
                    "TITLE_SPEC": {
                        "TABLE_NAME": "Ａ　人口・世帯"
                    }
                },
                "CLASS_INF": {
                    "CLASS_OBJ": [
                        {
                            "@id": "tab",
                            "@name": "観測値",
                            "CLASS": {
                                "@code": "00001",
                                "@name": "観測値",
                                "@level": "1"
                            }
                        },
                        {
                            "@id": "cat01",
                            "@name": "Ａ　人口・世帯",
                            "CLASS": {
                                "@code": "A2101",
                                "@name": "A2101_住民基本台帳人口（日本人）",
                                "@level": "1",
                                "@unit": "人"
                            }
                        },
                        {
                            "@id": "area",
                            "@name": "地域",
                            "CLASS": [
                                {
                                    "@code": "01100",
                                    "@name": "北海道 札幌市",
                                    "@level": "2",
                                    "@parentCode": "01000"
                                },
                                {
                                    "@code": "01101",
                                    "@name": "北海道 札幌市 中央区",
                                    "@level": "3",
                                    "@parentCode": "01100"
                                }
                            ]
                        }
                    ]
                },
                "DATA_INF": {
                    "VALUE": [
                        {
                            "@tab": "00001",
                            "@cat01": "A2101",
                            "@area": "01100",
                            "@time": "2020100000",
                            "@unit": "人",
                            "$": "1973395"
                        },
                        {
                            "@tab": "00001",
                            "@cat01": "A2101",
                            "@area": "01101",
                            "@time": "2020100000",
                            "@unit": "人",
                            "$": "248680"
                        }
                    ]
                }
            }
        }
    }