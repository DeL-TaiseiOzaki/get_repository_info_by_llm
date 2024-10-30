from typing import Optional
import openai
from pathlib import Path

class LLMService:
    def __init__(self, api_key: str):
        """
        LLMサービスの初期化
        Args:
            api_key: OpenAI APIキー
        """
        self.api_key = api_key
        openai.api_key = api_key
        
    def create_prompt(self, content: str, query: str) -> str:
        """
        プロンプトを生成
        Args:
            content: コードの内容
            query: ユーザーからの質問
        Returns:
            生成されたプロンプト
        """
        return f"""以下はGitHubリポジトリのコード解析結果です。このコードについて質問に答えてください。

コード解析結果:
{content}

質問: {query}

できるだけ具体的に、コードの内容を参照しながら回答してください。"""

    def get_response(self, content: str, query: str) -> tuple[str, Optional[str]]:
        """
        LLMを使用して回答を生成
        Args:
            content: コードの内容
            query: ユーザーからの質問
        Returns:
            (回答, エラーメッセージ)のタプル
        """
        try:
            prompt = self.create_prompt(content, query)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはコードアナリストとして、リポジトリの解析と質問への回答を行います。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.choices[0].message.content, None
            
        except Exception as e:
            return None, f"エラーが発生しました: {str(e)}"

    @staticmethod
    def format_code_content(files_content: dict) -> str:
        """
        ファイル内容をプロンプト用にフォーマット
        Args:
            files_content: ファイルパスと内容の辞書
        Returns:
            フォーマットされたテキスト
        """
        formatted_content = []
        for file_path, content in files_content.items():
            formatted_content.append(
                f"#ファイルパス\n{file_path}\n------------\n{content}\n"
            )
        return "\n".join(formatted_content)