import os
from typing import Dict, List, Optional
from datetime import datetime
import git
from pathlib import Path
import difflib
from dataclasses import dataclass
from ..config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

@dataclass
class CodeChange:
    file_path: str
    old_content: str
    new_content: str
    timestamp: datetime
    author: str
    commit_message: str

class CodeVersion(Base):
    __tablename__ = 'code_versions'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    commit_hash = Column(String, nullable=True)
    author = Column(String, nullable=False)
    commit_message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CodeEditor:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        
    def get_file_content(self, file_path: str) -> Dict:
        """Get file content with metadata"""
        abs_path = os.path.join(self.repo_path, file_path)
        if not os.path.exists(abs_path):
            raise ValueError(f"File not found: {file_path}")
            
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_type = self._get_file_type(file_path)
        
        return {
            'content': content,
            'file_type': file_type,
            'last_modified': datetime.fromtimestamp(os.path.getmtime(abs_path)),
            'size': os.path.getsize(abs_path)
        }
    
    def update_file(self, file_path: str, new_content: str, author: str, commit_message: str) -> Dict:
        """Update file content with version control"""
        abs_path = os.path.join(self.repo_path, file_path)
        
        # Backup current content
        old_content = ""
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
        
        # Write new content
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Create git commit
        self.repo.index.add([file_path])
        commit = self.repo.index.commit(commit_message)
        
        # Record change
        change = CodeChange(
            file_path=file_path,
            old_content=old_content,
            new_content=new_content,
            timestamp=datetime.utcnow(),
            author=author,
            commit_message=commit_message
        )
        
        return {
            'status': 'success',
            'commit_hash': commit.hexsha,
            'diff': self._generate_diff(old_content, new_content)
        }
    
    def rollback_changes(self, file_path: str, commit_hash: str) -> Dict:
        """Rollback file to specific version"""
        try:
            # Checkout specific version
            self.repo.git.checkout(commit_hash, '--', file_path)
            
            # Create new commit for rollback
            self.repo.index.add([file_path])
            commit = self.repo.index.commit(f"Rollback {file_path} to {commit_hash}")
            
            return {
                'status': 'success',
                'commit_hash': commit.hexsha
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_file_history(self, file_path: str) -> List[Dict]:
        """Get file version history"""
        history = []
        for commit in self.repo.iter_commits(paths=file_path):
            history.append({
                'commit_hash': commit.hexsha,
                'author': commit.author.name,
                'message': commit.message,
                'timestamp': commit.committed_datetime
            })
        return history
    
    def preview_changes(self, file_path: str, new_content: str) -> Dict:
        """Preview changes without saving"""
        abs_path = os.path.join(self.repo_path, file_path)
        
        if not os.path.exists(abs_path):
            return {'error': 'File not found'}
            
        with open(abs_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
            
        return {
            'diff': self._generate_diff(old_content, new_content),
            'syntax_check': self._check_syntax(file_path, new_content)
        }
    
    def _generate_diff(self, old_content: str, new_content: str) -> List[str]:
        """Generate readable diff between contents"""
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True)
        )
        return list(diff)
    
    def _check_syntax(self, file_path: str, content: str) -> Dict:
        """Check syntax based on file type"""
        file_type = self._get_file_type(file_path)
        errors = []
        
        try:
            if file_type == 'python':
                compile(content, file_path, 'exec')
            # Add syntax checking for other file types
            
        except Exception as e:
            errors.append(str(e))
            
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type based on extension"""
        ext = Path(file_path).suffix.lower()
        return {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json'
        }.get(ext, 'text')
