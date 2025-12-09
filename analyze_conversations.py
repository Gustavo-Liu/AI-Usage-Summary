#!/usr/bin/env python3
"""
AI Year-In-Review: Conversation Analysis Script
分析 ChatGPT conversations.json 文件，生成 summary.json
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import sys

# 尝试导入可选依赖
try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("警告: jieba 未安装，中文分词功能将受限。安装: pip install jieba")

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("警告: langdetect 未安装，语言检测功能将受限。安装: pip install langdetect")

try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    import nltk
    NLTK_AVAILABLE = True
    # 尝试下载必要的 NLTK 数据
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
except ImportError:
    NLTK_AVAILABLE = False
    print("警告: nltk 未安装，英文分词功能将受限。安装: pip install nltk")


class ConversationAnalyzer:
    """对话分析器"""
    
    # 书籍字数参考（用于换算）
    BOOK_SIZES = {
        "三体": 200000,  # 约20万字
        "哈利波特": 100000,  # 约10万字
        "小王子": 20000,  # 约2万字
    }
    
    # 礼貌用语关键词
    POLITE_KEYWORDS = {
        "en": ["please", "thank you", "thanks", "help", "appreciate"],
        "zh": ["请", "谢谢", "感谢", "帮忙", "帮", "救命", "麻烦"]
    }
    
    def __init__(self, conversations: List[Dict]):
        self.conversations = conversations
        self.summary = {}
        
    def count_characters(self, text: str) -> int:
        """统计字符数（中文字符按1个计算）"""
        return len(text)
    
    def extract_text_from_message(self, message: Dict) -> str:
        """从消息中提取文本内容"""
        if not message or "content" not in message:
            return ""
        content = message["content"]
        if isinstance(content, dict) and "parts" in content:
            parts = content["parts"]
            if isinstance(parts, list):
                return " ".join(str(p) for p in parts if p)
        return str(content) if content else ""
    
    def analyze_summary_stats(self):
        """1. 基础统计：总时长、总字数、最活跃时间"""
        total_user_chars = 0
        total_assistant_chars = 0
        total_messages = 0
        conversation_count = len(self.conversations)
        
        # 时间统计
        timestamps = []
        date_counts = defaultdict(int)
        hour_counts = defaultdict(int)
        weekday_counts = defaultdict(int)
        
        for conv in self.conversations:
            create_time = conv.get("create_time")
            if create_time:
                dt = datetime.fromtimestamp(create_time)
                timestamps.append(dt)
                date_counts[dt.date()] += 1
                hour_counts[dt.hour] += 1
                weekday_counts[dt.weekday()] += 1
            
            # 遍历 mapping 中的所有消息
            mapping = conv.get("mapping", {})
            for node_id, node in mapping.items():
                if node_id == "client-created-root":
                    continue
                message = node.get("message")
                if not message:
                    continue
                
                author = message.get("author", {})
                role = author.get("role", "")
                text = self.extract_text_from_message(message)
                
                if role == "user":
                    total_user_chars += self.count_characters(text)
                    total_messages += 1
                elif role == "assistant":
                    total_assistant_chars += self.count_characters(text)
        
        # 计算总时长（从最早到最晚）
        total_hours = 0
        if timestamps:
            earliest = min(timestamps)
            latest = max(timestamps)
            total_hours = (latest - earliest).total_seconds() / 3600
        
        # 最活跃的日期
        most_active_date = max(date_counts.items(), key=lambda x: x[1]) if date_counts else None
        most_active_hour = max(hour_counts.items(), key=lambda x: x[1]) if hour_counts else None
        
        # 换算成书籍
        books_equivalent = {}
        for book_name, book_size in self.BOOK_SIZES.items():
            books_equivalent[book_name] = round(total_assistant_chars / book_size, 1)
        
        self.summary["summary_stats"] = {
            "total_conversations": conversation_count,
            "total_messages": total_messages,
            "total_user_characters": total_user_chars,
            "total_assistant_characters": total_assistant_chars,
            "total_hours_span": round(total_hours, 1),
            "most_active_date": {
                "date": str(most_active_date[0]) if most_active_date else None,
                "count": most_active_date[1] if most_active_date else 0
            },
            "most_active_hour": {
                "hour": most_active_hour[0] if most_active_hour else None,
                "count": most_active_hour[1] if most_active_hour else 0
            },
            "books_equivalent": books_equivalent
        }
    
    def analyze_brain_activity_heatmap(self):
        """2. 大脑活跃热力图：24小时 x 7天"""
        # hour (0-23) x weekday (0-6, Monday=0)
        heatmap_data = defaultdict(int)
        
        for conv in self.conversations:
            create_time = conv.get("create_time")
            if not create_time:
                continue
            
            dt = datetime.fromtimestamp(create_time)
            hour = dt.hour
            weekday = dt.weekday()
            heatmap_data[(hour, weekday)] += 1
        
        # 转换为数组格式：[[hour, weekday, count], ...]
        heatmap_array = [[h, w, c] for (h, w), c in heatmap_data.items()]
        
        # 也生成按小时和按周日的统计
        hour_distribution = defaultdict(int)
        weekday_distribution = defaultdict(int)
        for (h, w), count in heatmap_data.items():
            hour_distribution[h] += count
            weekday_distribution[w] += count
        
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        self.summary["brain_activity_heatmap"] = {
            "heatmap_data": heatmap_array,
            "hour_distribution": dict(hour_distribution),
            "weekday_distribution": {weekday_names[i]: weekday_distribution[i] for i in range(7)}
        }
    
    def analyze_keywords(self):
        """3. 年度知识图谱：高频关键词"""
        all_text = []
        
        for conv in self.conversations:
            mapping = conv.get("mapping", {})
            for node_id, node in mapping.items():
                if node_id == "client-created-root":
                    continue
                message = node.get("message")
                if not message:
                    continue
                
                author = message.get("author", {})
                role = author.get("role", "")
                if role == "user":  # 只分析用户输入
                    text = self.extract_text_from_message(message)
                    if text:
                        all_text.append(text)
        
        combined_text = " ".join(all_text)
        
        # 关键词提取
        keywords = []
        
        # 中文分词
        if JIEBA_AVAILABLE:
            # 使用 TF-IDF 提取关键词
            keywords_zh = jieba.analyse.extract_tags(combined_text, topK=30, withWeight=True)
            for word, weight in keywords_zh:
                if len(word) > 1:  # 过滤单字
                    keywords.append({"word": word, "frequency": int(weight * 1000), "language": "zh"})
        
        # 英文关键词（简单词频统计）
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(combined_text.lower())
                stop_words = set(stopwords.words('english'))
                # 过滤停用词和短词
                filtered_tokens = [t for t in tokens if t.isalpha() and len(t) > 2 and t not in stop_words]
                word_freq = Counter(filtered_tokens)
                for word, freq in word_freq.most_common(20):
                    keywords.append({"word": word, "frequency": freq, "language": "en"})
            except Exception as e:
                print(f"英文分词出错: {e}")
        
        # 如果没有分词库，使用简单的正则提取
        if not keywords:
            # 提取中文词（2-4字）
            zh_words = re.findall(r'[\u4e00-\u9fff]{2,4}', combined_text)
            zh_freq = Counter(zh_words)
            for word, freq in zh_freq.most_common(20):
                keywords.append({"word": word, "frequency": freq, "language": "zh"})
            
            # 提取英文词
            en_words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text.lower())
            en_freq = Counter(en_words)
            for word, freq in en_freq.most_common(20):
                keywords.append({"word": word, "frequency": freq, "language": "en"})
        
        # 按频率排序
        keywords.sort(key=lambda x: x["frequency"], reverse=True)
        
        self.summary["keywords"] = {
            "top_keywords": keywords[:30],  # Top 30
            "total_unique_keywords": len(set(k["word"] for k in keywords))
        }
    
    def analyze_deep_dive_index(self):
        """4. 思维深潜度：对话轮数分布"""
        turn_counts = []
        conversation_turns = []
        
        for conv in self.conversations:
            mapping = conv.get("mapping", {})
            # 计算每个对话的轮数（user 消息数）
            user_message_count = 0
            for node_id, node in mapping.items():
                if node_id == "client-created-root":
                    continue
                message = node.get("message")
                if message:
                    author = message.get("author", {})
                    if author.get("role") == "user":
                        user_message_count += 1
            
            if user_message_count > 0:
                turn_counts.append(user_message_count)
                conversation_turns.append({
                    "conversation_id": conv.get("conversation_id", ""),
                    "title": conv.get("title", ""),
                    "turns": user_message_count
                })
        
        # 分类统计
        shallow = sum(1 for t in turn_counts if 1 <= t <= 2)
        medium = sum(1 for t in turn_counts if 3 <= t <= 9)
        deep = sum(1 for t in turn_counts if t >= 10)
        
        self.summary["deep_dive_index"] = {
            "total_conversations": len(turn_counts),
            "average_turns": round(sum(turn_counts) / len(turn_counts), 1) if turn_counts else 0,
            "distribution": {
                "shallow_1_2_turns": shallow,
                "medium_3_9_turns": medium,
                "deep_10plus_turns": deep
            },
            "max_turns": max(turn_counts) if turn_counts else 0,
            "top_deep_conversations": sorted(conversation_turns, key=lambda x: x["turns"], reverse=True)[:5]
        }
    
    def analyze_directors_ratio(self):
        """5. 输入输出比"""
        total_user_chars = self.summary["summary_stats"]["total_user_characters"]
        total_assistant_chars = self.summary["summary_stats"]["total_assistant_characters"]
        
        ratio = round(total_assistant_chars / total_user_chars, 2) if total_user_chars > 0 else 0
        
        # 判断类型
        if ratio >= 8:
            persona_type = "学习者"
            description = "你在大量吸收信息，是一个积极的学习者"
        elif ratio >= 3:
            persona_type = "平衡型"
            description = "你与 AI 的互动比较平衡"
        else:
            persona_type = "创作者"
            description = "你提供了大量上下文，更像是在与 AI 协作创作"
        
        self.summary["directors_ratio"] = {
            "input_chars": total_user_chars,
            "output_chars": total_assistant_chars,
            "ratio": ratio,
            "ratio_display": f"1:{ratio}",
            "persona_type": persona_type,
            "description": description
        }
    
    def analyze_linguistic_profile(self):
        """6. 语言偏好分布"""
        language_counts = defaultdict(int)
        total_messages = 0
        
        for conv in self.conversations:
            mapping = conv.get("mapping", {})
            for node_id, node in mapping.items():
                if node_id == "client-created-root":
                    continue
                message = node.get("message")
                if not message:
                    continue
                
                author = message.get("author", {})
                if author.get("role") != "user":
                    continue
                
                text = self.extract_text_from_message(message)
                if not text or len(text.strip()) < 5:
                    continue
                
                total_messages += 1
                
                # 语言检测
                if LANGDETECT_AVAILABLE:
                    try:
                        lang = detect(text)
                        language_counts[lang] += 1
                    except (LangDetectException, Exception):
                        # 简单启发式：中文字符比例
                        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
                        if chinese_chars / len(text) > 0.3:
                            language_counts["zh"] += 1
                        else:
                            language_counts["en"] += 1
                else:
                    # 简单启发式
                    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
                    if chinese_chars / len(text) > 0.3:
                        language_counts["zh"] += 1
                    else:
                        language_counts["en"] += 1
        
        # 计算百分比
        language_percentages = {}
        for lang, count in language_counts.items():
            language_percentages[lang] = round(count / total_messages * 100, 1) if total_messages > 0 else 0
        
        language_names = {"zh": "中文", "en": "英文"}
        
        self.summary["linguistic_profile"] = {
            "total_messages_analyzed": total_messages,
            "language_counts": dict(language_counts),
            "language_percentages": language_percentages,
            "primary_language": max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else "unknown",
            "language_display": {language_names.get(k, k): v for k, v in language_percentages.items()}
        }
    
    def analyze_marathon_session(self):
        """7. 最长思维马拉松"""
        max_turns = 0
        marathon_conv = None
        
        for conv in self.conversations:
            mapping = conv.get("mapping", {})
            user_message_count = 0
            for node_id, node in mapping.items():
                if node_id == "client-created-root":
                    continue
                message = node.get("message")
                if message:
                    author = message.get("author", {})
                    if author.get("role") == "user":
                        user_message_count += 1
            
            if user_message_count > max_turns:
                max_turns = user_message_count
                marathon_conv = conv
        
        if marathon_conv:
            create_time = marathon_conv.get("create_time")
            date_str = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d") if create_time else "未知"
            
            self.summary["marathon_session"] = {
                "title": marathon_conv.get("title", "未命名对话"),
                "date": date_str,
                "turns": max_turns,
                "conversation_id": marathon_conv.get("conversation_id", "")
            }
        else:
            self.summary["marathon_session"] = None
    
    def analyze_monthly_focus(self):
        """8. 月度专注主题"""
        monthly_texts = defaultdict(list)
        
        for conv in self.conversations:
            create_time = conv.get("create_time")
            if not create_time:
                continue
            
            dt = datetime.fromtimestamp(create_time)
            month_key = f"{dt.year}-{dt.month:02d}"
            
            mapping = conv.get("mapping", {})
            for node_id, node in mapping.items():
                if node_id == "client-created-root":
                    continue
                message = node.get("message")
                if message:
                    author = message.get("author", {})
                    if author.get("role") == "user":
                        text = self.extract_text_from_message(message)
                        if text:
                            monthly_texts[month_key].append(text)
        
        monthly_topics = []
        for month, texts in sorted(monthly_texts.items()):
            combined = " ".join(texts)
            
            # 提取关键词
            keywords = []
            if JIEBA_AVAILABLE:
                try:
                    keywords_zh = jieba.analyse.extract_tags(combined, topK=3, withWeight=True)
                    keywords.extend([w for w, _ in keywords_zh if len(w) > 1])
                except:
                    pass
            
            # 如果没有关键词，使用简单词频
            if not keywords:
                zh_words = re.findall(r'[\u4e00-\u9fff]{2,4}', combined)
                if zh_words:
                    word_freq = Counter(zh_words)
                    keywords = [w for w, _ in word_freq.most_common(3)]
            
            monthly_topics.append({
                "month": month,
                "top_keywords": keywords[:3],
                "conversation_count": len(set(conv.get("conversation_id") for conv in self.conversations if 
                    datetime.fromtimestamp(conv.get("create_time", 0)).strftime("%Y-%m") == month))
            })
        
        self.summary["monthly_focus"] = monthly_topics
    
    def analyze_politeness_score(self):
        """9. AI 礼貌指数"""
        polite_counts = {
            "please": 0,
            "thank_you": 0,
            "help": 0,
            "total_messages": 0
        }
        
        for conv in self.conversations:
            mapping = conv.get("mapping", {})
            for node_id, node in mapping.items():
                if node_id == "client-created-root":
                    continue
                message = node.get("message")
                if not message:
                    continue
                
                author = message.get("author", {})
                if author.get("role") != "user":
                    continue
                
                text = self.extract_text_from_message(message).lower()
                polite_counts["total_messages"] += 1
                
                # 英文
                if "please" in text:
                    polite_counts["please"] += 1
                if "thank you" in text or "thanks" in text:
                    polite_counts["thank_you"] += 1
                if "help" in text:
                    polite_counts["help"] += 1
                
                # 中文
                if "请" in text:
                    polite_counts["please"] += 1
                if "谢谢" in text or "感谢" in text:
                    polite_counts["thank_you"] += 1
                if "帮忙" in text or "帮" in text or "救命" in text:
                    polite_counts["help"] += 1
        
        total_polite = polite_counts["please"] + polite_counts["thank_you"] + polite_counts["help"]
        politeness_percentage = round(total_polite / polite_counts["total_messages"] * 100, 1) if polite_counts["total_messages"] > 0 else 0
        
        # 生成评价
        if politeness_percentage >= 50:
            evaluation = "你是个温文尔雅的绅士/淑女，对 AI 非常礼貌"
        elif politeness_percentage >= 20:
            evaluation = "你比较有礼貌，偶尔会使用礼貌用语"
        else:
            evaluation = "你是个雷厉风行的实干家，很少使用礼貌用语"
        
        self.summary["politeness_score"] = {
            "please_count": polite_counts["please"],
            "thank_you_count": polite_counts["thank_you"],
            "help_count": polite_counts["help"],
            "total_polite_usage": total_polite,
            "total_messages": polite_counts["total_messages"],
            "politeness_percentage": politeness_percentage,
            "evaluation": evaluation
        }
    
    def analyze_persona_badge(self):
        """10. 深夜哲学家/卷王认证"""
        # 基于热力图数据
        heatmap_data = self.summary.get("brain_activity_heatmap", {}).get("heatmap_data", [])
        
        late_night_count = sum(count for h, w, count in heatmap_data if 1 <= h <= 5)
        early_morning_count = sum(count for h, w, count in heatmap_data if 5 <= h < 8)
        weekend_count = sum(count for h, w, count in heatmap_data if w >= 5)  # 周六、周日
        
        total_count = sum(count for _, _, count in heatmap_data)
        
        badges = []
        
        if late_night_count > total_count * 0.2:
            badges.append({
                "name": "深夜哲学家",
                "description": f"你在凌晨 1-5 点有 {late_night_count} 次对话，是个深夜思考者"
            })
        
        if early_morning_count > total_count * 0.15:
            badges.append({
                "name": "晨间实干家",
                "description": f"你在清晨 5-8 点有 {early_morning_count} 次对话，是个早起的人"
            })
        
        if weekend_count > total_count * 0.3:
            badges.append({
                "name": "全勤卷王",
                "description": f"你在周末有 {weekend_count} 次对话，周末也在工作学习"
            })
        
        # 如果没有特殊标签，给一个默认的
        if not badges:
            badges.append({
                "name": "规律型用户",
                "description": "你的使用时间比较规律"
            })
        
        # 找出最活跃的深夜时刻
        late_night_sessions = [(h, w, count) for h, w, count in heatmap_data if 1 <= h <= 5]
        if late_night_sessions:
            max_session = max(late_night_sessions, key=lambda x: x[2])
            memorable_moment = {
                "hour": max_session[0],
                "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][max_session[1]],
                "count": max_session[2]
            }
        else:
            memorable_moment = None
        
        self.summary["persona_badge"] = {
            "badges": badges,
            "late_night_count": late_night_count,
            "early_morning_count": early_morning_count,
            "weekend_count": weekend_count,
            "memorable_moment": memorable_moment
        }
    
    def run_all_analyses(self):
        """运行所有分析"""
        print("开始分析对话数据...")
        
        print("  [1/10] 基础统计...")
        self.analyze_summary_stats()
        
        print("  [2/10] 大脑活跃热力图...")
        self.analyze_brain_activity_heatmap()
        
        print("  [3/10] 关键词提取...")
        self.analyze_keywords()
        
        print("  [4/10] 思维深潜度...")
        self.analyze_deep_dive_index()
        
        print("  [5/10] 输入输出比...")
        self.analyze_directors_ratio()
        
        print("  [6/10] 语言偏好...")
        self.analyze_linguistic_profile()
        
        print("  [7/10] 最长对话...")
        self.analyze_marathon_session()
        
        print("  [8/10] 月度专注主题...")
        self.analyze_monthly_focus()
        
        print("  [9/10] 礼貌指数...")
        self.analyze_politeness_score()
        
        print("  [10/10] 用户画像徽章...")
        self.analyze_persona_badge()
        
        print("分析完成！")
        return self.summary


def main():
    """主函数"""
    input_file = "conversation.json"
    output_file = "summary.json"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print(f"读取文件: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}")
        sys.exit(1)
    
    print(f"加载了 {len(conversations)} 个对话")
    
    # 运行分析
    analyzer = ConversationAnalyzer(conversations)
    summary = analyzer.run_all_analyses()
    
    # 添加元数据
    summary["metadata"] = {
        "generated_at": datetime.now().isoformat(),
        "total_conversations_analyzed": len(conversations),
        "version": "1.0"
    }
    
    # 保存结果
    print(f"保存结果到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析完成！结果已保存到 {output_file}")
    print(f"\n统计摘要:")
    print(f"  - 总对话数: {summary['summary_stats']['total_conversations']}")
    print(f"  - 总消息数: {summary['summary_stats']['total_messages']}")
    print(f"  - 用户输入: {summary['summary_stats']['total_user_characters']:,} 字符")
    print(f"  - AI 回复: {summary['summary_stats']['total_assistant_characters']:,} 字符")
    print(f"  - 输入输出比: {summary['directors_ratio']['ratio_display']}")


if __name__ == "__main__":
    main()

