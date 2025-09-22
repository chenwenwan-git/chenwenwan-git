# -*- coding: utf-8 -*-
"""
性能分析脚本
用于分析论文查重系统的性能瓶颈
"""

import cProfile
import pstats
import io
import time
import os
import sys
from similarity import TextSimilarityCalculator
from file_handler import FileHandler


def create_large_text(size_mb=1):
    """
    创建指定大小的测试文本
    
    Args:
        size_mb: 文本大小（MB）
    
    Returns:
        生成的文本
    """
    base_text = "这是一个用于性能测试的文本内容，包含中文和英文单词。"
    target_size = size_mb * 1024 * 1024  # 转换为字节
    
    text = ""
    while len(text.encode('utf-8')) < target_size:
        text += base_text + " "
    
    return text


def profile_similarity_calculation():
    """分析相似度计算的性能"""
    print("=" * 50)
    print("相似度计算性能分析")
    print("=" * 50)
    
    # 创建测试数据
    text1 = create_large_text(0.5)  # 0.5MB
    text2 = create_large_text(0.5)  # 0.5MB
    
    calculator = TextSimilarityCalculator()
    
    # 使用cProfile进行分析
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 执行相似度计算
    start_time = time.time()
    similarity = calculator.calculate_similarity(text1, text2)
    end_time = time.time()
    
    profiler.disable()
    
    print(f"计算时间: {end_time - start_time:.4f} 秒")
    print(f"相似度结果: {similarity}")
    
    # 分析性能数据
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # 显示前20个最耗时的函数
    
    print("\n性能分析结果:")
    print(s.getvalue())


def profile_file_operations():
    """分析文件操作的性能"""
    print("\n" + "=" * 50)
    print("文件操作性能分析")
    print("=" * 50)
    
    handler = FileHandler()
    
    # 创建测试文件
    test_file = "performance_test.txt"
    test_content = create_large_text(1)  # 1MB
    
    # 测试写入性能
    start_time = time.time()
    success = handler.write_file(test_file, test_content)
    write_time = time.time() - start_time
    
    print(f"写入文件时间: {write_time:.4f} 秒")
    print(f"写入成功: {success}")
    
    # 测试读取性能
    start_time = time.time()
    content = handler.read_file(test_file)
    read_time = time.time() - start_time
    
    print(f"读取文件时间: {read_time:.4f} 秒")
    print(f"读取成功: {content is not None}")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)


def profile_text_preprocessing():
    """分析文本预处理的性能"""
    print("\n" + "=" * 50)
    print("文本预处理性能分析")
    print("=" * 50)
    
    calculator = TextSimilarityCalculator()
    
    # 创建不同大小的测试文本
    sizes = [0.1, 0.5, 1.0]  # MB
    
    for size in sizes:
        text = create_large_text(size)
        
        start_time = time.time()
        words = calculator.preprocess_text(text)
        end_time = time.time()
        
        print(f"文本大小: {size}MB")
        print(f"预处理时间: {end_time - start_time:.4f} 秒")
        print(f"分词数量: {len(words)}")
        print("-" * 30)


def profile_memory_usage():
    """分析内存使用情况"""
    print("\n" + "=" * 50)
    print("内存使用分析")
    print("=" * 50)
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # 记录初始内存
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"初始内存使用: {initial_memory:.2f} MB")
    
    # 创建大文本并计算相似度
    calculator = TextSimilarityCalculator()
    text1 = create_large_text(1)
    text2 = create_large_text(1)
    
    # 记录计算前内存
    before_memory = process.memory_info().rss / 1024 / 1024
    print(f"计算前内存使用: {before_memory:.2f} MB")
    
    # 执行计算
    similarity = calculator.calculate_similarity(text1, text2)
    
    # 记录计算后内存
    after_memory = process.memory_info().rss / 1024 / 1024
    print(f"计算后内存使用: {after_memory:.2f} MB")
    print(f"内存增长: {after_memory - before_memory:.2f} MB")
    print(f"相似度结果: {similarity}")


def benchmark_different_algorithms():
    """对比不同算法的性能"""
    print("\n" + "=" * 50)
    print("算法性能对比")
    print("=" * 50)
    
    calculator = TextSimilarityCalculator()
    
    # 测试不同长度的文本
    test_cases = [
        ("短文本", "今天天气很好。", "今天天气不错。"),
        ("中等文本", "今天是星期天，天气晴，今天晚上我要去看电影。" * 10, 
         "今天是周天，天气晴朗，我晚上要去看电影。" * 10),
        ("长文本", create_large_text(0.1), create_large_text(0.1))
    ]
    
    for name, text1, text2 in test_cases:
        print(f"\n{name}测试:")
        print(f"文本1长度: {len(text1)} 字符")
        print(f"文本2长度: {len(text2)} 字符")
        
        start_time = time.time()
        similarity = calculator.calculate_similarity(text1, text2)
        end_time = time.time()
        
        print(f"计算时间: {end_time - start_time:.4f} 秒")
        print(f"相似度: {similarity}")


def main():
    """主函数"""
    print("论文查重系统 - 性能分析工具")
    
    try:
        # 相似度计算性能分析
        profile_similarity_calculation()
        
        # 文件操作性能分析
        profile_file_operations()
        
        # 文本预处理性能分析
        profile_text_preprocessing()
        
        # 内存使用分析
        try:
            profile_memory_usage()
        except ImportError:
            print("\npsutil未安装，跳过内存分析。安装命令: pip install psutil")
        
        # 算法性能对比
        benchmark_different_algorithms()
        
    except Exception as e:
        print(f"性能分析过程中发生错误: {e}")
    
    print("\n" + "=" * 50)
    print("性能分析完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
