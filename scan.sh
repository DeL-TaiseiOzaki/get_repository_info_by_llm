#!/bin/bash

# エラーが発生した場合に停止
set -e

# デフォルトのターゲットパスを設定
# ここを変更することで対象を変更できます
TARGET_PATH="https://github.com/DeL-TaiseiOzaki/idebate_scraping.git"  # 例: Linuxカーネル
# TARGET_PATH="/path/to/your/directory"  # ローカルディレクトリの例

# 必要なディレクトリの存在確認
if [ ! -d "output" ]; then
    mkdir output
fi

# Pythonの存在確認
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# GitHubリポジトリの場合、Gitの存在確認
if [[ $TARGET_PATH == http* ]] && [[ $TARGET_PATH == *github.com* ]]; then
    if ! command -v git &> /dev/null; then
        echo "Error: Git is not installed"
        exit 1
    fi
    echo "Scanning GitHub repository: $TARGET_PATH"
else
    if [ ! -d "$TARGET_PATH" ]; then
        echo "Error: Directory not found: $TARGET_PATH"
        exit 1
    fi
    echo "Scanning local directory: $TARGET_PATH"
fi

# スキャンの実行
echo "Starting directory scan..."
python3 main.py "$TARGET_PATH"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "Scan completed successfully!"
    echo "Results are saved in the 'output' directory"
else
    echo "Scan failed with exit code: $exit_code"
    exit $exit_code
fi