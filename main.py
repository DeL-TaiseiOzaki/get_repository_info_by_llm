import sys
from pathlib import Path
from config.settings import Settings
from core.git_manager import GitManager
from core.file_scanner import FileScanner
from utils.file_writer import FileWriter

def main():
    # コマンドライン引数からパスを取得
    if len(sys.argv) != 2:
        print("Usage: python main.py <github_url or directory_path>")
        return 1
    
    target_path = sys.argv[1]
    timestamp = Settings.get_timestamp()
    output_file = Settings.get_output_file(timestamp)
    
    # GitHubのURLかローカルパスかを判定
    is_github = target_path.startswith(('http://', 'https://')) and 'github.com' in target_path
    
    try:
        if is_github:
            # GitHubリポジトリの場合
            clone_dir = Settings.get_clone_dir(timestamp)
            print(f"Cloning repository: {target_path}")
            
            git_manager = GitManager(target_path, clone_dir)
            git_manager.clone_repository()
            
            scanner = FileScanner(clone_dir)
            cleanup_needed = True
        else:
            # ローカルディレクトリの場合
            target_dir = Path(target_path)
            if not target_dir.exists():
                print(f"Error: Directory not found: {target_dir}")
                return 1
                
            scanner = FileScanner(target_dir)
            cleanup_needed = False
        
        # ファイルスキャンと保存
        print("Scanning files...")
        files = scanner.scan_files()
        
        print(f"Writing contents to {output_file}")
        writer = FileWriter(output_file)
        writer.write_contents(files)
        
        print(f"Found {len(files)} files")
        print(f"Results saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    finally:
        # GitHubリポジトリの場合はクリーンアップ
        if is_github and cleanup_needed and 'git_manager' in locals():
            try:
                git_manager.cleanup()
                print("Cleanup completed")
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    return 0

if __name__ == "__main__":
    exit(main())