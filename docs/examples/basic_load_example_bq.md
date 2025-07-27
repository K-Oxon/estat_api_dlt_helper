---
title: 基本的なデータロード（BigQuery）
description: load_estat_data関数を使用してe-Stat APIからGoogle BigQueryへデータをロードする方法とクラウド環境での設定例
---

# 基本的なデータロード（BigQuery）

## 概要

`load_estat_data`関数を使用して、e-Stat APIからGoogle BigQueryへデータをロードする方法を説明します。

## 利用シーン

- クラウド上でデータ分析したい場合
- 大規模なデータセットを扱いたい場合
- チームでデータを共有したい場合
- BigQuery MLなどの高度な分析機能を使用したい場合
- 他のGCPサービスと連携したい場合

## 必要な準備

1. Google Cloud Projectの設定
   - [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
   - BigQuery APIを有効化
   - サービスアカウントを作成し、認証情報をダウンロード

2. 環境変数の設定
   ```bash
   export ESTAT_API_KEY="your-api-key-here"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   ```

3. 必要なパッケージのインストール
   ```bash
   pip install estat-api-dlt-helper "dlt[bigquery]"
   ```

## コード例

```python
import os
import dlt
from estat_api_dlt_helper import EstatDltConfig, load_estat_data

# BigQuery設定
dlt.config["destination.bigquery.project_id"] = "YOUR_PROJECT_ID"
dlt.config["destination.bigquery.location"] = "asia-northeast1"
dlt.config["destination.bigquery.autodetect_schema"] = True

def main():
    """Load social demographic municipal data to BigQuery."""

    # Simple configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": "0000020201",  # 社会人口統計体系 市町村データ 人口・世帯データ
            "limit": 100,  # 1 requestで取得する行数 | デフォルト:10万
            "maximum_offset": 200,  # 最大取得行数
        },
        "destination": {
            "pipeline_name": "estat_demo",
            "destination": "bigquery",
            "dataset_name": "estat_api_data",
            "table_name": "social_demographic_municipal",
            "write_disposition": "replace",  # Replace existing data
            "dev_mode": True,
        },
    }

    # Create config object
    estat_config = EstatDltConfig(**config)

    # Load data with one line
    print("Loading e-Stat data to BigQuery...")
    info = load_estat_data(estat_config)

    # Print results
    print("\nLoad completed!")
    print(info)

if __name__ == "__main__":
    main()
```

## BigQuery固有の設定

### プロジェクトとロケーション

```python
# プロジェクトIDの設定（必須）
dlt.config["destination.bigquery.project_id"] = "my-gcp-project"

# データセットのロケーション（東京リージョン推奨）
dlt.config["destination.bigquery.location"] = "asia-northeast1"
```

### スキーマの自動検出

```python
# 自動的にスキーマを検出（推奨）
dlt.config["destination.bigquery.autodetect_schema"] = True
```

### 認証方法

#### 1. サービスアカウントキー（推奨）
```python
# 環境変数で設定
export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"

# またはコード内で設定
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/key.json"
```

#### 2. OAuth（ローカル開発用）

```bash
# gcloud CLIでログイン
# $ gcloud auth application-default login
```

## 高度な設定例

### パーティショニング | クラスタリングの設定

[dlt bigquery-adapter](https://dlthub.com/docs/dlt-ecosystem/destinations/bigquery#bigquery-adapter)
を参照してください。

[パイプラインの個別利用](./pipeline_example.md)及び[リソースの個別利用](./resource_example.md)を利用することで通常のdltと同じインスタンスを生成し、
bigquery-adapterを設定することができます。

## コスト最適化のヒント

**クラスタリング**: よく使用するフィルタ条件（area、cat01など）でクラスタリング

## トラブルシューティング

### 権限エラー
```
403 Access Denied: BigQuery BigQuery: Permission denied
```
→ サービスアカウントに`BigQuery データ編集者`ロールを付与

### データセットが見つからない
```
404 Not found: Dataset my-project:estat_api_data was not found
```
→ データセットは自動作成されます。プロジェクトIDが正しいか確認

### ロケーションエラー
```
Cannot read and write in different locations
```
→ すべてのデータセットを同じロケーションに統一

## 次のステップ

- より細かいdltの制御が必要な場合は以下を参照
  - [パイプラインの個別利用](./pipeline_example.md)
  - [リソースの個別利用](./resource_example.md)
- ローカルでの開発は[基本的なデータロード（DuckDB）](./basic_load_example.md)を参照
