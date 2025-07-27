---
title: パーサーの基本的な使い方
description: parse_response関数を使用してe-Stat APIのレスポンスをApache Arrow形式に変換し、構造化されたデータを取得する方法
---

# パーサーの基本的な使い方

## 概要

`parse_response`関数を使用して、e-Stat APIのレスポンスをApache Arrow形式に変換する方法を説明します。

## 利用シーン

- e-Stat APIのレスポンスを構造化されたテーブル形式に変換したい場合
- dltを使わずに直接データを処理したい場合
- カスタムデータ処理パイプラインを構築したい場合
- レスポンスデータの構造を詳しく調査したい場合

## 必要な準備

1. e-Stat APIキーの設定
   ```bash
   export ESTAT_API_KEY="your-api-key-here"
   ```

2. 必要なパッケージのインストール
   ```bash
   pip install estat-api-dlt-helper requests pandas
   ```

## コード例

```python
import os
import requests
from estat_api_dlt_helper import parse_response

def main():
    """Main function to demonstrate parser usage."""
    # API endpoint
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

    # Parameters for the API request
    params = {
        "appId": os.getenv("ESTAT_API_KEY"),
        "statsDataId": "0000020201",  # 市区町村データ 基礎データ
        "limit": 100,
        "maximum_offset": 200,
    }

    # Check if API key is set
    if params["appId"] is None:
        print("Error: Please set your e-Stat API key")
        print("You can set it as an environment variable:")
        print("  export ESTAT_API_KEY='your-actual-api-key'")
        print("\nTo get an API key, register at:")
        print("  https://www.e-stat.go.jp/api/")
        return

    print("Fetching data from e-Stat API...")
    print(f"Stats Data ID: {params['statsDataId']}")

    try:
        # Make API request
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        # Check for API errors
        result = data.get("GET_STATS_DATA", {}).get("RESULT", {})
        if result.get("STATUS") != 0:
            error_msg = result.get("ERROR_MSG", "Unknown error")
            print(f"API Error: {error_msg}")
            return

        # Parse the response into Arrow table
        print("\nParsing response data...")
        table = parse_response(data)

        # Display table information
        print("\n" + "=" * 60)
        print("Table Information:")
        print("=" * 60)
        print(f"Number of rows: {table.num_rows}")
        print(f"Number of columns: {table.num_columns}")

        # Display column names
        print("\nColumns:")
        for col in table.column_names:
            col_type = table.schema.field(col).type
            print(f"  - {col}: {col_type}")

        # Display data
        # Convert to pandas DataFrame
        df = table.to_pandas()
        print(df.head(5))

    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()
```

## 出力されるデータ構造

`parse_response`関数は以下のカラムを持つArrowテーブルを返します。

| カラム名      | 型     | 説明                           |
| ------------- | ------ | ------------------------------ |
| stats_data_id | string | 統計表ID                       |
| tab           | string | 表章項目コード                 |
| cat01-cat15   | string | 分類事項コード（存在する場合） |
| area          | string | 地域コード                     |
| time          | string | 時間軸コード                   |
| unit          | string | 単位                           |
| value         | string | 統計値                         |
| annotation    | string | 注釈（存在する場合）           |

## 実行結果の例

```
Fetching data from e-Stat API...
Stats Data ID: 0000020201

Parsing response data...

============================================================
Table Information:
============================================================
Number of rows: 100
Number of columns: 9

Columns:
  - stats_data_id: string
  - tab: string
  - cat01: string
  - area: string
  - time: string
  - unit: string
  - value: string
  - annotation: string

   stats_data_id tab cat01   area   time unit    value annotation
0    0000020201  10  A2101  01100  20200   人  1973395       None
1    0000020201  10  A2101  01101  20200   人   197656       None
...
```

## Apache Arrowテーブルの活用

取得したArrowテーブルはさまざまな形式に変換できます。

```python
# Pandas DataFrameへの変換
df = table.to_pandas()

# PyArrow Parquetファイルとして保存
import pyarrow.parquet as pq
pq.write_table(table, 'estat_data.parquet')

# CSVファイルとして保存
import pyarrow.csv as csv
csv.write_csv(table, 'estat_data.csv')

# NumPy配列として取得（数値カラムのみ）
value_array = table.column('value').to_numpy()
```

## APIパラメータのカスタマイズ

特定の条件でデータを絞り込む場合は、以下のようにAPIパラメータを追加できます。

```python
params = {
    "appId": os.getenv("ESTAT_API_KEY"),
    "statsDataId": "0000020201",
    "cdCat01": "A2101",        # 分類事項でフィルタ
    "cdArea": "01100,01101",   # 地域コードでフィルタ
    "cdTime": "20200,20210",   # 時間軸でフィルタ
    "limit": 1000,
    "metaGetFlg": "N",         # メタ情報を取得しない
}
```

## 次のステップ

- dltを使用した自動化されたデータロードは[基本的なデータロード](./basic_load_example.md)を参照
- より複雑なデータ処理は[リソースの個別利用](./resource_example.md)を参照
