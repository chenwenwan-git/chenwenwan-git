# -*- coding: utf-8 -*-
import jieba

# 测试分词结果
text = "今天天气很好！@#$%^&*()"
words = jieba.lcut(text)
print("原始分词结果:", words)

# 移除空格和空字符串
words = [word.strip() for word in words if word.strip()]
print("处理后的分词结果:", words)