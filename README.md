# estat_api_dlt_helper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

[e-Stat API](https://www.e-stat.go.jp/api/)からデータを取得しロードするhelper

ドキュメントは[こちら](https://k-oxon.github.io/estat_api_dlt_helper/)

## 概要

e-Stat APIを利用してデータを取得し、DWHなどのデータ基盤にロードするシーンでの活用を想定しています。

Pythonのライブラリとして動作し、以下の３つの機能を提供します。

- `parse_response`
  - APIのレスポンスをパースし、データとメタデータを結合させたArrow Tableを作成します。
- `estat_table` / `estat_source`
  - dltのsource/resourceデコレータを活用した宣言的APIです。
  - 単一の統計表には `estat_table()` 、複数の統計表をまとめて扱う場合は `estat_source()` を使います。
- `load_estat_data`
  - [dlt(data load tool)](https://dlthub.com/docs/intro)のラッパーとして動作し、
    統計表IDとテーブル名などを設定するだけで、簡単にDWHなどにロード可能です。
  - paginationや複数の統計表IDを同じテーブルにロードしたいケースなどを内部でいい感じに処理します。
- `create_estat_resource` / `create_estat_pipeline` / `create_estat_source`
  - dltのresource・pipeline・sourceをそれぞれ個別に生成し、dltの細かい設定や機能を使いこなしたい場合に使用します。
  - `create_estat_source`は複数の`EstatDltConfig`をまとめてdlt sourceを生成できます。

## モチベーションとコンセプト

それなりの数の政府統計の統計表を効率よくデータ基盤に抽出・ロードしたいというニーズをもとに生まれました。
e-Stat APIのレスポンスはある程度抽象化されているため、メタデータを本体データに結合するパーサーと、
データロードスクリプトを非常に抽象化・量産化できるdlt(data load tool)を組み合わせることで、上記を達成できると感じて実装を始めました。

コンセプト:

- なるべく統計表IDとテーブル名を記述するだけで動くものがいい
- 複数の統計表IDのロードや、マージ戦略などの設定にも対応したい
- 何のデータソース(統計表ID)を、どこに(DWH|データセット|テーブル)、ロードするか、という設定をなるべく同じところで記述したい
- どの統計表のレスポンスにも対応できるパーサーが欲しい

## インストール

```bash
pip install estat_api_dlt_helper

# BigQuery
pip install "estat_api_dlt_helper[bigquery]"

# Snowflake
pip install "estat_api_dlt_helper[snowflake]"

# duckdb
pip install "estat_api_dlt_helper[duckdb]"
```

## 使用方法

e-Stat APIに関して、ユーザー登録やアプリケーションIDの取得が完了している前提です。
取得したアプリケーションIDは環境変数に入れておいてください。

```bash
export ESTAT_API_KEY=YOUR_APP_ID
```

Win: 

```
$env:ESTAT_API_KEY = "YOUR_APP_ID"
```

`estat_table` / `estat_source` を使う場合は、dltのsecrets管理によりapp_idを自動解決できます。

secrets.toml:

```toml
[sources.estat]
app_id = "YOUR_APP_ID"
```

環境変数:

```bash
export SOURCES__ESTAT__APP_ID=YOUR_APP_ID
```

### parse_responseの使い方

e-Stat APIの`/rest/3.0/app/json/getStatsData`のレスポンスを`parse_response()`に渡すことで、
responseの`TABLE_INF.VALUE`の中身をテーブルとして、`CLASS_INF.CLASS_OBJ`の中身をメタデータとして名寄せさせたArrow Tableを生成することができます。

処理イメージ:

| response                                  | 加工後                                   |
| ----------------------------------------- | ---------------------------------------- |
| ![response](docs/img/2024-11-18-json.jpg) | ![加工後](docs/img/2024-11-18-table.jpg) |

see: [examples](examples/basic_parser_usage.py)

```python
import os
import pandas as pd
import requests

from estat_api_dlt_helper import parse_response

# API endpoint
url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

# Parameters for the API request
params = {
    "appId": os.getenv("ESTAT_API_KEY"),
    "statsDataId": "0000020201",  # 社会人口統計 市区町村データ 基礎データ
    "cdCat01": "A2101",           # 住民基本台帳人口（日本人）
    "cdArea": "01100,01101",      # 札幌市, 札幌市中央区
    "limit": 10
}
try:
    # Make API request
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    # Parse the response into Arrow table
    table = parse_response(data)
    # Print data
    print(table.to_pandas())

except requests.RequestException as e:
    print(f"Error fetching data from API: {e}")
except Exception as e:
    print(f"Error processing data: {e}")
```

### estat_table / estat_sourceの使い方

dltの `@dlt.resource` / `@dlt.source` デコレータを活用した宣言的APIです。
統計表IDを指定するだけでDLTのリソース/ソースを生成できます。

see: [examples](examples/estat_source_example.py)

単一の統計表を取得する場合:

> NOTE: `estat_table` を単体で使う場合、`app_id` は dlt の secrets 解決により
> `SOURCES__ESTAT_TABLE__APP_ID` 環境変数（または `secrets.toml` の `[sources.estat_table]` セクション）から探索されます。
> `estat_source` 経由で使う場合は `SOURCES__ESTAT__APP_ID`（`[sources.estat]`）から解決されます。
> 混乱を避けるには、`app_id` を明示的に渡すか、`estat_source` 経由で使うことを推奨します。

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

複数の統計表をまとめて取得する場合:

```python
from estat_api_dlt_helper import estat_source

# IDリストを指定（リソース名は自動的に estat_{id} になります）
source = estat_source(
    stats_data_ids=["0000020201", "0004028584"],
    limit=100,
    maximum_offset=200,
)
pipeline.run(source)

# 辞書でカスタムリソース名を指定することもできます
source = estat_source(
    stats_data_ids={"population": "0000020201", "gdp": "0004028584"},
    write_disposition="merge",
    primary_key=["time_code", "area_code"],
)
pipeline.run(source)
```

リソースごとに個別の設定が必要な場合は、`tables` パラメータを使います:

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

### インクリメンタルロード（増分ロード）

`estat_table` / `estat_source` は `dlt.sources.incremental` を使ったインクリメンタルロードに対応しています。
前回ロード以降の新しい時点のデータだけを取得できるため、定期パイプラインでの全件取得を避けられます。

see: [examples](examples/incremental_load_example.py)

```python
import dlt
from estat_api_dlt_helper import estat_table

pipeline = dlt.pipeline(
    pipeline_name="estat_incremental",
    destination="duckdb",
    dataset_name="estat_data",
)

resource = estat_table(
    stats_data_id="0000020201",
    write_disposition="merge",
    primary_key=["time", "area"],
    incremental=dlt.sources.incremental("time", initial_value="2020000000"),
)

# 初回: initial_value 以降のデータを取得
# 2回目以降: 前回の最大 time 値以降のデータのみ取得
pipeline.run(resource)
```

`estat_source` でも同様に指定でき、全リソースに共通の incremental 設定が適用されます:

```python
from estat_api_dlt_helper import estat_source

source = estat_source(
    stats_data_ids=["0000020201", "0004028584"],
    write_disposition="merge",
    primary_key=["time", "area"],
    incremental=dlt.sources.incremental("time", initial_value="2020000000"),
)
pipeline.run(source)
```

注意点:
- `write_disposition` は `"merge"` または `"append"` と組み合わせて使用してください
- 新しい時点の追加のみ検出されます。既存データの改訂（遡及改定）は検出できません
- time カラムの値（例: `"2020000000"`）は辞書順で時系列順になるため、文字列比較で正しく動作します

### load_estat_dataの使い方

[dlt(data load tool)](https://dlthub.com/docs/intro)のwrapperとして簡便なconfigで取得データを
DWH等にロードできます。

ロード可能なDWHについては[dltのドキュメント](https://dlthub.com/docs/dlt-ecosystem/destinations/)を参考にしてください。

see: [examples](examples/basic_load_example.py)

```python
# duckdbの場合
import os
import dlt
import duckdb
from estat_api_dlt_helper import EstatDltConfig, load_estat_data

db = duckdb.connect("estat_demo.duckdb")

# Simple configuration
config = {
    "source": {
        "app_id": os.getenv("ESTAT_API_KEY"), #(必須項目)
        "statsDataId": "0000020201",  # (必須項目) 人口推計
        "limit": 100,  # (Optional) 1 requestで取得する行数 | デフォルト:10万
        "maximum_offset": 200,  # (Optional) 最大取得行数
    },
    "destination": {
        "pipeline_name": "estat_demo",
        "destination": dlt.destinations.duckdb(db),
        "dataset_name": "estat_api_data",
        "table_name": "population_estimates",
        "write_disposition": "replace",  # Replace existing data
    },
}
estat_config = EstatDltConfig(**config)

# Load data with one line
info = load_estat_data(estat_config)
print(info)
```

### load_estat_dataの使い方 (Advanced)

`load_estat_data()`は簡単な設定でロードを可能にしますが、dltの細かい設定や機能を使いこなしたい場合(`dlt.transform`や`bigquery_adapter`など)は、
dltのresourceとpipelineをそれぞれ単体で生成し、既存のdltのコードと同じように扱うこともできます。

see: [examples (resource)](examples/resource_example.py)

see: [examples (pipeline)](examples/pipeline_example.py)

### create_estat_sourceの使い方

複数の統計表を一括でロードしたい場合は、`create_estat_source()`を使用できます。
`EstatDltConfig`のリストを渡すことで、複数のリソースをまとめたdlt sourceを生成します。

see: [examples](examples/source_example.py)

```python
import os
import dlt
from estat_api_dlt_helper import EstatDltConfig, create_estat_source

app_id = os.getenv("ESTAT_API_KEY")

configs = [
    EstatDltConfig(
        source={"app_id": app_id, "statsDataId": "0000020201"},
        destination={"destination": "duckdb", "dataset_name": "estat", "table_name": "population"},
    ),
    EstatDltConfig(
        source={"app_id": app_id, "statsDataId": "0004028584"},
        destination={"destination": "duckdb", "dataset_name": "estat", "table_name": "household",
                     "write_disposition": "replace", "primary_key": None},
    ),
]

source = create_estat_source(configs)

pipeline = dlt.pipeline(
    pipeline_name="estat_multi",
    destination="duckdb",
    dataset_name="estat",
)
info = pipeline.run(source)
print(info)
```

## Development

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest

# Format code
uv run ruff format src/
```
