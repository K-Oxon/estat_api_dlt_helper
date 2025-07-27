# パイプラインの個別利用

## 概要

`create_estat_pipeline`と`create_estat_resource`を個別に使用して、dltパイプラインをカスタマイズする方法を説明します。

## 利用シーン

- パイプラインの動作を細かく制御したい場合
- 開発モードでスキーマの変更を確認したい場合
- パイプラインの状態を詳細に管理したい場合
- 複数のリソースを段階的にロードしたい場合
- スキーマのエクスポート・インポートを行いたい場合

## 必要な準備

1. e-Stat APIキーの設定
   ```bash
   export ESTAT_API_KEY="your-api-key-here"
   ```

2. 必要なパッケージのインストール
   ```bash
   pip install estat-api-dlt-helper duckdb
   ```

## コード例

```python
import os
from estat_api_dlt_helper import (
    EstatDltConfig,
    create_estat_pipeline,
    create_estat_resource,
)

def main():
    """Create and run dlt pipeline manually."""
    # Configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": "0000020201",
            "limit": 100,
            "maximum_offset": 200,
        },
        "destination": {
            "destination": "duckdb",
            "dataset_name": "estat_api_data",
            "table_name": "social_demographic_municipal",
            "write_disposition": "merge",
            "primary_key": ["time", "cat01", "area"],
        },
    }

    estat_config = EstatDltConfig(**config)

    # Create pipeline with custom settings
    print("Creating dlt pipeline...")
    pipeline = create_estat_pipeline(
        config=estat_config,
        pipeline_name="custom_estat_pipeline",
        dev_mode=True,  # Enable development mode
        export_schema_path="./schemas",  # Export schemas
    )

    # Create resource
    print("Creating e-Stat resource...")
    resource = create_estat_resource(
        config=estat_config,
        name="census_resource",  # Custom resource name
    )

    # Run pipeline manually
    print("Running pipeline...")
    info = pipeline.run(
        resource,
        refresh="drop_resources",  # Drop existing resources
    )

    print(f"\nPipeline completed!")
    print(f"Pipeline name: {info.pipeline.pipeline_name}")
    print(f"Load packages: {len(info.load_packages)}")

    # Check pipeline state
    print(f"\nPipeline state:")
    print(f"Working directory: {pipeline.working_dir}")
    print(f"Dataset name: {pipeline.dataset_name}")
    print(f"Destination: {pipeline.destination}")

    # Show schema info
    schema = pipeline.default_schema
    print(f"\nSchema info:")
    print(f"Schema name: {schema.name}")
    print(f"Tables: {list(schema.tables.keys())}")

if __name__ == "__main__":
    main()
```

## パイプラインのカスタマイズオプション

### create_estat_pipeline のパラメータ

| パラメータ           | 説明                                           | 例                                |
| -------------------- | ---------------------------------------------- | --------------------------------- |
| `pipeline_name`      | パイプライン名を指定                           | `"my_custom_pipeline"`            |
| `dev_mode`           | 開発モード（実行毎に新しいデータセットを作成） | `True`                            |
| `export_schema_path` | スキーマのエクスポート先                       | `"./schemas"`                     |
| `import_schema_path` | スキーマのインポート元                         | `"./saved_schemas"`               |
| `progress`           | 進捗表示の設定                                 | `"log"`, `"tqdm"`                 |
| `refresh`            | スキーマのリフレッシュ方法                     | `"drop_resources"`, `"drop_data"` |

### リフレッシュモードの説明

- `"drop_sources"`: テーブル、ソース、リソース状態を削除
- `"drop_resources"`: テーブルとリソース状態を削除
- `"drop_data"`: データとリソース状態を削除（スキーマは保持）

## 実行結果の例

```
Creating dlt pipeline...
Creating e-Stat resource...
Running pipeline...

Pipeline completed!
Pipeline name: custom_estat_pipeline
Load packages: 1

Pipeline state:
Working directory: /path/to/.dlt/pipelines/custom_estat_pipeline
Dataset name: estat_api_data
Destination: duckdb

Schema info:
Schema name: estat_api_data
Tables: ['social_demographic_municipal']
```

## 開発モードでの利点

開発モード（`dev_mode=True`）を有効にすると、以下の利点があります。

1. **新しいデータセット作成**: 実行毎に日時サフィックス付きの新しいデータセットを作成
2. **実験的な変更**: 既存のデータに影響を与えずに実験可能
3. **デバッグ情報**: エラー時により詳細な情報が表示されます

## スキーマの管理

### スキーマのエクスポート

```python
pipeline = create_estat_pipeline(
    config=estat_config,
    export_schema_path="./schemas",
)
```

実行後、`./schemas`ディレクトリに以下のファイルが作成されます。
- `import_schema.yaml`: スキーマ定義
- `export_schema.yaml`: 実際のスキーマ状態

### スキーマのインポート

保存したスキーマを再利用：

```python
pipeline = create_estat_pipeline(
    config=estat_config,
    import_schema_path="./schemas/import_schema.yaml",
)
```

## 高度な使用例

### リソースを複数宛先にロード

```python
resource = create_estat_resource(
    config=config1,
    name="population_data",
)
pipline_1 = create_estat_pipeline(
    config=config_1,
    pipeline_name="pipeline_1",
)
pipline_2 = create_estat_pipeline(
    config=config_2,
    pipeline_name="pipeline_2",
)

info_1 = pipeline_1.run(resource)
info_2 = pipeline_2.run(resource)
```

### BigQuery Adapterを使用したクラスタリング

BigQueryで`cat01`カラムでクラスタリングする例：

```python
import os
import dlt
from dlt.destinations.adapters import bigquery_adapter
from estat_api_dlt_helper import (
    EstatDltConfig,
    create_estat_pipeline,
    create_estat_resource,
)

def main():
    """Create pipeline with BigQuery clustering."""
    # Configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": "0000020201",  # 社会人口統計体系 市町村データ
            "limit": 1000,
        },
        "destination": {
            "destination": "bigquery",
            "dataset_name": "estat_clustered",
            "table_name": "social_demographic_municipal",
            "write_disposition": "replace",
        },
    }

    estat_config = EstatDltConfig(**config)

    # Create pipeline for BigQuery
    pipeline = create_estat_pipeline(
        config=estat_config,
        pipeline_name="estat_bq_clustered",
    )

    # Create resource
    resource = create_estat_resource(
        config=estat_config,
        name="social_demographic_municipal",
    )

    # Apply BigQuery adapter for clustering
    bigquery_adapter(
        resource,
        cluster=["area", "cat01"]  # 地域とcat01でクラスタリング
    )

    # Run pipeline
    info = pipeline.run(resource)
    
    print(f"Pipeline completed: {info.pipeline.pipeline_name}")
    print(f"Table created with clustering on area and cat01")

if __name__ == "__main__":
    main()
```

## 次のステップ

- リソースレベルでのカスタマイズは[リソースの個別利用](./resource_example.md)を参照
- BigQueryへの展開は[BigQueryの例](./basic_load_example_bq.md)を参照
