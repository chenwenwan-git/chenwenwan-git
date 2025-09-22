# -*- coding: utf-8 -*-
"""
文件处理模块的单元测试
"""

import unittest
import sys
import os
import tempfile
import shutil

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_handler import FileHandler, read_text_file, write_text_file


class TestFileHandler(unittest.TestCase):
    """文件处理器测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.handler = FileHandler()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
    
    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_read_existing_file(self):
        """测试读取存在的文件"""
        # 创建测试文件
        test_content = "这是一个测试文件。"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 读取文件
        content = self.handler.read_file(self.test_file)
        self.assertEqual(content, test_content)
    
    def test_read_nonexistent_file(self):
        """测试读取不存在的文件"""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        with self.assertRaises(FileNotFoundError):
            self.handler.read_file(nonexistent_file)
    
    def test_write_file(self):
        """测试写入文件"""
        test_content = "这是写入的测试内容。"
        success = self.handler.write_file(self.test_file, test_content)
        self.assertTrue(success)
        
        # 验证文件内容
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, test_content)
    
    def test_write_to_nonexistent_directory(self):
        """测试写入到不存在的目录"""
        test_dir = os.path.join(self.test_dir, "subdir")
        test_file = os.path.join(test_dir, "test.txt")
        test_content = "测试内容"
        
        success = self.handler.write_file(test_file, test_content)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_file))
    
    def test_validate_file_path(self):
        """测试文件路径验证"""
        # 有效路径
        valid_paths = [
            "test.txt",
            "C:\\test\\file.txt",
            "/home/user/file.txt",
            "相对路径/文件.txt"
        ]
        for path in valid_paths:
            self.assertTrue(self.handler.validate_file_path(path))
        
        # 无效路径
        invalid_paths = [
            "",
            None,
            "test<>file.txt",
            "test:file.txt",
            "test|file.txt"
        ]
        for path in invalid_paths:
            if path is not None:
                self.assertFalse(self.handler.validate_file_path(path))
    
    def test_get_file_size(self):
        """测试获取文件大小"""
        # 测试不存在的文件
        size = self.handler.get_file_size("nonexistent.txt")
        self.assertEqual(size, -1)
        
        # 测试存在的文件
        test_content = "测试内容"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        size = self.handler.get_file_size(self.test_file)
        self.assertGreater(size, 0)
    
    def test_read_file_with_different_encodings(self):
        """测试读取不同编码的文件"""
        # 测试UTF-8编码
        utf8_file = os.path.join(self.test_dir, "utf8.txt")
        test_content = "这是UTF-8编码的测试文件。"
        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        content = self.handler.read_file(utf8_file)
        self.assertEqual(content, test_content)
        
        # 测试GBK编码
        gbk_file = os.path.join(self.test_dir, "gbk.txt")
        with open(gbk_file, 'w', encoding='gbk') as f:
            f.write(test_content)
        
        content = self.handler.read_file(gbk_file)
        self.assertEqual(content, test_content)
    
    def test_read_empty_file(self):
        """测试读取空文件"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        content = self.handler.read_file(self.test_file)
        self.assertEqual(content, "")
    
    def test_write_empty_content(self):
        """测试写入空内容"""
        success = self.handler.write_file(self.test_file, "")
        self.assertTrue(success)
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, "")


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
    
    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_read_text_file_function(self):
        """测试read_text_file便捷函数"""
        test_content = "便捷函数测试内容。"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        content = read_text_file(self.test_file)
        self.assertEqual(content, test_content)
        
        # 测试不存在的文件
        content = read_text_file("nonexistent.txt")
        self.assertIsNone(content)
    
    def test_write_text_file_function(self):
        """测试write_text_file便捷函数"""
        test_content = "便捷函数写入测试。"
        success = write_text_file(self.test_file, test_content)
        self.assertTrue(success)
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, test_content)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
