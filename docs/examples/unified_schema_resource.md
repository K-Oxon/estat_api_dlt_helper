# Unified Schema Resource

## 概要

Unified Schema Resourceは、複数のstatsDataIdからデータを取得する際に発生する「Schema at index X was different」エラーを解決するための機能です。

## なぜこの機能が必要になったか

### 問題の背景

e-Stat APIから複数のstatsDataIdのデータを取得する際、各データセットのメタデータ構造が異なることがあります。

具体的な例：
- あるデータセットの`time_metadata`には`parent_code`フィールドが含まれる
- 別のデータセットの`time_metadata`には`parent_code`フィールドが含まれない

```python
# データセットA
time_metadata: {
    "code": "2020",
    "name": "2020年",
    "level": "1"
}

# データセットB  
time_metadata: {
    "code": "202001",
    "name": "2020年1月",
    "level": "2",
    "parent_code": "2020"  # このフィールドが追加されている
}
```

この違いにより、PyArrowでテーブルを結合しようとすると以下のようなエラーが発生します：

```
pyarrow.lib.ArrowInvalid: Schema at index 1 was different: 
time_metadata: struct<code: string not null, name: string not null, level: string, parent_code: string>
vs
time_metadata: struct<code: string not null, name: string not null, level: string>
```

### 解決アプローチ

Unified Schema Resourceは、すべての可能なフィールドを含む統一されたPydanticモデルを使用することで、この問題を解決します。存在しないフィールドは自動的に`None`として扱われ、スキーマの一貫性が保たれます。

## 使用方法

### 基本的な使い方

```python
from estat_api_dlt_helper import EstatDltConfig
from estat_api_dlt_helper.loader.unified_schema_resource import create_unified_estat_resource
import dlt

# 設定の作成
config = EstatDltConfig(
    source={
        "app_id": "your_app_id",
        "statsDataId": ["0004028473", "0004028474", "0004028475"],  # 複数のID
        "limit": 100000,
    },
    destination={
        "pipeline_name": "estat_pipeline",
        "destination": dlt.destinations.duckdb("estat.duckdb"),
        "dataset_name": "estat_data",
        "table_name": "unified_stats",
        "write_disposition": "replace",
    }
)

# 統一スキーマリソースの作成
resource = create_unified_estat_resource(config)

# パイプラインの実行
pipeline = dlt.pipeline(
    pipeline_name=config.destination.pipeline_name,
    destination=config.destination.destination,
    dataset_name=config.destination.dataset_name,
)
load_info = pipeline.run(resource)
```

### 詳細な例

完全な動作例は `examples/unified_schema_example.py` を参照してください。

## 技術詳細

### 統一スキーマモデル

以下のような統一されたPydanticモデルを使用します：

```python
class UnifiedTimeMetadata(BaseModel):
    code: str = Field(description="Time code")
    name: str = Field(description="Time name")
    level: Optional[str] = Field(None, description="Time level")
    parent_code: Optional[str] = Field(None, description="Parent time code")
    unit: Optional[str] = Field(None, description="Time unit")
    extra_attributes: Dict[str, Any] = Field(default_factory=dict)
```

すべてのオプショナルフィールドを含むことで、どのようなメタデータ構造にも対応できます。

## 通常のリソースとの比較

### 通常のリソース（create_estat_resource）

- スキーマが完全に一致する単一または複数のstatsDataIdに適している
- より高速だが、スキーマの違いに対応できない
- スキーマエラーが発生する可能性がある

### 統一スキーマリソース（create_unified_estat_resource）

- スキーマが異なる複数のstatsDataIdに対応
- すべての可能なフィールドを含む統一モデルを使用
- スキーマエラーを完全に回避
- 若干のパフォーマンスオーバーヘッドがある

## いつ使用すべきか

以下の場合に統一スキーマリソースを使用してください：

1. 複数のstatsDataIdからデータを取得する場合
2. 「Schema at index X was different」エラーが発生した場合
3. データセット間でメタデータ構造が異なることが予想される場合
4. スキーマの一貫性を保証したい場合

## トラブルシューティング

### よくある問題

1. **パフォーマンスが遅い**
   - バッチサイズを調整してください（デフォルト: 1000）
   - データ量に応じて`limit`と`maximum_offset`を調整してください

2. **メモリ使用量が多い**
   - より小さなバッチサイズを使用してください
   - `maximum_offset`を設定してデータ量を制限してください

3. **特定のフィールドが欠落している**
   - `extra_dimensions`や`extra_metadata`フィールドを確認してください
   - 必要に応じて統一スキーマモデルを拡張してください

## 関連情報

- [DLT Schema Evolution](https://dlthub.com/docs/general-usage/schema-evolution)
- [e-Stat API仕様](https://api.e-stat.go.jp/swagger-ui/e-statapi3.0.html)
- `src/estat_api_dlt_helper/models/unified_schema.py` - 統一スキーマモデルの定義
- `src/estat_api_dlt_helper/loader/unified_schema_resource.py` - 実装の詳細