---
title: ソースの利用（複数テーブル一括ロード）
description: create_estat_sourceを使用して複数の統計表を一括でロードする方法
---

# ソースの利用（複数テーブル一括ロード）

## 概要

`create_estat_source`を使用して、複数の統計表を一括でロードする方法を説明します。`EstatDltConfig`のリストを渡すことで、テーブルごとにリソースを持つdlt sourceを生成できます。

## 利用シーン

- 複数の統計表をまとめてロードしたい場合
- テーブルごとに異なる書き込み戦略（merge / replace / append）を指定したい場合
- dlt sourceとしてまとめて1つのパイプラインで実行したい場合

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

import dlt

from estat_api_dlt_helper import EstatDltConfig, create_estat_source


def main():
    """Load multiple e-Stat tables using create_estat_source."""
    app_id = os.getenv("ESTAT_API_KEY", "")

    configs = [
        EstatDltConfig(
            source={
                "app_id": app_id,
                "statsDataId": "0000020201",
                "limit": 100,
                "maximum_offset": 200,
            },
            destination={
                "destination": "duckdb",
                "dataset_name": "estat_multi",
                "table_name": "population",
                "write_disposition": "merge",
                "primary_key": ["time", "area", "cat01"],
            },
        ),
        EstatDltConfig(
            source={
                "app_id": app_id,
                "statsDataId": "0000020202",
                "limit": 100,
                "maximum_offset": 200,
            },
            destination={
                "destination": "duckdb",
                "dataset_name": "estat_multi",
                "table_name": "household",
                "write_disposition": "replace",
                "primary_key": None,
            },
        ),
    ]

    source = create_estat_source(configs)

    print(f"Source name: {source.name}")
    print(f"Resources: {list(source.resources.keys())}")

    # Create pipeline and run
    pipeline = dlt.pipeline(
        pipeline_name="estat_source_demo",
        destination="duckdb",
        dataset_name="estat_multi",
    )

    print("\nRunning pipeline...")
    info = pipeline.run(source)

    print("\nLoad completed!")
    print(f"Load info: {info}")


if __name__ == "__main__":
    main()
```

## create_estat_source のパラメータ

| パラメータ | 説明 | 例 |
| --- | --- | --- |
| `configs` | `EstatDltConfig`のリスト（各要素がリソースに対応） | `[EstatDltConfig(...), ...]` |
| `**source_kwargs` | `dlt.source`に渡す追加キーワード引数 | `name="my_source"` |

## 注意事項

各`EstatDltConfig`の`table_name`はソース内で一意である必要があります。同じ`table_name`を複数の設定で使用すると`ValueError`が発生します。

```python
# NG: table_nameが重複している
configs = [
    EstatDltConfig(
        source={"app_id": app_id, "statsDataId": "0000020201"},
        destination={"destination": "duckdb", "dataset_name": "estat", "table_name": "stats"},
    ),
    EstatDltConfig(
        source={"app_id": app_id, "statsDataId": "0000020202"},
        destination={"destination": "duckdb", "dataset_name": "estat", "table_name": "stats"},  # 重複
    ),
]
# ValueError: Duplicate table names found: ['stats']
```

## バリデーション

`create_estat_source`は以下の入力バリデーションを行います。

- `configs`が空リストの場合、`ValueError`を送出します
- 複数の設定で同じ`table_name`が指定されている場合、`ValueError`を送出します

## 実行結果の例

```
Source name: estat_source
Resources: ['population', 'household']

Running pipeline...

Load completed!
Load info: ...
```

## 次のステップ

- シンプルな使い方は[基本的なデータロード](./basic_load_example.md)を参照
- リソースレベルでのカスタマイズは[リソースの個別利用](./resource_example.md)を参照
- パイプラインレベルでのカスタマイズは[パイプラインの個別利用](./pipeline_example.md)を参照
