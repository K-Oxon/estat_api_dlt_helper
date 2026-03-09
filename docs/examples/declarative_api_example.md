---
title: 宣言的APIの利用（estat_table / estat_source）
description: estat_table と estat_source を使って単一または複数の統計表を dlt resource/source として扱う方法
---

# 宣言的APIの利用（estat_table / estat_source）

## 概要

`estat_table()` は単一の統計表を1つのdlt resourceとして扱いたい場合に使います。
`estat_source()` は複数の統計表をまとめてdlt sourceとして扱いたい場合に使います。

コード例そのものは [examples/estat_source_example.py](https://github.com/K-Oxon/estat_api_dlt_helper/blob/main/examples/estat_source_example.py) と
[examples/incremental_load_example.py](https://github.com/K-Oxon/estat_api_dlt_helper/blob/main/examples/incremental_load_example.py) を参照してください。

## app_id の解決

`estat_table` / `estat_source` を使う場合は、dltのsecrets管理により `app_id` を自動解決できます。

`estat_table` を単体で使う場合:

- `SOURCES__ESTAT_TABLE__APP_ID` 環境変数
- `secrets.toml` の `[sources.estat_table]`

`estat_source` 経由で使う場合:

- `SOURCES__ESTAT__APP_ID` 環境変数
- `secrets.toml` の `[sources.estat]`

混乱を避けるには、`app_id` を明示的に渡すか、`estat_source` 経由で使うことを推奨します。

## 単一の統計表を取得する

```python
import dlt

from estat_api_dlt_helper import estat_table

resource = estat_table(
    stats_data_id="0000020201",
    write_disposition="replace",
    limit=100,
    maximum_offset=200,
)

pipeline = dlt.pipeline(
    pipeline_name="estat",
    destination="duckdb",
    dataset_name="estat_data",
)
pipeline.run(resource)
```

## 複数の統計表をまとめて取得する

```python
from estat_api_dlt_helper import estat_source

source = estat_source(
    stats_data_ids=["0000020201", "0004028584"],
    limit=100,
    maximum_offset=200,
)
pipeline.run(source)
```

辞書でカスタムリソース名を指定することもできます。

```python
from estat_api_dlt_helper import estat_source

source = estat_source(
    stats_data_ids={"population": "0000020201", "gdp": "0004028584"},
    write_disposition="merge",
    primary_key=["time_code", "area_code"],
)
pipeline.run(source)
```

## tables パラメータで個別設定する

リソースごとに個別の設定が必要な場合は、`tables` パラメータを使います。

```python
from estat_api_dlt_helper import estat_source, estat_table

source = estat_source(
    tables=[
        estat_table(
            stats_data_id="0000020201",
            table_name="pop",
            write_disposition="merge",
            primary_key=["time_code"],
            limit=100,
            maximum_offset=200,
        ),
        estat_table(
            stats_data_id="0004028584",
            table_name="gdp",
            write_disposition="replace",
            limit=100,
            maximum_offset=200,
        ),
    ],
)
pipeline.run(source)
```

## インクリメンタルロード

`estat_table` / `estat_source` は `dlt.sources.incremental` を使ったインクリメンタルロードに対応しています。
前回ロード以降の新しい時点のデータだけを取得できるため、定期パイプラインでの全件取得を避けられます。

```python
import dlt

from estat_api_dlt_helper import estat_table

resource = estat_table(
    stats_data_id="0000020201",
    write_disposition="merge",
    primary_key=["time", "area"],
    incremental=dlt.sources.incremental("time", initial_value="2020000000"),
)
```

`estat_source` でも同様に指定でき、全リソースに共通の incremental 設定が適用されます。

## 注意点

- `write_disposition` は `"merge"` または `"append"` と組み合わせて使用してください。
- 新しい時点の追加のみ検出されます。既存データの改訂（遡及改定）は検出できません。
- time カラムの値は辞書順で時系列順になる前提です。

## 関連ページ

- `create_estat_source` を使う構成ベースの source 生成は [ソースの利用（複数テーブル一括ロード）](./source_example.md) を参照
- resource を直接組み立てる場合は [リソースの個別利用](./resource_example.md) を参照
- pipeline を直接組み立てる場合は [パイプラインの個別利用](./pipeline_example.md) を参照
