# -*- coding: utf-8 -*-
"""
论文查重系统 - 文件处理模块
负责文件的读取和写入操作
"""

import os
import sys
from typing import Optional


class FileHandler:
    """文件处理器"""
    
    def __init__(self):
        """初始化文件处理器"""
        self.supported_encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
    
    def read_file(self, file_path: str) -> Optional[str]:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串，如果读取失败返回None
            
        Raises:
            FileNotFoundError: 文件不存在
            PermissionError: 权限不足
            UnicodeDecodeError: 编码错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"没有读取权限: {file_path}")
        
        # 尝试不同的编码方式读取文件
        for encoding in self.supported_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read().strip()
                    return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise Exception(f"读取文件时发生错误: {e}")
        
        # 如果所有编码都失败，抛出异常
        raise UnicodeDecodeError("无法使用支持的编码格式读取文件")
    
    def write_file(self, file_path: str, content: str) -> bool:
        """
        写入文件内容
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            
        Returns:
            写入成功返回True，失败返回False
            
        Raises:
            PermissionError: 权限不足
            OSError: 文件系统错误
        """
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # 检查写入权限
            if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
                raise PermissionError(f"没有写入权限: {file_path}")
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            return True
            
        except Exception as e:
            print(f"写入文件时发生错误: {e}")
            return False
    
    def validate_file_path(self, file_path: str) -> bool:
        """
        验证文件路径是否有效
        
        Args:
            file_path: 文件路径
            
        Returns:
            路径有效返回True，否则返回False
        """
        if not file_path or not isinstance(file_path, str):
            return False
        
        # 检查路径长度
        if len(file_path) > 260:  # Windows路径长度限制
            return False
        
        # 检查是否包含非法字符
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in file_path for char in illegal_chars):
            return False
        
        return True
    
    def get_file_size(self, file_path: str) -> int:
        """
        获取文件大小（字节）
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小，如果文件不存在返回-1
        """
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return -1
        except Exception:
            return -1


def read_text_file(file_path: str) -> Optional[str]:
    """
    便捷函数：读取文本文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容，读取失败返回None
    """
    handler = FileHandler()
    try:
        return handler.read_file(file_path)
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None


def write_text_file(file_path: str, content: str) -> bool:
    """
    便捷函数：写入文本文件
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        
    Returns:
        写入成功返回True，失败返回False
    """
    handler = FileHandler()
    return handler.write_file(file_path, content)


if __name__ == "__main__":
    # 测试代码
    handler = FileHandler()
    
    # 测试文件路径验证
    test_paths = [
        "test.txt",
        "C:\\test\\file.txt",
        "",
        "test<>file.txt"
    ]
    
    for path in test_paths:
        is_valid = handler.validate_file_path(path)
        print(f"路径 '{path}' 是否有效: {is_valid}")
