from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class FileInfo:
    path: Path
    content: Optional[str] = None

class FileScanner:
    # スキャン対象の拡張子
    TARGET_EXTENSIONS = {
        '.py', '.js', '.java', '.cpp', '.hpp', '.c', '.h',
        '.go', '.rs', '.php', '.rb', '.ts', '.scala', '.kt',
        '.cs', '.swift', '.m', '.sh', '.pl', '.r'
    }
    
    # スキャン対象から除外するディレクトリ
    EXCLUDED_DIRS = {
        '.git', '__pycache__', 'node_modules', 'venv', '.env',
        'build', 'dist', 'target', 'bin', 'obj'
    }
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    def _should_scan_file(self, path: Path) -> bool:
        if any(excluded in path.parts for excluded in self.EXCLUDED_DIRS):
            return False
        return path.suffix.lower() in self.TARGET_EXTENSIONS
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        try:
            # まずUTF-8で試す
            try:
                with file_path.open('r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                # UTF-8で失敗したらcp932を試す
                with file_path.open('r', encoding='cp932') as f:
                    return f.read()
        except (OSError, UnicodeDecodeError):
            return None
    
    def scan_files(self) -> List[FileInfo]:
        if not self.base_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.base_dir}")
        
        files = []
        
        for entry in self.base_dir.rglob('*'):
            if entry.is_file() and self._should_scan_file(entry):
                content = self._read_file_content(entry)
                if content is not None:
                    files.append(FileInfo(
                        path=entry.relative_to(self.base_dir),
                        content=content
                    ))
        
        return sorted(files, key=lambda x: str(x.path))
