import streamlit as st
import tempfile
import git
import os
from pathlib import Path
from datetime import datetime 
from config.settings import Settings
from core.file_scanner import FileScanner, FileInfo
from services.llm_service import LLMService
from typing import List, Set

st.set_page_config(
   page_title="Repository Code Analysis",
   page_icon="🔍",
   layout="wide"
)

# ダークテーマの設定
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .chat-message {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .assistant-message {
        background-color: #1e2329;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

def create_download_content(files: List[FileInfo]) -> str:
    content = "# スキャン結果\n\n"
    for file in files:
        content += f"## {file.path}\n"
        content += f"サイズ: {file.formatted_size}\n"
        content += f"エンコーディング: {file.encoding or '不明'}\n\n"
        if file.content:
            content += f"```{file.extension[1:] if file.extension else ''}\n"
            content += file.content
            content += "\n```\n\n"
    return content

def clone_repository(repo_url: str) -> Path:
    temp_dir = Path(tempfile.mkdtemp())
    git.Repo.clone_from(repo_url, temp_dir)
    return temp_dir

# セッション状態の初期化
if 'repo_content' not in st.session_state:
    st.session_state.repo_content = None
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = None
if 'llm_service' not in st.session_state:
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("ANTHROPIC_API_KEY環境変数が設定されていません")
            st.stop()
        st.session_state.llm_service = LLMService(api_key)
    except Exception as e:
        st.error(str(e))
        st.stop()

# メインのUIレイアウト
st.title("🔍 リポジトリ解析・質問システム")

# サイドバーの設定
with st.sidebar:
    st.subheader("📌 使い方")
    st.markdown("""
    1. スキャン対象の拡張子を選択
    2. GitHubリポジトリのURLを入力
    3. スキャンを実行
    4. コードについて質問（最大5ターンの会話が可能）
    """)
    
    # スキャン対象の拡張子選択
    st.subheader("🔍 スキャン対象の選択")
    
    # 拡張子をカテゴリごとに表示
    st.write("プログラミング言語:")
    prog_exts = {'.py', '.js', '.ts', '.java', '.cpp', '.hpp', '.c', '.h', '.go', '.rs'}
    selected_prog = {ext: st.checkbox(ext, value=True, key=f"prog_{ext}") 
                    for ext in prog_exts}
    
    st.write("設定ファイル:")
    config_exts = {'.json', '.yml', '.yaml', '.toml'}
    selected_config = {ext: st.checkbox(ext, value=True, key=f"config_{ext}") 
                      for ext in config_exts}
    
    st.write("ドキュメント:")
    doc_exts = {'.md', '.txt'}
    selected_doc = {ext: st.checkbox(ext, value=True, key=f"doc_{ext}") 
                   for ext in doc_exts}
    
    # 選択された拡張子の集合を作成
    selected_extensions = {ext for exts in [selected_prog, selected_config, selected_doc]
                         for ext, selected in exts.items() if selected}

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
            scanner = FileScanner(temp_dir, selected_extensions)
            files = scanner.scan_files()
            st.session_state.repo_content = LLMService.format_code_content(files)
            
        st.success(f"スキャン完了: {len(files)}個のファイルを検出")
        
        # スキャン結果のダウンロードボタン
        scan_result = create_download_content(files)
        st.download_button(
            label="スキャン結果をダウンロード",
            data=scan_result,
            file_name=f"scan_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
        
        # 新しいスキャン時に会話履歴をクリア
        st.session_state.llm_service.clear_history()
        
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

# スキャン完了後の質問セクション
if st.session_state.repo_content:
    st.divider()
    st.subheader("💭 コードについて質問する")
    
    # 会話履歴の表示
    for message in st.session_state.llm_service.conversation_history:
        if message.role == "assistant":
            st.markdown(f'<div class="chat-message assistant-message">{message.content}</div>', 
                       unsafe_allow_html=True)
    
    query = st.text_area(
        "質問を入力してください",
        placeholder="例: このコードの主な機能は何ですか？"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("履歴クリア"):
            st.session_state.llm_service.clear_history()
            st.rerun()
    
    with col2:
        if st.button("質問する", disabled=not query):
            with st.spinner('回答を生成中...'):
                response, error = st.session_state.llm_service.get_response(
                    st.session_state.repo_content,
                    query
                )
                
                if error:
                    st.error(error)
                else:
                    st.rerun()

# セッション終了時のクリーンアップ
if st.session_state.temp_dir and Path(st.session_state.temp_dir).exists():
    try:
        import shutil
        shutil.rmtree(st.session_state.temp_dir)
    except:
        pass