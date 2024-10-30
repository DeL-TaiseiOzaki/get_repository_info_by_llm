# Repository Code Analyzer

GitHubリポジトリやローカルディレクトリのコードを解析し、Claude AIを使って対話的にコードの理解を深めるためのツールです。

## 機能

- GitHubリポジトリのクローンと解析
- ローカルディレクトリの解析
- 指定した拡張子のファイル抽出
- コード内容のテキスト抽出とダウンロード
- Claude AIを使ったコードについての対話
- Streamlit Web UI
- Hugging Face Spaces対応

## 必要条件

- Python 3.8以上
- Anthropic API Key

## インストール

```bash
git clone <your-repository-url>
cd repository-code-analyzer
pip install -r requirements.txt
```

## 環境変数の設定

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## 使用方法

### Webインターフェース

```bash
streamlit run app.py
```

1. サイドバーでスキャン対象の拡張子を選択
2. GitHubリポジトリのURLを入力
3. スキャンを実行
4. コードについて質問（最大5ターン）

### コマンドライン

```bash
# GitHubリポジトリの解析
./scan.sh https://github.com/username/repository.git

# ローカルディレクトリの解析
./scan.sh /path/to/local/directory
```

## スキャン対象ファイル

- プログラミング言語: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.hpp`, `.c`, `.h`, `.go`, `.rs`
- 設定ファイル: `.json`, `.yml`, `.yaml`, `.toml`
- ドキュメント: `.md`, `.txt`

## Hugging Face Spacesへのデプロイ

1. リポジトリをHugging Face Spacesに接続
2. 環境変数`ANTHROPIC_API_KEY`を設定
3. 依存関係が記述された`requirements.txt`を配置
4. Streamlitアプリとして自動デプロイ
