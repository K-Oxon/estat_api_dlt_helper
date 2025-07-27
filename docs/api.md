# APIリファレンス

## メイン設定クラス

### EstatDltConfig

e-Stat APIからdltへのデータ統合のメイン設定クラスです。ソースとロード先の設定を組み合わせ、データ抽出とロードのための追加処理オプションを提供します。

::: estat_api_dlt_helper.EstatDltConfig

### SourceConfig

e-Stat APIデータソースの設定クラスです。認証、取得する統計表選択、各種オプションを含む統計データの取得パラメータを定義します。

パラメータの詳細は[e_Stat API 仕様](https://api.e-stat.go.jp/swagger-ui/e-statapi3.0.html#/)を参照のこと。

::: estat_api_dlt_helper.SourceConfig

### DestinationConfig

dlt destination (データロード先) の設定クラスです。ロード先のDWH、データセット/テーブル名、書き込み戦略を含むdltの設定を定義します。

::: estat_api_dlt_helper.DestinationConfig

## APIクライアント

### EstatApiClient

e-Stat APIアクセス用のクライアントクラスです。政府統計のe-Stat API機能から統計データを取得するメソッドを提供し、API認証、リクエストフォーマット、レスポンス解析を処理します。

::: estat_api_dlt_helper.EstatApiClient

## データ解析

### parse_response

e-Stat APIレスポンスを解析してArrow形式に変換する関数です。JSONレスポンスを受け取り、データ値と関連メタデータを含む構造化されたArrowテーブルを返します。

::: estat_api_dlt_helper.parse_response

## データローダー関数

### load_estat_data

e-Stat APIデータを指定されたデスティネーションにロードする便利な関数です。提供された設定でdltパイプラインを作成して実行します。

::: estat_api_dlt_helper.load_estat_data

### create_estat_resource

e-Stat APIデータ用のdltリソースを作成する関数です。設定に基づいてe-Stat APIからデータを取得するカスタマイズ可能なdltリソースを作成します。

::: estat_api_dlt_helper.create_estat_resource

### create_estat_pipeline

e-Stat APIデータロード用のdltパイプラインを作成する関数です。提供された設定に基づいて指定されたデスティネーション用に構成されたカスタマイズ可能なdltパイプラインを作成します。

::: estat_api_dlt_helper.create_estat_pipeline
