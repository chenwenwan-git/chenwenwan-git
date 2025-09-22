import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import logging
import subprocess

# 导入要测试的模块
import run_tests

class TestRunTests(unittest.TestCase):
    
    def test_setup_logger(self):
        """测试日志配置功能"""
        # 清除已有的handlers，确保测试环境干净
        logger = logging.getLogger('plagiarism_checker')
        logger.handlers = []
        
        # 测试logger创建
        new_logger = run_tests.setup_logger()
        self.assertIsNotNone(new_logger)
        self.assertEqual(new_logger.name, 'plagiarism_checker')
        self.assertEqual(new_logger.level, logging.INFO)
        
        # 测试不重复添加handler
        handlers_before = len(new_logger.handlers)
        run_tests.setup_logger()
        handlers_after = len(new_logger.handlers)
        self.assertEqual(handlers_before, handlers_after)
        
        # 清理
        logger.handlers = []
    
    @patch('run_tests.subprocess.run')
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_run_unit_tests_success(self, mock_print, mock_logger, mock_subprocess_run):
        """测试成功运行单元测试"""
        # 设置模拟对象
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result
        
        # 执行函数
        run_tests.run_unit_tests()
        
        # 验证调用
        self.assertEqual(mock_subprocess_run.call_count, 3)  # 应该运行3个测试文件
        mock_logger.info.assert_any_call("开始运行单元测试")
        mock_logger.info.assert_any_call("单元测试运行完成")
    
    @patch('run_tests.subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=["python"], timeout=60))
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_run_unit_tests_timeout(self, mock_print, mock_logger, mock_subprocess_run):
        """测试单元测试超时处理"""
        # 执行函数
        run_tests.run_unit_tests()
        
        # 验证超时被正确处理
        mock_logger.error.assert_any_call(f"测试 tests/test_similarity.py 超时")
        mock_print.assert_any_call("❌ 测试超时 (超过60秒)")
    
    @patch('run_tests.subprocess.run')
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_run_unit_tests_failure(self, mock_print, mock_logger, mock_subprocess_run):
        """测试单元测试失败处理"""
        # 设置模拟对象返回失败
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "测试输出"
        mock_result.stderr = "测试错误"
        mock_subprocess_run.return_value = mock_result
        
        # 执行函数
        run_tests.run_unit_tests()
        
        # 验证失败被正确处理
        mock_logger.error.assert_any_call(f"测试 tests/test_similarity.py 失败: 测试错误")
        mock_print.assert_any_call("❌ 测试失败")
    
    @patch('run_tests.subprocess.run')
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_run_coverage_test_success(self, mock_print, mock_logger, mock_subprocess_run):
        """测试成功运行覆盖率测试"""
        # 设置模拟对象
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "覆盖率测试输出"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # 执行函数
        run_tests.run_coverage_test()
        
        # 验证调用
        mock_subprocess_run.assert_called_once()
        mock_logger.info.assert_any_call("开始运行覆盖率测试")
        mock_logger.info.assert_any_call("覆盖率测试运行完成")
    
    @patch('run_tests.subprocess.run')
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_run_coverage_test_failure(self, mock_print, mock_logger, mock_subprocess_run):
        """测试覆盖率测试失败处理"""
        # 设置模拟对象返回失败
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "覆盖率测试输出"
        mock_result.stderr = "覆盖率测试错误"
        mock_subprocess_run.return_value = mock_result
        
        # 执行函数
        run_tests.run_coverage_test()
        
        # 验证失败被正确处理
        mock_logger.warning.assert_any_call(f"覆盖率测试警告: 覆盖率测试错误")
        mock_logger.error.assert_any_call(f"覆盖率测试失败，返回码: 1")
    
    @patch('run_tests.subprocess.run', side_effect=FileNotFoundError)
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_run_coverage_test_file_not_found(self, mock_print, mock_logger, mock_subprocess_run):
        """测试覆盖率测试依赖未安装的处理"""
        # 执行函数
        run_tests.run_coverage_test()
        
        # 验证错误被正确处理
        mock_logger.error.assert_any_call("pytest或pytest-cov未安装")
        mock_print.assert_any_call("pytest或pytest-cov未安装，请运行: pip install pytest pytest-cov")
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('run_tests.logger')
    def test_create_simple_test_file_new(self, mock_logger, mock_file, mock_makedirs, mock_exists):
        """测试创建新的测试文件"""
        # 设置模拟对象
        mock_exists.return_value = False
        
        # 执行函数
        test_path = "test_dir/test_file.txt"
        run_tests.create_simple_test_file(test_path)
        
        # 验证调用
        mock_exists.assert_called_once_with(test_path)
        mock_makedirs.assert_called_once_with(os.path.dirname(test_path), exist_ok=True)
        mock_file.assert_called_once_with(test_path, 'w', encoding='utf-8')
        mock_logger.info.assert_called_once_with(f"已创建测试文件: {test_path}")
    
    @patch('os.path.exists')
    @patch('run_tests.logger')
    def test_create_simple_test_file_exists(self, mock_logger, mock_exists):
        """测试文件已存在时不创建"""
        # 设置模拟对象
        mock_exists.return_value = True
        
        # 执行函数
        test_path = "test_dir/test_file.txt"
        run_tests.create_simple_test_file(test_path)
        
        # 验证不创建文件
        mock_exists.assert_called_once_with(test_path)
        self.assertEqual(mock_logger.info.call_count, 0)
    
    @patch('run_tests.subprocess.run')
    @patch('run_tests.os.path.exists')
    @patch('run_tests.create_simple_test_file')
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_run_integration_test_success(self, mock_print, mock_logger, mock_create_file, mock_exists, mock_subprocess_run):
        """测试成功运行集成测试"""
        # 设置模拟对象
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "集成测试输出"
        mock_subprocess_run.return_value = mock_result
        
        # 模拟读取结果文件
        mock_file = mock_open(read_data="0.85")
        
        with patch('builtins.open', mock_file):
            # 执行函数
            run_tests.run_integration_test()
        
        # 验证调用
        mock_logger.info.assert_any_call("开始运行集成测试")
        mock_logger.info.assert_any_call("集成测试运行完成")
    
    @patch('run_tests.subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=["python"], timeout=120))
    @patch('run_tests.os.path.exists')
    @patch('run_tests.create_simple_test_file')
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_run_integration_test_timeout(self, mock_print, mock_logger, mock_create_file, mock_exists, mock_subprocess_run):
        """测试集成测试超时处理"""
        # 设置模拟对象
        mock_exists.return_value = True
        
        # 执行函数
        run_tests.run_integration_test()
        
        # 验证超时被正确处理
        mock_logger.error.assert_any_call(f"集成测试 test_data/orig.txt vs test_data/orig_add.txt 超时")
        mock_print.assert_any_call("❌ 测试超时 (超过2分钟)")
    
    @patch('run_tests.run_unit_tests')
    @patch('run_tests.run_coverage_test')
    @patch('run_tests.run_integration_test')
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_main_success(self, mock_print, mock_logger, mock_integration, mock_coverage, mock_unit):
        """测试主函数正常流程"""
        # 执行函数
        run_tests.main()
        
        # 验证调用顺序
        mock_unit.assert_called_once()
        mock_coverage.assert_called_once()
        mock_integration.assert_called_once()
        mock_logger.info.assert_any_call("论文查重系统测试运行器启动")
    
    @patch('run_tests.run_unit_tests', side_effect=Exception("测试错误"))
    @patch('run_tests.logger')
    @patch('builtins.print')
    def test_main_exception_handling(self, mock_print, mock_logger, mock_unit):
        """测试主函数异常处理"""
        # 执行函数
        run_tests.main()
        
        # 验证异常被正确处理
        mock_logger.error.assert_called_once_with(f"测试过程中发生严重错误: 测试错误")
        mock_print.assert_any_call(f"\n❌ 测试过程中发生严重错误: 测试错误")

if __name__ == "__main__":
    unittest.main()