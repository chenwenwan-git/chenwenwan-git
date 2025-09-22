# -*- coding: utf-8 -*-
"""
论文查重系统 - 主程序
使用方法: python main.py [原文文件] [抄袭版论文的文件] [答案文件]
"""

import sys
import os
import logging
from typing import Optional

from similarity import calculate_text_similarity
from file_handler import read_text_file, write_text_file

# 配置日志
def setup_logger():
    # 修复中文编码问题，兼容Python 3.8及以下版本
    logger = logging.getLogger('plagiarism_checker')
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建文件处理器，显式指定UTF-8编码
        try:
            # 尝试使用FileHandler设置编码
            handler = logging.FileHandler('plagiarism_checker.log', encoding='utf-8')
        except TypeError:
            # 对于不支持encoding参数的旧版本Python
            handler = logging.FileHandler('plagiarism_checker.log')
            
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # 添加处理器到logger
        logger.addHandler(handler)
    
    return logger

logger = setup_logger()


def print_usage():
    # 用户使用提示
    print("使用方法: python main.py [原文文件] [抄袭版论文的文件] [答案文件]")
    print("示例: python main.py orig.txt orig_add.txt ans.txt")


def validate_arguments(args: list) -> bool:
    """
    验证命令行参数
    
    Args:
        args: 命令行参数列表
        
    Returns:
        参数有效返回True，否则返回False
    """
    if len(args) != 4:
        print("错误: 参数数量不正确")
        print_usage()
        return False
    
    # 检查文件路径
    for i, file_path in enumerate(args[1:], 1):
        if not file_path or not isinstance(file_path, str):
            print(f"错误: 第{i}个参数不是有效的文件路径")
            return False
        
        if i <= 2:  # 前两个是输入文件
            if not os.path.exists(file_path):
                print(f"错误: 文件不存在: {file_path}")
                return False
    
    return True


def calculate_plagiarism_rate(original_file: str, plagiarized_file: str, output_file: str) -> bool:
    """
    计算论文重复率
    
    Args:
        original_file: 原文文件路径
        plagiarized_file: 抄袭版论文文件路径
        output_file: 输出答案文件路径
        
    Returns:
        计算成功返回True，失败返回False
    """
    try:
        # 读取原文
        logger.info(f"正在读取原文文件: {original_file}")
        print(f"正在读取原文文件: {original_file}")
        original_text = read_text_file(original_file)
        if original_text is None:
            logger.error("错误: 无法读取原文文件")
            print("错误: 无法读取原文文件")
            return False
        
        # 读取抄袭版论文
        logger.info(f"正在读取抄袭版论文文件: {plagiarized_file}")
        print(f"正在读取抄袭版论文文件: {plagiarized_file}")
        plagiarized_text = read_text_file(plagiarized_file)
        if plagiarized_text is None:
            logger.error("错误: 无法读取抄袭版论文文件")
            print("错误: 无法读取抄袭版论文文件")
            return False
        
        # 检查文本是否为空
        if not original_text.strip():
            logger.error("错误: 原文文件为空")
            print("错误: 原文文件为空")
            return False
        
        if not plagiarized_text.strip():
            logger.error("错误: 抄袭版论文文件为空")
            print("错误: 抄袭版论文文件为空")
            return False
        
        # 计算相似度
        logger.info("正在计算文本相似度...")
        print("正在计算文本相似度...")
        similarity = calculate_text_similarity(original_text, plagiarized_text)
        
        # 输出结果
        logger.info(f"计算完成，相似度: {similarity}")
        print(f"计算完成，相似度: {similarity}")
        
        # 写入结果文件
        logger.info(f"正在写入结果文件: {output_file}")
        print(f"正在写入结果文件: {output_file}")
        success = write_text_file(output_file, str(similarity))
        
        if success:
            logger.info("论文查重完成！")
            print("论文查重完成！")
            return True
        else:
            logger.error("错误: 无法写入结果文件")
            print("错误: 无法写入结果文件")
            return False
            
    except Exception as e:
        # 处理异常
        logger.error(f"计算过程中发生错误: {e}")
        print(f"计算过程中发生错误: {e}")
        return False


def main():
    """主函数"""
    try:
        # 获取命令行参数
        args = sys.argv
        
        # 验证参数
        if not validate_arguments(args):
            sys.exit(1)
        
        # 提取文件路径
        original_file = args[1]
        plagiarized_file = args[2]
        output_file = args[3]
        
        print("=" * 50)
        print("论文查重系统")
        print("=" * 50)
        print(f"原文文件: {original_file}")
        print(f"抄袭版论文文件: {plagiarized_file}")
        print(f"输出文件: {output_file}")
        print("=" * 50)
        
        # 计算重复率
        success = calculate_plagiarism_rate(original_file, plagiarized_file, output_file)
        
        if success:
            print("程序执行成功！")
            sys.exit(0)
        else:
            print("程序执行失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行过程中发生未预期的错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
