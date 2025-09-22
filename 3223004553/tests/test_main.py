# -*- coding: utf-8 -*-
"""
主程序模块的单元测试
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import validate_arguments, calculate_plagiarism_rate, print_usage


class TestMain(unittest.TestCase):
    """主程序测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.test_dir = tempfile.mkdtemp()
        self.original_file = os.path.join(self.test_dir, "original.txt")
        self.plagiarized_file = os.path.join(self.test_dir, "plagiarized.txt")
        self.output_file = os.path.join(self.test_dir, "output.txt")
        
        # 创建测试文件
        with open(self.original_file, 'w', encoding='utf-8') as f:
            f.write("今天是星期天，天气晴，今天晚上我要去看电影。")
        
        with open(self.plagiarized_file, 'w', encoding='utf-8') as f:
            f.write("今天是周天，天气晴朗，我晚上要去看电影。")
    
    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_validate_arguments_correct(self):
        """测试正确的参数验证"""
        args = ["main.py", self.original_file, self.plagiarized_file, self.output_file]
        result = validate_arguments(args)
        self.assertTrue(result)
    
    def test_validate_arguments_incorrect_count(self):
        """测试参数数量不正确"""
        args = ["main.py", self.original_file, self.plagiarized_file]
        result = validate_arguments(args)
        self.assertFalse(result)
        
        args = ["main.py", self.original_file]
        result = validate_arguments(args)
        self.assertFalse(result)
    
    def test_validate_arguments_nonexistent_file(self):
        """测试不存在的文件"""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        args = ["main.py", nonexistent_file, self.plagiarized_file, self.output_file]
        result = validate_arguments(args)
        self.assertFalse(result)
    
    def test_validate_arguments_empty_path(self):
        """测试空路径"""
        args = ["main.py", "", self.plagiarized_file, self.output_file]
        result = validate_arguments(args)
        self.assertFalse(result)
    
    @patch('main.read_text_file')
    @patch('main.calculate_text_similarity')
    @patch('main.write_text_file')
    def test_calculate_plagiarism_rate_success(self, mock_write, mock_calculate, mock_read):
        """测试成功计算重复率"""
        # 设置模拟返回值
        mock_read.side_effect = ["原文内容", "抄袭版内容"]
        mock_calculate.return_value = 0.85
        mock_write.return_value = True
        
        result = calculate_plagiarism_rate(
            self.original_file, 
            self.plagiarized_file, 
            self.output_file
        )
        
        self.assertTrue(result)
        mock_read.assert_called()
        mock_calculate.assert_called_once_with("原文内容", "抄袭版内容")
        mock_write.assert_called_once_with(self.output_file, "0.85")
    
    @patch('main.read_text_file')
    def test_calculate_plagiarism_rate_read_failure(self, mock_read):
        """测试读取文件失败"""
        mock_read.return_value = None
        
        result = calculate_plagiarism_rate(
            self.original_file, 
            self.plagiarized_file, 
            self.output_file
        )
        
        self.assertFalse(result)
    
    @patch('main.read_text_file')
    def test_calculate_plagiarism_rate_empty_original(self, mock_read):
        """测试原文为空"""
        mock_read.side_effect = ["", "抄袭版内容"]
        
        result = calculate_plagiarism_rate(
            self.original_file, 
            self.plagiarized_file, 
            self.output_file
        )
        
        self.assertFalse(result)
    
    @patch('main.read_text_file')
    def test_calculate_plagiarism_rate_empty_plagiarized(self, mock_read):
        """测试抄袭版为空"""
        mock_read.side_effect = ["原文内容", ""]
        
        result = calculate_plagiarism_rate(
            self.original_file, 
            self.plagiarized_file, 
            self.output_file
        )
        
        self.assertFalse(result)
    
    @patch('main.read_text_file')
    @patch('main.calculate_text_similarity')
    @patch('main.write_text_file')
    def test_calculate_plagiarism_rate_write_failure(self, mock_write, mock_calculate, mock_read):
        """测试写入文件失败"""
        mock_read.side_effect = ["原文内容", "抄袭版内容"]
        mock_calculate.return_value = 0.85
        mock_write.return_value = False
        
        result = calculate_plagiarism_rate(
            self.original_file, 
            self.plagiarized_file, 
            self.output_file
        )
        
        self.assertFalse(result)
    
    def test_print_usage(self):
        """测试打印使用说明"""
        with patch('builtins.print') as mock_print:
            print_usage()
            mock_print.assert_called()
    
    def test_calculate_plagiarism_rate_real_files(self):
        """测试使用真实文件计算重复率"""
        result = calculate_plagiarism_rate(
            self.original_file, 
            self.plagiarized_file, 
            self.output_file
        )
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_file))
        
        # 验证输出文件内容
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # 相似度应该是0-1之间的数字
        similarity = float(content)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
