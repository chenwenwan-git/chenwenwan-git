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
import logging
import os

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
        try:
            if not text or not isinstance(text, str):
                logger.warning("无效的文本输入")
                return []
            
            # 去除标点符号和特殊字符，保留中文、英文、数字
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
            
            # 根据系统类型选择分词模式
            if os.name == 'nt':  # Windows系统
                # Windows系统不支持并行分词，直接使用串行模式
                logger.info("检测到Windows系统，使用串行分词模式")
                words = jieba.lcut(text)
            else:
                # 非Windows系统尝试并行分词
                try:
                    logger.info("尝试使用并行分词模式")
                    jieba.enable_parallel()  # 开启并行分词模式
                    words = jieba.lcut(text)
                except Exception as e:
                    logger.warning(f"并行分词失败，使用串行模式: {e}")
                    words = jieba.lcut(text)  # 回退到串行模式
                finally:
                    try:
                        jieba.disable_parallel()  # 关闭并行分词模式
                    except:
                        pass  # 忽略可能的错误
            
            # 去除停用词和空字符串
            words = [word.strip() for word in words if word.strip() and word not in self.stop_words]
            logger.info(f"文本预处理完成，分词数量: {len(words)}")
            return words
        except Exception as e:
            logger.error(f"文本预处理失败: {e}")
            return []
    
    def calculate_tf_idf(self, texts: List[List[str]]) -> Tuple[List[dict], dict]:
        """
        计算TF-IDF值（优化版）
        
        Args:
            texts: 文本列表，每个文本是词列表
            
        Returns:
            (tf_idf_vectors, idf_dict): TF-IDF向量和IDF字典
        """
        # 计算词频(TF)和文档频率(DF)同时进行
        tf_vectors = []
        df_dict = Counter()  # 文档频率计数器
        
        for text in texts:
            unique_words = set(text)  # 获取文本中的唯一词汇
            df_dict.update(unique_words)  # 更新文档频率
            word_count = Counter(text)  # 计算词频
            # 归一化词频
            total_words = len(text)
            if total_words > 0:
                normalized_tf = {word: count/total_words for word, count in word_count.items()}
            else:
                normalized_tf = {}
            tf_vectors.append(normalized_tf)
        
        # 计算逆文档频率(IDF)
        total_docs = len(texts)
        idf_dict = {word: np.log(total_docs / (df_count + 1)) for word, df_count in df_dict.items()}
        
        # 计算TF-IDF向量
        tf_idf_vectors = []
        for tf_vec in tf_vectors:
            tf_idf_vec = {word: tf * idf_dict[word] for word, tf in tf_vec.items()}
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
        计算两个文本的相似度（优化版）
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            相似度值，范围0-1
        """
        try:
            logger.info(f"开始计算文本相似度")
            
            # 检查文本是否为空
            if not text1 or not text2:
                logger.warning("至少一个文本为空")
                return 0.0
            
            # 预处理文本
            logger.info(f"开始预处理文本")
            tokens1 = self.preprocess_text(text1)
            tokens2 = self.preprocess_text(text2)
            
            # 检查预处理后的文本是否为空
            if not tokens1 and not tokens2:
                logger.info("两个文本预处理后都为空，相似度为1.0")
                return 1.0
            elif not tokens1 or not tokens2:
                logger.warning("至少一个文本的预处理结果为空")
                return 0.0
            
            # 计算TF-IDF
            logger.info(f"开始计算TF-IDF")
            tf_idf_vectors, idf_dict = self.calculate_tf_idf([tokens1, tokens2])
            
            # 计算余弦相似度
            logger.info(f"开始计算余弦相似度")
            similarity = self.cosine_similarity(tf_idf_vectors[0], tf_idf_vectors[1])
            
            logger.info(f"相似度计算完成，相似度值: {similarity}")
            return round(similarity, 2)
        except Exception as e:
            logger.error(f"计算相似度时发生错误: {e}")
            return 0.0
            
    def calculate_file_similarity(self, file1_path: str, file2_path: str) -> float:
        """
        计算两个文件的文本相似度
        
        Args:
            file1_path: 第一个文件路径
            file2_path: 第二个文件路径
            
        Returns:
            相似度值，范围0-1
        """
        try:
            logger.info(f"开始计算文件相似度: {file1_path} vs {file2_path}")
            
            from file_handler import FileHandler
            # 读取文件内容
            file_handler = FileHandler()
            
            # 检查文件大小，大文件使用分块读取
            file1_size = file_handler.get_file_size(file1_path)
            file2_size = file_handler.get_file_size(file2_path)
            
            if file1_size > 10 * 1024 * 1024 or file2_size > 10 * 1024 * 1024:
                # 大文件（>10MB）使用分块读取
                logger.info(f"使用分块读取大文件")
                content1 = file_handler.read_large_file(file1_path)
                content2 = file_handler.read_large_file(file2_path)
            else:
                # 普通文件直接读取
                content1 = file_handler.read_file(file1_path)
                content2 = file_handler.read_file(file2_path)
            
            if content1 is None or content2 is None:
                raise Exception("文件读取失败")
            
            # 计算文本相似度
            return self.calculate_similarity(content1, content2)
        except FileNotFoundError as e:
            logger.error(f"文件不存在: {e}")
            return 0.0
        except PermissionError as e:
            logger.error(f"没有读取权限: {e}")
            return 0.0
        except UnicodeDecodeError as e:
            logger.error(f"文件编码错误: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"计算文件相似度时发生错误: {e}")
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
