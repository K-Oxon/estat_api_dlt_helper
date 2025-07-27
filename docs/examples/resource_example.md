---
title: リソースの個別利用
description: create_estat_resourceを使用してdltリソースを詳細にカスタマイズし、複数の統計表やデータ前処理を扱う方法
---

# リソースの個別利用

## 概要

`create_estat_resource`を使用して、dltリソースを詳細にカスタマイズする方法を説明します。複数の統計表を扱う場合や、データの前処理を行いたい場合に有効です。

## 利用シーン

- 複数の統計表IDからデータを一括取得したい場合
- リソースレベルで書き込み設定をカスタマイズしたい場合
- プライマリキーを動的に設定したい場合
- データを取得しながら内容を確認したい場合
- 複数のリソースを組み合わせて使用したい場合

## 必要な準備

1. e-Stat APIキーの設定
   ```bash
   export ESTAT_API_KEY="your-api-key-here"
   ```

2. 必要なパッケージのインストール
   ```bash
   pip install estat-api-dlt-helper duckdb pandas
   ```

## コード例

```python
import os
import dlt
from estat_api_dlt_helper import EstatDltConfig, create_estat_resource

def main():
    """Create and use e-Stat resource manually."""
    # Configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": ["0000020203", "0000020204"],  # Multiple stats IDs
            "limit": 100,
            "maximum_offset": 200,
        },
        "destination": {
            "destination": "duckdb",
            "dataset_name": "estat_resource",
            "table_name": "multi_stats",
            "write_disposition": "append",
        },
    }

    estat_config = EstatDltConfig(**config)

    # Create resource with custom parameters
    print("Creating e-Stat resource...")
    resource = create_estat_resource(
        config=estat_config,
        name="multi_stats_resource",
        write_disposition="merge",  # Override config
        primary_key=["stats_data_id", "time", "area"],  # Custom primary key
        # selectedはdlt 1.0で非推奨
    )

    print(f"Resource name: {resource.name}")
    print(f"Resource write disposition: {resource.write_disposition}")
    print(f"Resource primary key: {resource.primary_key}")

    # Create a simple pipeline
    pipeline = dlt.pipeline(
        pipeline_name="resource_demo",
        destination="duckdb",
        dataset_name="estat_resource",
    )

    # Run with the resource
    print("\nRunning pipeline with resource...")
    info = pipeline.run(resource)

    print("\nLoad completed!")
    print(f"Tables created: {list(info.load_packages[0].schema_update.tables.keys())}")

    # Inspect the resource data generator
    print("\nInspecting resource data...")

    # Create a new resource instance to inspect data
    inspect_resource = create_estat_resource(
        config=estat_config,
        name="inspect_resource",
    )

    # Get first few records
    data_generator = inspect_resource()
    first_batch = next(data_generator)

    print(f"First batch schema: {first_batch.schema}")
    print(f"First batch shape: {first_batch.shape}")
    print(f"Columns: {first_batch.column_names}")

    # Convert to pandas for display
    df = first_batch.to_pandas()
    print("\nSample data (first 3 rows):")
    print(df.head(3))

if __name__ == "__main__":
    main()
```

## リソースのカスタマイズオプション

### create_estat_resource のパラメータ

| パラメータ          | 説明                                      | 例                                      |
| ------------------- | ----------------------------------------- | --------------------------------------- |
| `name`              | リソース名（テーブル名にも使用）          | `"my_stats_data"`                       |
| `primary_key`       | プライマリキーカラム                      | `["time", "area", "cat01"]`             |
| `write_disposition` | 書き込み方法                              | `"append"`, `"replace"`, `"merge"`      |
| `merge_key`         | マージ時のキー（primary_keyと異なる場合） | `["stats_data_id", "time"]`             |
| `columns`           | カラム定義（データ型、nullable等）        | `{"time": {"data_type": "timestamp"}}`  |
| `schema_contract`   | スキーマ変更の制御                        | `"freeze"`, `"evolve"`, `"discard_row"` |
| `file_format`       | ファイルフォーマットの指定                | `"parquet"`, `"jsonl"`                  |

## 実行結果の例

```
Creating e-Stat resource...
Resource name: multi_stats_resource
Resource write disposition: merge
Resource primary key: ['stats_data_id', 'time', 'area']

Running pipeline with resource...

Load completed!
Tables created: ['multi_stats_resource']

Inspecting resource data...
First batch schema: stats_data_id: string
                   tab: string
                   cat01: string
                   area: string
                   time: string
                   unit: string
                   value: string
First batch shape: (100, 8)
Columns: ['stats_data_id', 'tab', 'cat01', 'area', 'time', 'unit', 'value']

Sample data (first 3 rows):
   stats_data_id tab cat01   area   time unit    value
0      0000020203  01   001  00000  20200   人  126146099
1      0000020203  01   001  01000  20200   人   5224614
2      0000020203  01   001  02000  20200   人   1237984
```

## 高度な使用例

dltリソースのより高度な使用方法については、[dlt公式ドキュメント - Declare a resource](https://dlthub.com/docs/general-usage/resource#declare-a-resource)を参照してください。

特に以下のトピックが参考になります：

- リソースの並列化（`parallelized`パラメータ）
- スキーマ契約（`schema_contract`）によるスキーマ変更の制御
- ネストされたデータの処理（`nested_hints`）
- 動的なテーブル名の設定

## 次のステップ

- シンプルな使い方は[基本的なデータロード](./basic_load_example.md)を参照
- BigQueryへの展開は[BigQueryの例](./basic_load_example_bq.md)を参照
