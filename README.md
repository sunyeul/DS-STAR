# DS-Star

データサイエンスタスクを自動化するマルチエージェントシステム。Google ADK (Agent Development Kit) を使用して構築されており、データ分析から質問応答までを自律的に実行します。

## 概要

DS-Star は、複数の専門エージェントが連携してデータサイエンスタスクを処理するシステムです。データファイルの分析、計画立案、コード生成、検証、最終的な回答生成までを自動化します。

## アーキテクチャ

本システムは以下の6つの専門エージェントで構成されています：

### エージェント構成

1. **Analyzer Agent** (`analyzer_agent`)
   - データファイルの内容を分析し、構造や特徴を把握
   - データを読み込み、記述するためのPythonコードを生成

2. **Planner Agent** (`planner_agent`)
   - 初期計画と後続ステップの計画を動的に立案
   - 質問に答えるための戦略を策定

3. **Coder Agent** (`coder_agent`)
   - 計画に基づいて実行可能なPythonコードを生成
   - データ分析や処理のためのコードを作成

4. **Verifier Agent** (`verifier_agent`)
   - 生成されたコードの検証を実施
   - エラーの有無や実行可能性を確認

5. **Router Agent** (`router_agent`)
   - 計画が不十分な場合に、次のステップを決定
   - 計画の改善方法を提案

6. **Finalyzer Agent** (`finalyzer_agent`)
   - 最終的な回答を生成・統合
   - 分析結果をまとめて出力

### ワークフロー

```text
データファイル分析 (Analyzer Agent)
    ↓
初期計画立案 (Planner Agent)
    ↓
コード生成 (Coder Agent)
    ↓
ループ処理 (LoopAgent: Verifier → Router → Planner → Coder)
    ↓
最終回答生成 (Finalyzer Agent)
```

ループ処理は最大5回まで反復され、計画とコードを改善しながら質問への回答を生成します。

## 要件

- Python >= 3.13
- Google ADK >= 1.19.0
- pandas >= 2.3.3
- scipy >= 1.16.3
- tabulate >= 0.9.0

## インストール

```bash
# プロジェクトのクローン
git clone <repository-url>
cd ds_star

# 依存関係のインストール（uvを使用）
uv sync
```

## 使用方法

### データの配置

分析対象のデータファイルを `data/` ディレクトリに配置してください。

```bash
# 例: CSVファイルを配置
cp your_data.csv data/
```

### エージェントの実行

```python
from ds_star import root_agent

# エージェントの実行
# （実行方法はGoogle ADKの使用方法に従います）
```

## プロジェクト構造

```text
ds_star/
├── config/
│   └── config.py          # パス設定
├── data/                   # データファイル格納ディレクトリ
│   └── yulu_bike_sharing_dataset.csv
├── ds_star/
│   ├── agent.py           # メインエージェント
│   └── sub_agent/
│       ├── analyzer_agent/    # データ分析エージェント
│       ├── planner_agent/     # 計画立案エージェント
│       ├── coder_agent/       # コード生成エージェント
│       ├── verifier_agent/    # 検証エージェント
│       ├── router_agent/      # ルーティングエージェント
│       └── finalyzer_agent/   # 最終化エージェント
├── pyproject.toml         # プロジェクト設定
└── README.md
```

## 開発

開発用の依存関係をインストールする場合：

```bash
uv sync --group dev
```

開発ツール：

- `ruff`: コードフォーマッター・リンター
- `ipykernel`: Jupyter Notebook サポート

## ライセンス

[ライセンス情報を追加]

## 貢献

[貢献ガイドラインを追加]
