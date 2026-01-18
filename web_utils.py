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
    score_str = str(score_str).strip()
    
    level_map = {
        '优秀': 4.0,
        '良好': 3.6,
        '中等': 2.8,
        '及格': 1.7,
        '不及格': 0.0
    }
    
    
    if score_str in level_map:
        return level_map[score_str]
    
    
    try:
        score = float(score_str)
    except ValueError:
        return 0.0 
        
    if score < 60:
        return 0.0
    
    
    if score > 100:
        return 0.0
        
    
    gp = 4 - 3 * ((100 - score)**2) / 1600
    return round(gp, 1)

def convert_score_val(score_str):
    """
    将成绩转换为数值用于计算加权平均分
    """
    if not score_str:
        return 0
    score_str = str(score_str).strip()
    
    
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
    
    
    calc_credit_real = 0
    sum_gp_credit_real = 0
    sum_score_credit_real = 0
    real_total_credit = 0 
    
    
    calc_credit_est = 0
    sum_gp_credit_est = 0
    sum_score_credit_est = 0
    
    for s in scores:
        
        score_val = s.get('score')     
        avg_val = s.get('average')     
        course_type = s.get('type')    
        
        
        try:
            credit = float(s.get('credit', 0))
        except:
            credit = 0
          

        
        has_score = False
        if score_val and str(score_val).strip():
            has_score = True
            published_courses += 1
            real_total_credit += credit
        else:
            unpublished_courses += 1

        if credit <= 0.001:
            continue
            
        if not is_calculated_course(course_type):
            continue
            
        if has_score:
            my_gp = calculate_gp(score_val)
            my_score = convert_score_val(score_val)
            
            if my_score <= 100:
                calc_credit_real += credit
                sum_gp_credit_real += credit * my_gp
                sum_score_credit_real += credit * my_score

        if avg_val and str(avg_val).strip():
            grade_gp = calculate_gp(avg_val)       
            grade_score = convert_score_val(avg_val) 
            
            if grade_score <= 100:
                calc_credit_est += credit
                sum_gp_credit_est += credit * grade_gp
                sum_score_credit_est += credit * grade_score

    
    
    
    gpa = sum_gp_credit_real / calc_credit_real if calc_credit_real > 0 else 0
    avg = sum_score_credit_real / calc_credit_real if calc_credit_real > 0 else 0
    
    
    est_gpa = sum_gp_credit_est / calc_credit_est if calc_credit_est > 0 else 0
    est_avg = sum_score_credit_est / calc_credit_est if calc_credit_est > 0 else 0
    
    return {
        'total': total_courses,
        'published': published_courses,
        'unpublished': unpublished_courses,
        'gpa': round(gpa, 4),            
        'average': round(avg, 4),        
        'est_gpa': round(est_gpa, 4),    
        'est_average': round(est_avg, 4),
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
    
    seen = set()
    unique_scores = []
    for s in all_scores:
        
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
        import jwb 
        j = jwb.jwb() 
        all_scores = j.get_all_score()

        current_kksj = utils.get_current_kksj()
        
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
                for line in content.split('\n'):
                    if "时间" in line:
                         return line.split(':', 1)[1].strip()
        except:
            return "未知"
    return "未知"



