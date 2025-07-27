# 基本的なデータロード（DuckDB）

## 概要

`load_estat_data`関数を使用して、e-Stat APIからDuckDBへデータをロードするもっともシンプルな方法を説明します。

## 利用シーン

- e-Stat APIからデータを取得してローカルで分析したい場合
- SQLを使用してデータを探索したい場合
- プロトタイピングや小規模なデータ分析したい場合
- クラウドサービスを使わずにローカルで完結させたい場合

## 必要な準備

1. e-Stat APIキーの設定
   ```bash
   export ESTAT_API_KEY="your-api-key-here"
   ```

2. 必要なパッケージのインストール
   ```bash
   pip install "estat-api-dlt-helper[duckdb]"
   ```

## コード例

```python
import os
import dlt
import duckdb
from estat_api_dlt_helper import EstatDltConfig, load_estat_data

def main():
    """Load social demographic municipal data to DuckDB."""
    db = duckdb.connect("estat_demo.duckdb")

    # Simple configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": "0000020201",  # 社会人口統計体系 市町村データ 人口・世帯データ
            "limit": 100,  # Small limit for demo
            "maximum_offset": 200,
        },
        "destination": {
            "pipeline_name": "estat_demo",
            "destination": dlt.destinations.duckdb(db),
            "dataset_name": "estat_api_data",
            "table_name": "social_demographic_municipal",
            "write_disposition": "replace",  # Replace existing data
        },
    }

    # Create config object
    estat_config = EstatDltConfig(**config)

    # Load data with one line
    print("Loading e-Stat data to DuckDB...")
    info = load_estat_data(estat_config)

    # Print results
    print("\nLoad completed!")
    print(f"Pipeline: {info.pipeline.pipeline_name}")
    print(f"Destination: {info.destination_name}")
    print(f"Dataset: {info.dataset_name}")

    # Access the data
    print("\nQuerying loaded data...")

    table_name = f"{estat_config.destination.dataset_name}.{estat_config.destination.table_name}"
    result = db.execute(f"SELECT COUNT(*) as row_count FROM {table_name}").fetchone()
    print(f"Total rows loaded: {result[0]}")

    # Show sample data
    print("\nSample data:")
    sample = db.execute(f"""
        SELECT *
        FROM {table_name} 
        LIMIT 5
    """).fetchdf()
    print(sample)

    db.close()

if __name__ == "__main__":
    main()
```

## 設定パラメータの説明

### sourceセクション
- `app_id`: e-Stat APIキー（必須）
- `statsDataId`: 統計表ID（必須）
- `limit`: 1回のAPIリクエストで取得する最大レコード数（デフォルト: 100,000）
- `maximum_offset`: 取得する最大レコード数の上限

### destinationセクション
- `pipeline_name`: dltパイプラインの名前
- `destination`: ロード先（この例ではDuckDB）
- `dataset_name`: データセット（スキーマ）名
- `table_name`: テーブル名
- `write_disposition`: 書き込み方法
  - `"replace"`: 既存データを削除して新規作成
  - `"append"`: 既存データに追加
  - `"merge"`: プライマリキーに基づいてマージ

## 実行結果の例

```
Loading e-Stat data to DuckDB...

Load completed!
Pipeline: estat_demo
Destination: duckdb
Dataset: estat_api_data

Querying loaded data...
Total rows loaded: 200

Sample data:
   tab cat01 cat02  ... time unit      value
0  001   001   001  ... 2019   人    123456
1  001   001   002  ... 2019   人     78901
...
```

## DuckDBでのデータ活用例

ロード後は通常のSQLでデータを分析できます。

```sql
-- 年別の集計
SELECT 
    time,
    SUM(CAST(value AS INTEGER)) as total_population
FROM estat_api_data.social_demographic_municipal
WHERE value != '-'
GROUP BY time
ORDER BY time;

-- 地域別の人口分布
SELECT 
    area,
    value
FROM estat_api_data.social_demographic_municipal
WHERE time = '2020'
ORDER BY CAST(value AS INTEGER) DESC
LIMIT 10;
```

## 次のステップ

- より高度な設定が必要な場合は[パイプラインの個別利用](./pipeline_example.md)を参照
- BigQueryへのロードは[BigQueryの例](./basic_load_example_bq.md)を参照
- 複数の統計表を扱う場合は[リソースの個別利用](./resource_example.md)を参照
