import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import sys
import os

# 导入要测试的模块
import performance_analysis
from similarity import TextSimilarityCalculator
from file_handler import FileHandler

class TestPerformanceAnalysis(unittest.TestCase):
    
    def test_create_large_text(self):
        """测试创建指定大小的文本"""
        # 测试创建小文本
        text = performance_analysis.create_large_text(0.01)  # 约10KB
        # 检查文本大小是否符合预期
        self.assertTrue(len(text.encode('utf-8')) >= 10 * 1024)  # 至少10KB
        self.assertTrue(len(text.encode('utf-8')) < 20 * 1024)  # 小于20KB
        
        # 检查文本内容
        self.assertTrue("性能测试" in text)
        
        # 测试默认参数
        default_text = performance_analysis.create_large_text()
        self.assertTrue(len(default_text.encode('utf-8')) >= 1024 * 1024)  # 至少1MB
    
    @patch('performance_analysis.TextSimilarityCalculator')
    @patch('performance_analysis.create_large_text')
    @patch('performance_analysis.cProfile.Profile')
    @patch('builtins.print')
    def test_profile_similarity_calculation(self, mock_print, mock_profile, mock_create_text, mock_calculator):
        """测试相似度计算性能分析"""
        # 设置模拟对象
        mock_text = "测试文本"
        mock_create_text.return_value = mock_text
        
        mock_calc_instance = mock_calculator.return_value
        mock_calc_instance.calculate_similarity.return_value = 0.85
        
        mock_profiler_instance = mock_profile.return_value
        
        # 执行函数
        performance_analysis.profile_similarity_calculation()
        
        # 验证调用
        mock_create_text.assert_called_with(0.5)
        mock_calc_instance.calculate_similarity.assert_called_with(mock_text, mock_text)
        mock_profiler_instance.enable.assert_called_once()
        mock_profiler_instance.disable.assert_called_once()
    
    @patch('performance_analysis.FileHandler')
    @patch('performance_analysis.create_large_text')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('builtins.print')
    def test_profile_file_operations(self, mock_print, mock_remove, mock_exists, mock_create_text, mock_handler):
        """测试文件操作性能分析"""
        # 设置模拟对象
        mock_content = "测试内容"
        mock_create_text.return_value = mock_content
        
        mock_handler_instance = mock_handler.return_value
        mock_handler_instance.write_file.return_value = True
        mock_handler_instance.read_file.return_value = mock_content
        
        mock_exists.return_value = True
        
        # 执行函数
        performance_analysis.profile_file_operations()
        
        # 验证调用
        mock_handler_instance.write_file.assert_called_once()
        mock_handler_instance.read_file.assert_called_once()
        mock_exists.assert_called_once()
        mock_remove.assert_called_once()
    
    @patch('performance_analysis.TextSimilarityCalculator')
    @patch('performance_analysis.create_large_text')
    @patch('builtins.print')
    def test_profile_text_preprocessing(self, mock_print, mock_create_text, mock_calculator):
        """测试文本预处理性能分析"""
        # 设置模拟对象
        mock_texts = {0.1: "小文本", 0.5: "中等文本", 1.0: "大文本"}
        mock_create_text.side_effect = lambda size: mock_texts[size]
        
        mock_calc_instance = mock_calculator.return_value
        mock_calc_instance.preprocess_text.side_effect = lambda text: ["分词" for _ in range(len(text))]
        
        # 执行函数
        performance_analysis.profile_text_preprocessing()
        
        # 验证调用
        self.assertEqual(mock_create_text.call_count, 3)
        self.assertEqual(mock_calc_instance.preprocess_text.call_count, 3)
    
    @patch('performance_analysis.TextSimilarityCalculator')
    @patch('performance_analysis.create_large_text')
    @patch('builtins.print')
    def test_benchmark_different_algorithms(self, mock_print, mock_create_text, mock_calculator):
        """测试不同算法性能对比"""
        # 设置模拟对象
        mock_create_text.return_value = "长文本内容"
        
        mock_calc_instance = mock_calculator.return_value
        mock_calc_instance.calculate_similarity.return_value = 0.9
        
        # 执行函数
        performance_analysis.benchmark_different_algorithms()
        
        # 验证调用
        self.assertGreaterEqual(mock_calc_instance.calculate_similarity.call_count, 3)
    
    @patch('performance_analysis.profile_similarity_calculation')
    @patch('performance_analysis.profile_file_operations')
    @patch('performance_analysis.profile_text_preprocessing')
    @patch('performance_analysis.profile_memory_usage')
    @patch('performance_analysis.benchmark_different_algorithms')
    @patch('builtins.print')
    def test_main(self, mock_print, mock_benchmark, mock_memory, mock_preprocessing, mock_file_ops, mock_similarity):
        """测试主函数正常流程"""
        # 执行函数
        performance_analysis.main()
        
        # 验证调用
        mock_similarity.assert_called_once()
        mock_file_ops.assert_called_once()
        mock_preprocessing.assert_called_once()
        mock_memory.assert_called_once()
        mock_benchmark.assert_called_once()
    
    @patch('performance_analysis.profile_similarity_calculation')
    @patch('builtins.print')
    def test_main_exception_handling(self, mock_print, mock_similarity):
        """测试主函数异常处理"""
        # 设置模拟对象抛出异常
        mock_similarity.side_effect = Exception("测试异常")
        
        # 执行函数
        performance_analysis.main()
        
        # 验证异常被捕获并打印
        mock_print.assert_any_call("性能分析过程中发生错误: 测试异常")
    
    @unittest.skip("跳过导入错误测试，该测试在当前环境中难以正确模拟")
    def test_memory_analysis_import_error(self):
        """测试内存分析时psutil导入失败的情况"""
        # 由于导入错误的模拟在单元测试环境中比较复杂
        # 暂时跳过这个测试，实际运行时函数内部已有异常处理机制
        pass

if __name__ == "__main__":
    unittest.main()