# APIクライアントの基本的な使い方

## 概要

`EstatApiClient`を使用してe-Stat APIに直接アクセスする方法を説明します。

## 利用シーン

- e-Stat APIの動作確認をしたい場合
- データ構造を確認してから本格的なデータロードを行いたい場合
- 特定の統計データが存在するか確認したい場合
- APIレスポンスの構造を理解したい場合

## 必要な準備

1. e-Stat APIキーの取得
   - [e-Stat API](https://www.e-stat.go.jp/api/)でユーザー登録
   - APIキーを取得

2. 環境変数の設定
   ```bash
   export ESTAT_API_KEY="your-api-key-here"
   ```

## コード例

```python
import os
from estat_api_dlt_helper.api.client import EstatApiClient

def demo_api_client():
    """Demonstrate API client usage"""
    # Get API key from environment
    api_key = os.getenv("ESTAT_API_KEY")

    if not api_key:
        print("Warning: ESTAT_API_KEY not set.")
        print("\nTo test with real API:")
        print("1. Get API key from https://www.e-stat.go.jp/api/")
        print("2. Set environment variable: export ESTAT_API_KEY=your_key_here")
        print("3. Run this script again")
        return

    # Initialize client
    client = EstatApiClient(app_id=api_key)

    try:
        print("Testing e-Stat API client...")

        # Test with a sample statistics data ID
        # This is a real statistics ID for population census data
        stats_data_id = "0000020202"

        print(f"Fetching data for statsDataId: {stats_data_id}")
        print("Requesting first 10 records...")

        # Get small sample of data
        response = client.get_stats_data(
            stats_data_id=stats_data_id, 
            limit=10, 
            start_position=1
        )

        # Display response structure
        print("\nAPI Response Structure:")
        if "GET_STATS_DATA" in response:
            stats_data = response["GET_STATS_DATA"]
            if "STATISTICAL_DATA" in stats_data:
                statistical_data = stats_data["STATISTICAL_DATA"]

                # Show result info
                if "RESULT_INF" in statistical_data:
                    result_inf = statistical_data["RESULT_INF"]
                    print(f"Total records: {result_inf.get('TOTAL_NUMBER', 'N/A')}")
                    print(f"Retrieved: {result_inf.get('FROM_NUMBER', 'N/A')}-{result_inf.get('TO_NUMBER', 'N/A')}")

                # Show table structure
                if "TABLE_INF" in statistical_data:
                    table_inf = statistical_data["TABLE_INF"]
                    if "VALUE" in table_inf and table_inf["VALUE"]:
                        print(f"Sample data records: {len(table_inf['VALUE'])}")
                        print("First record keys:", list(table_inf["VALUE"][0].keys()))

                # Show metadata structure
                if "CLASS_INF" in statistical_data:
                    class_inf = statistical_data["CLASS_INF"]
                    print(f"Metadata classes: {len(class_inf.get('CLASS_OBJ', []))}")

        print("\n✅ API client test successful!")

    except Exception as e:
        print(f"\n❌ API client test failed: {e}")

    finally:
        # Clean up
        client.close()

if __name__ == "__main__":
    demo_api_client()
```

## 実行結果の例

```text
Testing e-Stat API client...
Fetching data for statsDataId: 0000020202
Requesting first 10 records...

API Response Structure:
Total records: 156375
Retrieved: 1-10
Sample data records: 10
First record keys: ['tab', 'cat01', 'cat02', 'cat03', 'area', 'time', 'unit', 'value', 'annotation']
Metadata classes: 6

✅ API client test successful!
```

## 補足情報

- `statsDataId`は統計表を一意に識別するIDです
- `limit`パラメータで取得するレコード数を制限できます
- `start_position`で取得開始位置を指定できます（1から開始）
- APIレスポンスには統計データ本体（`TABLE_INF`）とメタデータ（`CLASS_INF`）が含まれます

## 次のステップ

APIクライアントで動作確認ができたら、[基本的なデータロード](./basic_load_example.md)や[パーサーの使い方](./basic_parser_usage.md)を参照してください。
