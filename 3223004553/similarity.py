# -*- coding: utf-8 -*-
"""
论文查重系统 - 相似度计算模块
使用余弦相似度算法计算文本相似度
"""

import re
import jieba
import numpy as np
from collections import Counter
from typing import List, Tuple


class TextSimilarityCalculator:
    """文本相似度计算器"""
    
    def __init__(self):
        """初始化计算器"""
        # 停用词列表（可根据需要扩展）
        self.stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        文本预处理
        包括：去除标点符号、分词、去除停用词
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的词列表
        """
        if not text:
            return []
        
        # 去除标点符号和特殊字符，保留中文、英文、数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
        
        # 使用jieba分词
        words = jieba.lcut(text)
        
        # 去除停用词和空字符串
        words = [word.strip() for word in words if word.strip() and word not in self.stop_words]
        
        return words
    
    def calculate_tf_idf(self, texts: List[List[str]]) -> Tuple[List[dict], dict]:
        """
        计算TF-IDF值
        
        Args:
            texts: 文本列表，每个文本是词列表
            
        Returns:
            (tf_idf_vectors, idf_dict): TF-IDF向量和IDF字典
        """
        # 计算词频(TF)
        tf_vectors = []
        all_words = set()
        
        for text in texts:
            word_count = Counter(text)
            tf_vectors.append(word_count)
            all_words.update(text)
        
        # 计算逆文档频率(IDF)
        idf_dict = {}
        total_docs = len(texts)
        
        for word in all_words:
            doc_count = sum(1 for tf_vec in tf_vectors if word in tf_vec)
            idf_dict[word] = np.log(total_docs / (doc_count + 1))  # 加1避免除零
        
        # 计算TF-IDF向量
        tf_idf_vectors = []
        for tf_vec in tf_vectors:
            tf_idf_vec = {}
            for word, tf in tf_vec.items():
                tf_idf_vec[word] = tf * idf_dict[word]
            tf_idf_vectors.append(tf_idf_vec)
        
        return tf_idf_vectors, idf_dict
    
    def cosine_similarity(self, vec1: dict, vec2: dict) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec1: 第一个向量（字典形式）
            vec2: 第二个向量（字典形式）
            
        Returns:
            余弦相似度值 (0-1之间)
        """
        # 获取所有词汇
        all_words = set(vec1.keys()) | set(vec2.keys())
        
        if not all_words:
            return 0.0
        
        # 构建向量
        v1 = np.array([vec1.get(word, 0) for word in all_words])
        v2 = np.array([vec2.get(word, 0) for word in all_words])
        
        # 计算余弦相似度
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return max(0.0, min(1.0, similarity))  # 确保结果在[0,1]范围内
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            相似度值 (0-1之间，保留两位小数)
        """
        try:
            # 文本预处理
            words1 = self.preprocess_text(text1)
            words2 = self.preprocess_text(text2)
            
            # 如果任一文本为空，返回0
            if not words1 or not words2:
                return 0.0
            
            # 计算TF-IDF
            tf_idf_vectors, _ = self.calculate_tf_idf([words1, words2])
            
            # 计算余弦相似度
            similarity = self.cosine_similarity(tf_idf_vectors[0], tf_idf_vectors[1])
            
            # 返回保留两位小数的结果
            return round(similarity, 2)
            
        except Exception as e:
            # 发生异常时返回0
            print(f"计算相似度时发生错误: {e}")
            return 0.0


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    便捷函数：计算两个文本的相似度
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        
    Returns:
        相似度值 (0-1之间，保留两位小数)
    """
    calculator = TextSimilarityCalculator()
    return calculator.calculate_similarity(text1, text2)


if __name__ == "__main__":
    # 测试代码
    calculator = TextSimilarityCalculator()
    
    # 测试用例
    text1 = "今天是星期天，天气晴，今天晚上我要去看电影。"
    text2 = "今天是周天，天气晴朗，我晚上要去看电影。"
    
    similarity = calculator.calculate_similarity(text1, text2)
    print(f"文本1: {text1}")
    print(f"文本2: {text2}")
    print(f"相似度: {similarity}")
