from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import settings
import web_utils
import os
import secrets
import threading

app = Flask(__name__)


app.secret_key = secrets.token_hex(16)

def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@app.route('/js/<path:filename>')
def serve_js(filename):
    return app.send_static_file(os.path.join('js', filename))
@app.route('/css/<path:filename>')
def serve_css(filename):
    return app.send_static_file(os.path.join('css', filename))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == settings.WEB_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="密码错误")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def index():
    student_info, scores = web_utils.merge_data()
    
    global_stats = web_utils.get_stats(scores)
    
    
    last_refresh_time = web_utils.get_last_refresh_time()
    
    
    semesters = sorted(list(set([s['kksj'] for s in scores if s.get('kksj')])), reverse=True)
    
    
    scores.sort(key=lambda x: x.get('kksj', ''), reverse=True)
    
    return render_template('index.html', 
                           student=student_info, 
                           stats=global_stats, 
                           scores=scores, 
                           semesters=semesters,
                           refresh_time=last_refresh_time)

@app.route('/api/stats')
@login_required
def api_stats():
    """如果是前端筛选，可能需要后端重新计算不同范围的 GPA"""
    semester = request.args.get('semester')
    student_info, scores = web_utils.merge_data()
    
    if semester and semester != 'all':
        filtered_scores = [s for s in scores if s.get('kksj') == semester]
    else:
        filtered_scores = scores
        
    stats = web_utils.get_stats(filtered_scores)
    return jsonify(stats)

@app.route('/api/dashboard_data')
@login_required
def api_dashboard_data():
    student_info, scores = web_utils.merge_data()
    
    global_stats = web_utils.get_stats(scores)
    
    
    refresh_time = web_utils.get_last_refresh_time()
    
    
    semesters = sorted(list(set([s['kksj'] for s in scores if s.get('kksj')])), reverse=True)
    
    
    scores.sort(key=lambda x: x.get('kksj', ''), reverse=True)
    
    return jsonify({
        'student': student_info,
        'scores': scores,
        'globalStats': global_stats,
        'refreshTime': refresh_time,
        'semesters': semesters
    })

def run_server():
    web_utils.fetch_history_if_needed()
    app.run(host=settings.WEB_HOST, port=settings.WEB_PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_server()
