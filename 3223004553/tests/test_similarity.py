# -*- coding: utf-8 -*-
"""
相似度计算模块的单元测试
"""

import unittest
import sys
import os

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from similarity import TextSimilarityCalculator, calculate_text_similarity


class TestTextSimilarityCalculator(unittest.TestCase):
    """文本相似度计算器测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.calculator = TextSimilarityCalculator()
    
    def test_identical_texts(self):
        """测试完全相同的文本"""
        text1 = "今天是星期天，天气晴，今天晚上我要去看电影。"
        text2 = "今天是星期天，天气晴，今天晚上我要去看电影。"
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertEqual(similarity, 1.0)
    
    def test_completely_different_texts(self):
        """测试完全不同的文本"""
        text1 = "今天天气很好。"
        text2 = "明天会下雨。"
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertLess(similarity, 0.5)
    
    def test_partially_similar_texts(self):
        """测试部分相似的文本"""
        text1 = "今天是星期天，天气晴，今天晚上我要去看电影。"
        text2 = "今天是周天，天气晴朗，我晚上要去看电影。"
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertGreater(similarity, 0.5)
        self.assertLess(similarity, 1.0)
    
    def test_empty_texts(self):
        """测试空文本"""
        text1 = ""
        text2 = "今天天气很好。"
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertEqual(similarity, 0.0)
        
        text1 = "今天天气很好。"
        text2 = ""
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertEqual(similarity, 0.0)
        
        text1 = ""
        text2 = ""
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertEqual(similarity, 0.0)
    
    def test_text_with_special_characters(self):
        """测试包含特殊字符的文本"""
        text1 = "今天天气很好！@#$%^&*()"
        text2 = "今天天气很好"
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertGreater(similarity, 0.8)
    
    def test_long_texts(self):
        """测试长文本"""
        text1 = "这是一个很长的文本。" * 100
        text2 = "这是一个很长的文本。" * 100
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertEqual(similarity, 1.0)
    
    def test_text_preprocessing(self):
        """测试文本预处理功能"""
        text = "今天天气很好！@#$%^&*()"
        words = self.calculator.preprocess_text(text)
        # 检查是否包含预期的词或词素
        self.assertTrue(any('今天' in word for word in words) or '很' in words or '好' in words)
        # 特殊字符应该被过滤掉
        self.assertNotIn("！", words)
        # 确保结果不为空
        self.assertTrue(len(words) > 0)
    
    def test_cosine_similarity_calculation(self):
        """测试余弦相似度计算"""
        vec1 = {"今天": 1, "天气": 1, "很好": 1}
        vec2 = {"今天": 1, "天气": 1, "很好": 1}
        similarity = self.calculator.cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 1.0)
        
        vec1 = {"今天": 1, "天气": 1}
        vec2 = {"明天": 1, "下雨": 1}
        similarity = self.calculator.cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)
    
    def test_tf_idf_calculation(self):
        """测试TF-IDF计算"""
        texts = [
            ["今天", "天气", "很好"],
            ["今天", "天气", "不好"],
            ["明天", "会", "下雨"]
        ]
        tf_idf_vectors, idf_dict = self.calculator.calculate_tf_idf(texts)
        
        self.assertEqual(len(tf_idf_vectors), 3)
        self.assertIsInstance(idf_dict, dict)
        self.assertIn("今天", idf_dict)
    
    def test_similarity_range(self):
        """测试相似度值在合理范围内"""
        text1 = "今天天气很好。"
        text2 = "明天会下雨。"
        similarity = self.calculator.calculate_similarity(text1, text2)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)


class TestCalculateTextSimilarity(unittest.TestCase):
    """便捷函数测试类"""
    
    def test_convenience_function(self):
        """测试便捷函数"""
        text1 = "今天天气很好。"
        text2 = "今天天气很好。"
        similarity = calculate_text_similarity(text1, text2)
        self.assertEqual(similarity, 1.0)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
