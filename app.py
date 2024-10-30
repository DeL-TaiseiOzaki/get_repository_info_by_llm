import streamlit as st
import tempfile
import git
from pathlib import Path
from datetime import datetime
import time
from core.file_scanner import FileScanner
from services.llm_service import LLMService

# ページ設定
st.set_page_config(
    page_title="Repository Code Analysis",
    page_icon="🔍",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    .css-1v0mbdj.ebxwdo61 {
        width: 100%;
        max-width: 800px;
    }
</style>
""", unsafe_allow_html=True)

def clone_repository(repo_url: str) -> Path:
    """リポジトリをクローンして一時ディレクトリに保存"""
    temp_dir = Path(tempfile.mkdtemp())
    git.Repo.clone_from(repo_url, temp_dir)
    return temp_dir

# セッション状態の初期化
if 'repo_content' not in st.session_state:
    st.session_state.repo_content = None
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = None
if 'llm_service' not in st.session_state:
    st.session_state.llm_service = None

# メインのUIレイアウト
st.title("🔍 リポジトリ解析・質問システム")

# OpenAI APIキーの設定
api_key = st.sidebar.text_input("OpenAI APIキー", type="password", key="api_key")
if api_key:
    st.session_state.llm_service = LLMService(api_key)

# URLの入力
repo_url = st.text_input(
    "GitHubリポジトリのURLを入力",
    placeholder="https://github.com/username/repository.git"
)

# スキャン実行ボタン
if st.button("スキャン開始", disabled=not repo_url):
    try:
        with st.spinner('リポジトリをクローン中...'):
            temp_dir = clone_repository(repo_url)
            st.session_state.temp_dir = temp_dir
        
        with st.spinner('ファイルをスキャン中...'):
            scanner = FileScanner(temp_dir)
            files_content = scanner.scan_files()
            
            if st.session_state.llm_service:
                st.session_state.repo_content = LLMService.format_code_content(files_content)
            
        st.success(f"スキャン完了: {len(files_content)}個のファイルを検出")
        
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

# スキャン完了後の質問セクション
if st.session_state.repo_content and st.session_state.llm_service:
    st.divider()
    st.subheader("💭 コードについて質問する")
    
    query = st.text_area(
        "質問を入力してください",
        placeholder="例: このコードの主な機能は何ですか？"
    )
    
    if st.button("質問する", disabled=not query):
        with st.spinner('回答を生成中...'):
            response, error = st.session_state.llm_service.get_response(
                st.session_state.repo_content,
                query
            )
            
            if error:
                st.error(error)
            else:
                st.markdown("### 回答:")
                st.markdown(response)

# セッション終了時のクリーンアップ
if st.session_state.temp_dir and Path(st.session_state.temp_dir).exists():
    try:
        import shutil
        shutil.rmtree(st.session_state.temp_dir)
    except:
        pass

# サイドバー情報
with st.sidebar:
    st.subheader("📌 使い方")
    st.markdown("""
    1. OpenAI APIキーを入力
    2. GitHubリポジトリのURLを入力
    3. スキャンを実行
    4. コードについて質問
    """)
    
    st.subheader("🔍 スキャン対象")
    st.markdown("""
    - Python (.py)
    - JavaScript (.js)
    - Java (.java)
    - C/C++ (.c, .h, .cpp, .hpp)
    - その他の主要なプログラミング言語
    """)