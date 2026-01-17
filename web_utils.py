import utils
import os
import json


def calculate_gp(score_str):
    """
    计算单科绩点
    支持：百分制数值、五级制中文
    """
    if not score_str:
        return 0.0
    
    # 处理可能的空白字符
    score_str = str(score_str).strip()
    
    # 五级制转换
    level_map = {
        '优秀': 4.0,
        '良好': 3.6,
        '中等': 2.8,
        '及格': 1.7,
        '不及格': 0.0
    }
    
    # 1. 尝试直接匹配等级
    if score_str in level_map:
        return level_map[score_str]
    
    # 2. 尝试转换为浮点数
    try:
        score = float(score_str)
    except ValueError:
        return 0.0 
        
    if score < 60:
        return 0.0
    
    # 如果分数大于100 (如CET4/6)，则绩点记为0，不参与计算
    if score > 100:
        return 0.0
        
    # 公式: 4 - 3 * (100 - X)^2 / 1600
    gp = 4 - 3 * ((100 - score)**2) / 1600
    return round(gp, 1)

def convert_score_val(score_str):
    """
    将成绩转换为数值用于计算加权平均分
    """
    if not score_str:
        return 0
    score_str = str(score_str).strip()
    
    # 处理等级制对应的默认分数
    level_val_map = {
        '优秀': 95,
        '良好': 85,
        '中等': 75,
        '及格': 65,
        '不及格': 0
    }
    if score_str in level_val_map:
        return level_val_map[score_str]
    
    try:
        val = float(score_str)
        return val
    except:
        return 0

def is_calculated_course(course_type):
    """筛选参与GPA计算的课程类型"""
    if not course_type:
        return False
    # 根据实际情况调整这些类型
    valid_types = ['公共基础课程', '体育课', '专业课', '基础教育', '专业教育课程', '通识教育课程']
    return course_type in valid_types

def get_stats(scores):
    """
    计算统计信息
    return: 
        gpa/average: 个人的实际绩点/均分
        est_gpa/est_average: 年级的平均绩点/均分 (基于课程 average 字段)
    """
    total_courses = len(scores)
    published_courses = 0
    unpublished_courses = 0
    
    # 1. 个人实际数据 (Real)
    calc_credit_real = 0
    sum_gp_credit_real = 0
    sum_score_credit_real = 0
    real_total_credit = 0 # 仅用于显示已修总学分
    
    # 2. 年级/预估数据 (Estimate / Grade Average)
    calc_credit_est = 0
    sum_gp_credit_est = 0
    sum_score_credit_est = 0
    
    for s in scores:
        # --- 基础数据提取 ---
        score_val = s.get('score')     # 个人分数
        avg_val = s.get('average')     # 年级平均分
        course_type = s.get('type')    # 课程类型
        
        # 获取学分
        try:
            credit = float(s.get('credit', 0))
        except:
            credit = 0
          

        # 判断是否已出成绩 (用于计数和显示总学分)
        has_score = False
        if score_val and str(score_val).strip():
            has_score = True
            published_courses += 1
            real_total_credit += credit
        else:
            unpublished_courses += 1

        # 学分太小忽略
        if credit <= 0.001:
            continue
            
        # --- 核心计算逻辑 ---
        
        # 只有特定类型的课程才参与 GPA/均分 计算
        if not is_calculated_course(course_type):
            continue
            
        # [逻辑A] 计算个人实际 GPA (仅当有个人成绩时)
        if has_score:
            my_gp = calculate_gp(score_val)
            my_score = convert_score_val(score_val)
            
            # 排除非百分制异常值 (如 > 100)
            if my_score <= 100:
                calc_credit_real += credit
                sum_gp_credit_real += credit * my_gp
                sum_score_credit_real += credit * my_score

        # [逻辑B] 计算年级预估 GPA (强制使用 average 字段)
        # 只要这门课有平均分数据，就计入年级均分统计 (无论我个人是否已出成绩)
        if avg_val and str(avg_val).strip():
            grade_gp = calculate_gp(avg_val)       # 用平均分算绩点
            grade_score = convert_score_val(avg_val) # 转数值
            
            if grade_score <= 100:
                calc_credit_est += credit
                sum_gp_credit_est += credit * grade_gp
                sum_score_credit_est += credit * grade_score

    # --- 汇总结果 ---
    
    # 个人实际
    gpa = sum_gp_credit_real / calc_credit_real if calc_credit_real > 0 else 0
    avg = sum_score_credit_real / calc_credit_real if calc_credit_real > 0 else 0
    
    # 年级/预估
    est_gpa = sum_gp_credit_est / calc_credit_est if calc_credit_est > 0 else 0
    est_avg = sum_score_credit_est / calc_credit_est if calc_credit_est > 0 else 0
    
    return {
        'total': total_courses,
        'published': published_courses,
        'unpublished': unpublished_courses,
        'gpa': round(gpa, 4),            # 个人GPA
        'average': round(avg, 4),        # 个人均分
        'est_gpa': round(est_gpa, 4),    # 年级平均GPA
        'est_average': round(est_avg, 4),# 年级平均分
        'real_total_credit': real_total_credit
    }


DATA_FILE = "data/data.json"   
HISTORY_FILE = "data/history.json"

def merge_data():
    """合并历史数据和当前数据"""
    history_scores = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history_scores = json.load(f)
        except:
            history_scores = []
            
    current_data = {}
    current_scores = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                current_scores = current_data.get('score', [])
        except:
            pass
    
    all_scores = history_scores + current_scores
    # 简单去重 (根据 课程名+开课时间)
    seen = set()
    unique_scores = []
    for s in all_scores:
        # 作为一个健壮性处理，处理可能的 None
        c_name = s.get('course', '')
        k_time = s.get('kksj', '')
        key = (c_name, k_time)
        
        if key not in seen:
            seen.add(key)
            unique_scores.append(s)
            
    return current_data.get('student', {}), unique_scores


def fetch_history_if_needed():
    """
    检查是否有历史数据，如果没有则获取。
    """
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 5:
        return
        
    print("Web模块: 正在初始化历史成绩缓存...")
    try:
        import jwb # 延迟导入，避免循环引用
        j = jwb.jwb() # 这里会登录
        all_scores = j.get_all_score()
        
        # 这里的 get_current_kksj 需要存在
        current_kksj = utils.get_current_kksj()
        
        # 筛选非当前学期的作为历史成绩
        history_only = [s for s in all_scores if s.get('kksj') != current_kksj]
        
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_only, f, ensure_ascii=False, indent=4)
        print("Web模块: 历史成绩缓存完成")
    except Exception as e:
        print(f"Web模块: 获取历史成绩失败: {e}")

def get_last_refresh_time():
    """读取上次刷新时间"""
    log_file = "data/log.txt"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 假设格式: "更新时间:2023-01-01 12:00:00" 或 "最后检查时间:..."
                # 这里简单提取第一行或寻找特定关键词
                for line in content.split('\n'):
                    if "时间" in line:
                         return line.split(':', 1)[1].strip()
        except:
            return "未知"
    return "未知"



