import unittest
import jieba

class TestTokenization(unittest.TestCase):
    
    def test_basic_tokenization(self):
        """测试基本分词功能"""
        # 测试简单中文句子
        text = "这是一个测试句子"
        words = jieba.lcut(text)
        # 检查分词结果是否合理
        self.assertTrue(len(words) > 0)
        self.assertTrue("测试" in words or "句子" in words)  # 至少包含一个有意义的词
        
        # 测试复杂中文句子
        complex_text = "这是一段包含多个复杂词汇的中文测试文本"
        complex_words = jieba.lcut(complex_text)
        self.assertTrue(len(complex_words) > 0)
        
        # 检查分词结果是否包含预期的词
        expected_words = ["这是", "一段", "包含", "多个", "复杂", "词汇", "的", "中文", "测试", "文本"]
        for word in expected_words:
            self.assertTrue(word in complex_words)
    
    def test_edge_cases(self):
        """测试边缘情况"""
        # 测试空字符串
        empty_text = ""
        empty_words = jieba.lcut(empty_text)
        empty_processed = [word.strip() for word in empty_words if word.strip()]
        self.assertEqual(len(empty_processed), 0)
        
        # 测试只有空白字符的字符串
        whitespace_text = "   \t\n  "
        whitespace_words = jieba.lcut(whitespace_text)
        whitespace_processed = [word.strip() for word in whitespace_words if word.strip()]
        self.assertEqual(len(whitespace_processed), 0)
        
        # 测试只有标点符号的字符串
        punctuation_text = "，。！？；："
        punctuation_words = jieba.lcut(punctuation_text)
        punctuation_processed = [word for word in punctuation_words if word.strip()]
        # 标点符号应该被单独切分
        self.assertEqual(len(punctuation_processed), len(punctuation_text))
    
    def test_mixed_text(self):
        """测试中英文混合文本"""
        # 测试中英文混合
        mixed_text = "这是一个English中文混合text"
        mixed_words = jieba.lcut(mixed_text)
        
        # 检查英文部分是否被正确处理
        self.assertTrue("English" in mixed_words or "text" in mixed_words)
        # 检查中文部分是否被正确处理
        self.assertTrue("这是" in mixed_words or "一个" in mixed_words or "中文" in mixed_words or "混合" in mixed_words)
        
    def test_special_characters(self):
        """测试包含特殊字符的文本"""
        # 测试包含数字和特殊符号的文本
        special_text = "这个价格是¥99.99，折扣是8折！"
        special_words = jieba.lcut(special_text)
        
        # 检查是否成功分词
        self.assertTrue(len(special_words) > 0)
        
        # 检查是否包含关键中文词汇
        self.assertTrue("价格" in special_words or "折扣" in special_words)
        
    def test_long_text(self):
        """测试长文本分词性能"""
        # 创建一个较长的文本
        long_text = "这是一个" * 50 + "很长很长的句子" * 20
        
        # 确保分词不会崩溃并且能处理长文本
        try:
            long_words = jieba.lcut(long_text)
            self.assertTrue(len(long_words) > 0)
        except Exception as e:
            self.fail(f"长文本分词失败: {e}")

if __name__ == "__main__":
    unittest.main()