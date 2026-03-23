from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
import os, json

app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(basedir, 'data')
os.makedirs(datadir, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(datadir, 'secondbrain.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ── Models ──────────────────────────────────────────────────────────────────

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    category = db.Column(db.String(50))
    amount = db.Column(db.Float)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, default=date.today)
    account = db.Column(db.String(50))

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(20))
    balance = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default='EUR')
    color = db.Column(db.String(7), default='#e8a849')

class SurahProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surah_number = db.Column(db.Integer, unique=True)
    surah_name = db.Column(db.String(50))
    surah_name_ar = db.Column(db.String(50))
    total_ayahs = db.Column(db.Integer)
    ayahs_read = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    memorized = db.Column(db.Boolean, default=False)
    juz = db.Column(db.Integer)
    last_read = db.Column(db.Date)

class ReadingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    surah_number = db.Column(db.Integer)
    surah_name = db.Column(db.String(50))
    from_ayah = db.Column(db.Integer)
    to_ayah = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    type = db.Column(db.String(20))
    notes = db.Column(db.Text)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    progress = db.Column(db.Integer, default=0)
    deadline = db.Column(db.Date)
    color = db.Column(db.String(7), default='#e8a849')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'))
    title = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)

# ── Learning Plan Models ────────────────────────────────────────────────────

class LearningPhase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#1a5276')

class LearningWeek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phase_id = db.Column(db.Integer, db.ForeignKey('learning_phase.id'))
    week_number = db.Column(db.Integer)
    title = db.Column(db.String(100))
    goal = db.Column(db.Text)

class LearningTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('learning_week.id'))
    category = db.Column(db.String(20))
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, default='')
    completed_at = db.Column(db.DateTime)

class DailyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), unique=True)
    notes = db.Column(db.Text, default='')
    energy_level = db.Column(db.Integer, default=3)

class DailyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    daily_plan_id = db.Column(db.Integer, db.ForeignKey('daily_plan.id'))
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    time_slot = db.Column(db.String(10), default='')
    sort_order = db.Column(db.Integer, default=0)

# ── Fitness Models ──────────────────────────────────────────────────────────

class FitnessProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, default=0)
    height = db.Column(db.Float, default=0)
    age = db.Column(db.Integer, default=0)
    sex = db.Column(db.String(10), default='male')
    activity = db.Column(db.String(20), default='moderate')
    phase = db.Column(db.Integer, default=0)

class FitnessSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_key = db.Column(db.String(20))
    session_index = db.Column(db.Integer)
    done = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, default='')

class WeightEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    kg = db.Column(db.Float)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    status = db.Column(db.String(20), default='applied')
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    location = db.Column(db.String(100))
    url = db.Column(db.String(300))
    contact = db.Column(db.String(100))
    notes = db.Column(db.Text)
    date_applied = db.Column(db.Date, default=date.today)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(200), default='')
    quarter = db.Column(db.Integer, default=1)
    category = db.Column(db.String(50), default='security')
    status = db.Column(db.String(20), default='to_read')
    notes = db.Column(db.Text, default='')
    rating = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ── Helpers ─────────────────────────────────────────────────────────────────

def to_dict(obj, fields):
    d = {}
    for f in fields:
        v = getattr(obj, f)
        if isinstance(v, (date, datetime)):
            v = v.isoformat()
        d[f] = v
    return d

TX_FIELDS = ['id','type','category','amount','description','date','account']
ACCT_FIELDS = ['id','name','type','balance','currency','color']
SURAH_FIELDS = ['id','surah_number','surah_name','surah_name_ar','total_ayahs','ayahs_read','completed','memorized','juz','last_read']
LOG_FIELDS = ['id','date','surah_number','surah_name','from_ayah','to_ayah','duration','type','notes']
PROJ_FIELDS = ['id','name','description','status','progress','deadline','color','created_at']
TASK_FIELDS = ['id','project_id','title','completed']
JOB_FIELDS = ['id','company','position','status','salary_min','salary_max','location','url','contact','notes','date_applied','last_updated']
LPHASE_FIELDS = ['id','name','description','color']
LWEEK_FIELDS = ['id','phase_id','week_number','title','goal']
LTASK_FIELDS = ['id','week_id','category','description','completed','notes','completed_at']
DAILY_PLAN_FIELDS = ['id','date','notes','energy_level']
DAILY_TASK_FIELDS = ['id','daily_plan_id','description','completed','time_slot','sort_order']
BOOK_FIELDS = ['id','title','author','quarter','category','status','notes','rating','sort_order','created_at']

# ── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

# Dashboard
@app.route('/api/dashboard')
def dashboard():
    total_income = sum(t.amount for t in Transaction.query.filter_by(type='income').all())
    total_expense = sum(t.amount for t in Transaction.query.filter_by(type='expense').all())
    total_savings = sum(a.balance for a in Account.query.filter_by(type='savings').all())
    total_investments = sum(a.balance for a in Account.query.filter_by(type='investment').all())
    accounts = Account.query.all()
    net_worth = sum(a.balance for a in accounts)
    surahs = SurahProgress.query.all()
    surahs_completed = sum(1 for s in surahs if s.completed)
    surahs_memorized = sum(1 for s in surahs if s.memorized)
    projects_active = Project.query.filter_by(status='active').count()
    projects_completed = Project.query.filter_by(status='completed').count()
    jobs_total = JobApplication.query.count()
    jobs_active = JobApplication.query.filter(JobApplication.status.notin_(['rejected','accepted'])).count()
    jobs_offers = JobApplication.query.filter_by(status='offer').count()
    recent_tx = [to_dict(t, TX_FIELDS) for t in Transaction.query.order_by(Transaction.date.desc()).limit(5).all()]
    learning_total = LearningTask.query.count()
    learning_done = LearningTask.query.filter_by(completed=True).count()
    return jsonify({
        'finance': {'income': total_income, 'expenses': total_expense, 'savings': total_savings,
                     'investments': total_investments, 'net_worth': net_worth},
        'quran': {'total': len(surahs), 'completed': surahs_completed, 'memorized': surahs_memorized},
        'projects': {'active': projects_active, 'completed': projects_completed},
        'jobs': {'total': jobs_total, 'active': jobs_active, 'offers': jobs_offers},
        'learning': {'total': learning_total, 'done': learning_done},
        'recent_transactions': recent_tx
    })

# ── Transactions CRUD ───────────────────────────────────────────────────────

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    txs = Transaction.query.order_by(Transaction.date.desc()).all()
    return jsonify([to_dict(t, TX_FIELDS) for t in txs])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    d = request.json
    t = Transaction(type=d['type'], category=d.get('category',''), amount=float(d['amount']),
                    description=d.get('description',''), date=date.fromisoformat(d['date']) if d.get('date') else date.today(),
                    account=d.get('account',''))
    db.session.add(t)
    # Update account balance
    if d.get('account'):
        acct = Account.query.filter_by(name=d['account']).first()
        if acct:
            if d['type'] == 'income':
                acct.balance += float(d['amount'])
            elif d['type'] == 'expense':
                acct.balance -= float(d['amount'])
    db.session.commit()
    return jsonify(to_dict(t, TX_FIELDS)), 201

@app.route('/api/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    t = Transaction.query.get_or_404(id)
    d = request.json
    for k in ['type','category','amount','description','account']:
        if k in d:
            setattr(t, k, float(d[k]) if k == 'amount' else d[k])
    if 'date' in d:
        t.date = date.fromisoformat(d['date'])
    db.session.commit()
    return jsonify(to_dict(t, TX_FIELDS))

@app.route('/api/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    t = Transaction.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return '', 204

# ── Accounts CRUD ───────────────────────────────────────────────────────────

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify([to_dict(a, ACCT_FIELDS) for a in Account.query.all()])

@app.route('/api/accounts', methods=['POST'])
def add_account():
    d = request.json
    a = Account(name=d['name'], type=d['type'], balance=float(d.get('balance',0)),
                currency=d.get('currency','EUR'), color=d.get('color','#e8a849'))
    db.session.add(a)
    db.session.commit()
    return jsonify(to_dict(a, ACCT_FIELDS)), 201

@app.route('/api/accounts/<int:id>', methods=['PUT'])
def update_account(id):
    a = Account.query.get_or_404(id)
    d = request.json
    for k in ['name','type','currency','color']:
        if k in d: setattr(a, k, d[k])
    if 'balance' in d: a.balance = float(d['balance'])
    db.session.commit()
    return jsonify(to_dict(a, ACCT_FIELDS))

@app.route('/api/accounts/<int:id>', methods=['DELETE'])
def delete_account(id):
    a = Account.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    return '', 204

# ── Financial Stats ─────────────────────────────────────────────────────────

@app.route('/api/finance/stats')
def finance_stats():
    txs = Transaction.query.all()
    by_cat = {}
    monthly = {}
    for t in txs:
        if t.type == 'expense':
            by_cat[t.category] = by_cat.get(t.category, 0) + t.amount
        key = t.date.strftime('%Y-%m') if t.date else 'unknown'
        if key not in monthly:
            monthly[key] = {'income': 0, 'expense': 0}
        if t.type == 'income':
            monthly[key]['income'] += t.amount
        elif t.type == 'expense':
            monthly[key]['expense'] += t.amount
    sorted_months = sorted(monthly.keys())
    return jsonify({
        'by_category': by_cat,
        'monthly': {
            'labels': sorted_months,
            'income': [monthly[m]['income'] for m in sorted_months],
            'expenses': [monthly[m]['expense'] for m in sorted_months]
        }
    })

# ── Quran CRUD ──────────────────────────────────────────────────────────────

@app.route('/api/quran/surahs', methods=['GET'])
def get_surahs():
    return jsonify([to_dict(s, SURAH_FIELDS) for s in SurahProgress.query.order_by(SurahProgress.surah_number).all()])

@app.route('/api/quran/surahs/<int:num>', methods=['PUT'])
def update_surah(num):
    s = SurahProgress.query.filter_by(surah_number=num).first_or_404()
    d = request.json
    for k in ['ayahs_read','completed','memorized']:
        if k in d:
            setattr(s, k, d[k])
    if 'ayahs_read' in d and int(d['ayahs_read']) >= s.total_ayahs:
        s.completed = True
        s.ayahs_read = s.total_ayahs
    s.last_read = date.today()
    db.session.commit()
    return jsonify(to_dict(s, SURAH_FIELDS))

@app.route('/api/quran/log', methods=['GET'])
def get_reading_log():
    logs = ReadingLog.query.order_by(ReadingLog.date.desc()).all()
    return jsonify([to_dict(l, LOG_FIELDS) for l in logs])

@app.route('/api/quran/log', methods=['POST'])
def add_reading_log():
    d = request.json
    l = ReadingLog(date=date.fromisoformat(d['date']) if d.get('date') else date.today(),
                   surah_number=int(d['surah_number']), surah_name=d.get('surah_name',''),
                   from_ayah=int(d.get('from_ayah',1)), to_ayah=int(d.get('to_ayah',1)),
                   duration=int(d.get('duration',0)), type=d.get('type','reading'),
                   notes=d.get('notes',''))
    db.session.add(l)
    # Update surah progress
    s = SurahProgress.query.filter_by(surah_number=int(d['surah_number'])).first()
    if s:
        s.ayahs_read = max(s.ayahs_read, int(d.get('to_ayah', s.ayahs_read)))
        if s.ayahs_read >= s.total_ayahs:
            s.completed = True
        s.last_read = date.today()
    db.session.commit()
    return jsonify(to_dict(l, LOG_FIELDS)), 201

@app.route('/api/quran/log/<int:id>', methods=['DELETE'])
def delete_reading_log(id):
    l = ReadingLog.query.get_or_404(id)
    db.session.delete(l)
    db.session.commit()
    return '', 204

# ── Projects CRUD ───────────────────────────────────────────────────────────

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    result = []
    for p in projects:
        pd = to_dict(p, PROJ_FIELDS)
        tasks = ProjectTask.query.filter_by(project_id=p.id).all()
        pd['tasks'] = [to_dict(t, TASK_FIELDS) for t in tasks]
        if tasks:
            pd['progress'] = int(sum(1 for t in tasks if t.completed) / len(tasks) * 100)
        result.append(pd)
    return jsonify(result)

@app.route('/api/projects', methods=['POST'])
def add_project():
    d = request.json
    p = Project(name=d['name'], description=d.get('description',''), status=d.get('status','active'),
                color=d.get('color','#e8a849'),
                deadline=date.fromisoformat(d['deadline']) if d.get('deadline') else None)
    db.session.add(p)
    db.session.commit()
    return jsonify(to_dict(p, PROJ_FIELDS)), 201

@app.route('/api/projects/<int:id>', methods=['PUT'])
def update_project(id):
    p = Project.query.get_or_404(id)
    d = request.json
    for k in ['name','description','status','progress','color']:
        if k in d: setattr(p, k, d[k])
    if 'deadline' in d and d['deadline']:
        p.deadline = date.fromisoformat(d['deadline'])
    db.session.commit()
    return jsonify(to_dict(p, PROJ_FIELDS))

@app.route('/api/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    ProjectTask.query.filter_by(project_id=id).delete()
    p = Project.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return '', 204

@app.route('/api/projects/<int:id>/tasks', methods=['POST'])
def add_task(id):
    d = request.json
    t = ProjectTask(project_id=id, title=d['title'])
    db.session.add(t)
    db.session.commit()
    return jsonify(to_dict(t, TASK_FIELDS)), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    t = ProjectTask.query.get_or_404(id)
    d = request.json
    if 'completed' in d: t.completed = d['completed']
    if 'title' in d: t.title = d['title']
    db.session.commit()
    return jsonify(to_dict(t, TASK_FIELDS))

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    t = ProjectTask.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return '', 204

# ── Jobs CRUD ───────────────────────────────────────────────────────────────

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify([to_dict(j, JOB_FIELDS) for j in JobApplication.query.order_by(JobApplication.date_applied.desc()).all()])

@app.route('/api/jobs', methods=['POST'])
def add_job():
    d = request.json
    j = JobApplication(company=d['company'], position=d['position'], status=d.get('status','applied'),
                        salary_min=float(d['salary_min']) if d.get('salary_min') else None,
                        salary_max=float(d['salary_max']) if d.get('salary_max') else None,
                        location=d.get('location',''), url=d.get('url',''), contact=d.get('contact',''),
                        notes=d.get('notes',''),
                        date_applied=date.fromisoformat(d['date_applied']) if d.get('date_applied') else date.today())
    db.session.add(j)
    db.session.commit()
    return jsonify(to_dict(j, JOB_FIELDS)), 201

@app.route('/api/jobs/<int:id>', methods=['PUT'])
def update_job(id):
    j = JobApplication.query.get_or_404(id)
    d = request.json
    for k in ['company','position','status','location','url','contact','notes']:
        if k in d: setattr(j, k, d[k])
    for k in ['salary_min','salary_max']:
        if k in d and d[k]: setattr(j, k, float(d[k]))
    if 'date_applied' in d and d['date_applied']:
        j.date_applied = date.fromisoformat(d['date_applied'])
    j.last_updated = datetime.utcnow()
    db.session.commit()
    return jsonify(to_dict(j, JOB_FIELDS))

@app.route('/api/jobs/<int:id>', methods=['DELETE'])
def delete_job(id):
    j = JobApplication.query.get_or_404(id)
    db.session.delete(j)
    db.session.commit()
    return '', 204

# ── Fitness Routes ─────────────────────────────────────────────────────────

@app.route('/api/fitness/profile', methods=['GET'])
def get_fitness_profile():
    p = FitnessProfile.query.first()
    if not p:
        p = FitnessProfile()
        db.session.add(p)
        db.session.commit()
    return jsonify({'weight': p.weight, 'height': p.height, 'age': p.age, 'sex': p.sex, 'activity': p.activity, 'phase': p.phase})

@app.route('/api/fitness/profile', methods=['PUT'])
def update_fitness_profile():
    p = FitnessProfile.query.first()
    if not p:
        p = FitnessProfile()
        db.session.add(p)
    d = request.json
    for k in ['weight', 'height', 'age', 'sex', 'activity', 'phase']:
        if k in d:
            val = d[k]
            if k in ('weight', 'height'):
                val = float(val) if val else 0
            elif k == 'age':
                val = int(val) if val else 0
            elif k == 'phase':
                val = int(val)
            setattr(p, k, val)
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/fitness/sessions/<week_key>', methods=['GET'])
def get_fitness_sessions(week_key):
    sessions = FitnessSession.query.filter_by(week_key=week_key).all()
    result = {}
    for s in sessions:
        result[str(s.session_index)] = {'done': s.done, 'note': s.note or ''}
    return jsonify(result)

@app.route('/api/fitness/sessions/<week_key>/<int:idx>', methods=['POST'])
def toggle_fitness_session(week_key, idx):
    d = request.json
    s = FitnessSession.query.filter_by(week_key=week_key, session_index=idx).first()
    if not s:
        s = FitnessSession(week_key=week_key, session_index=idx)
        db.session.add(s)
    if 'done' in d:
        s.done = d['done']
    if 'note' in d:
        s.note = d['note']
    db.session.commit()
    return jsonify({'done': s.done, 'note': s.note})

@app.route('/api/fitness/weight', methods=['GET'])
def get_weight_log():
    entries = WeightEntry.query.order_by(WeightEntry.date).all()
    return jsonify([{'date': e.date.isoformat(), 'kg': e.kg} for e in entries])

@app.route('/api/fitness/weight', methods=['POST'])
def add_weight_entry():
    d = request.json
    e = WeightEntry(kg=float(d['kg']), date=date.fromisoformat(d['date']) if d.get('date') else date.today())
    db.session.add(e)
    db.session.commit()
    return jsonify({'id': e.id, 'date': e.date.isoformat(), 'kg': e.kg}), 201

@app.route('/api/fitness/weight/<int:wid>', methods=['DELETE'])
def delete_weight_entry(wid):
    e = WeightEntry.query.get_or_404(wid)
    db.session.delete(e)
    db.session.commit()
    return '', 204

@app.route('/api/fitness/stats')
def fitness_stats():
    p = FitnessProfile.query.first()
    entries = WeightEntry.query.order_by(WeightEntry.date).all()
    last_weight = entries[-1].kg if entries else None
    return jsonify({'last_weight': last_weight, 'total_entries': len(entries), 'phase': p.phase if p else 0})

# ── Learning Plan Routes ───────────────────────────────────────────────────

@app.route('/api/learning/roadmap')
def get_learning_roadmap():
    phases = LearningPhase.query.order_by(LearningPhase.id).all()
    result = []
    for p in phases:
        pd = to_dict(p, LPHASE_FIELDS)
        weeks = LearningWeek.query.filter_by(phase_id=p.id).order_by(LearningWeek.week_number).all()
        pd['weeks'] = []
        for w in weeks:
            wd = to_dict(w, LWEEK_FIELDS)
            wd['tasks'] = [to_dict(t, LTASK_FIELDS) for t in LearningTask.query.filter_by(week_id=w.id).order_by(LearningTask.category.desc(), LearningTask.id).all()]
            pd['weeks'].append(wd)
        result.append(pd)
    return jsonify(result)

@app.route('/api/learning/stats')
def get_learning_stats():
    total = LearningTask.query.count()
    done = LearningTask.query.filter_by(completed=True).count()
    phases = LearningPhase.query.all()
    by_phase = []
    for p in phases:
        week_ids = [w.id for w in LearningWeek.query.filter_by(phase_id=p.id).all()]
        if week_ids:
            pt = LearningTask.query.filter(LearningTask.week_id.in_(week_ids)).count()
            pd = LearningTask.query.filter(LearningTask.week_id.in_(week_ids), LearningTask.completed==True).count()
            by_phase.append({'name': p.name, 'color': p.color, 'total': pt, 'done': pd})
    by_week = []
    for w in LearningWeek.query.order_by(LearningWeek.week_number).all():
        wt = LearningTask.query.filter_by(week_id=w.id).count()
        wd = LearningTask.query.filter_by(week_id=w.id, completed=True).count()
        by_week.append({'week_number': w.week_number, 'title': w.title, 'total': wt, 'done': wd})
    return jsonify({'total': total, 'done': done, 'by_phase': by_phase, 'by_week': by_week})

@app.route('/api/learning/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_learning_task(task_id):
    t = LearningTask.query.get_or_404(task_id)
    t.completed = not t.completed
    t.completed_at = datetime.utcnow() if t.completed else None
    db.session.commit()
    return jsonify({'completed': t.completed})

@app.route('/api/learning/tasks/<int:task_id>', methods=['PUT'])
def update_learning_task(task_id):
    t = LearningTask.query.get_or_404(task_id)
    d = request.json
    for k in ['description', 'notes', 'category']:
        if k in d: setattr(t, k, d[k])
    db.session.commit()
    return jsonify(to_dict(t, LTASK_FIELDS))

@app.route('/api/learning/tasks', methods=['POST'])
def add_learning_task():
    d = request.json
    t = LearningTask(week_id=d['week_id'], category=d.get('category', 'weekday'), description=d['description'], notes=d.get('notes', ''))
    db.session.add(t)
    db.session.commit()
    return jsonify(to_dict(t, LTASK_FIELDS)), 201

@app.route('/api/learning/tasks/<int:task_id>', methods=['DELETE'])
def delete_learning_task(task_id):
    t = LearningTask.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    return '', 204

# ── Daily Planner Routes ──────────────────────────────────────────────────

@app.route('/api/learning/daily/<dt>')
def get_daily_plan(dt):
    plan = DailyPlan.query.filter_by(date=dt).first()
    if not plan:
        plan = DailyPlan(date=dt)
        db.session.add(plan)
        db.session.commit()
    pd = to_dict(plan, DAILY_PLAN_FIELDS)
    pd['tasks'] = [to_dict(t, DAILY_TASK_FIELDS) for t in DailyTask.query.filter_by(daily_plan_id=plan.id).order_by(DailyTask.sort_order, DailyTask.id).all()]
    return jsonify(pd)

@app.route('/api/learning/daily/<dt>', methods=['PUT'])
def update_daily_plan(dt):
    plan = DailyPlan.query.filter_by(date=dt).first()
    if not plan:
        plan = DailyPlan(date=dt)
        db.session.add(plan)
        db.session.commit()
    d = request.json
    if 'notes' in d: plan.notes = d['notes']
    if 'energy_level' in d: plan.energy_level = d['energy_level']
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/learning/daily/<dt>/tasks', methods=['POST'])
def add_daily_task(dt):
    plan = DailyPlan.query.filter_by(date=dt).first()
    if not plan:
        plan = DailyPlan(date=dt)
        db.session.add(plan)
        db.session.commit()
    d = request.json
    t = DailyTask(daily_plan_id=plan.id, description=d['description'], time_slot=d.get('time_slot', ''))
    db.session.add(t)
    db.session.commit()
    return jsonify(to_dict(t, DAILY_TASK_FIELDS)), 201

@app.route('/api/learning/daily/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_daily_task(task_id):
    t = DailyTask.query.get_or_404(task_id)
    t.completed = not t.completed
    db.session.commit()
    return jsonify({'completed': t.completed})

@app.route('/api/learning/daily/tasks/<int:task_id>', methods=['DELETE'])
def delete_daily_task(task_id):
    t = DailyTask.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    return '', 204

# ── Learning Plan Reset ────────────────────────────────────────────────────

@app.route('/api/learning/reset', methods=['POST'])
def reset_learning_progress():
    LearningTask.query.update({LearningTask.completed: False, LearningTask.completed_at: None})
    DailyTask.query.delete()
    DailyPlan.query.delete()
    db.session.commit()
    return jsonify({'ok': True})

# ── Books / Reading List ───────────────────────────────────────────────────

@app.route('/api/books')
def get_books():
    books = Book.query.order_by(Book.quarter, Book.sort_order, Book.id).all()
    return jsonify([to_dict(b, BOOK_FIELDS) for b in books])

@app.route('/api/books', methods=['POST'])
def add_book():
    d = request.json
    b = Book(title=d['title'], author=d.get('author',''), quarter=d.get('quarter',1),
             category=d.get('category','security'), status=d.get('status','to_read'),
             notes=d.get('notes',''), rating=d.get('rating',0))
    db.session.add(b)
    db.session.commit()
    return jsonify({'id': b.id})

@app.route('/api/books/<int:bid>', methods=['PUT'])
def update_book(bid):
    b = Book.query.get_or_404(bid)
    d = request.json
    for k in ('title','author','quarter','category','status','notes','rating','sort_order'):
        if k in d:
            setattr(b, k, d[k])
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/books/<int:bid>', methods=['DELETE'])
def delete_book(bid):
    b = Book.query.get_or_404(bid)
    db.session.delete(b)
    db.session.commit()
    return '', 204

# ── Seed Quran Data ─────────────────────────────────────────────────────────

SURAHS = [
    (1,"Al-Fatiha","الفاتحة",7,1),(2,"Al-Baqarah","البقرة",286,1),(3,"Ali 'Imran","آل عمران",200,3),
    (4,"An-Nisa","النساء",176,4),(5,"Al-Ma'idah","المائدة",120,6),(6,"Al-An'am","الأنعام",165,7),
    (7,"Al-A'raf","الأعراف",206,8),(8,"Al-Anfal","الأنفال",75,9),(9,"At-Tawbah","التوبة",129,10),
    (10,"Yunus","يونس",109,11),(11,"Hud","هود",123,11),(12,"Yusuf","يوسف",111,12),
    (13,"Ar-Ra'd","الرعد",43,13),(14,"Ibrahim","إبراهيم",52,13),(15,"Al-Hijr","الحجر",99,14),
    (16,"An-Nahl","النحل",128,14),(17,"Al-Isra","الإسراء",111,15),(18,"Al-Kahf","الكهف",110,15),
    (19,"Maryam","مريم",98,16),(20,"Ta-Ha","طه",135,16),(21,"Al-Anbiya","الأنبياء",112,17),
    (22,"Al-Hajj","الحج",78,17),(23,"Al-Mu'minun","المؤمنون",118,18),(24,"An-Nur","النور",64,18),
    (25,"Al-Furqan","الفرقان",77,18),(26,"Ash-Shu'ara","الشعراء",227,19),(27,"An-Naml","النمل",93,19),
    (28,"Al-Qasas","القصص",88,20),(29,"Al-Ankabut","العنكبوت",69,20),(30,"Ar-Rum","الروم",60,21),
    (31,"Luqman","لقمان",34,21),(32,"As-Sajdah","السجدة",30,21),(33,"Al-Ahzab","الأحزاب",73,21),
    (34,"Saba","سبأ",54,22),(35,"Fatir","فاطر",45,22),(36,"Ya-Sin","يس",83,22),
    (37,"As-Saffat","الصافات",182,23),(38,"Sad","ص",88,23),(39,"Az-Zumar","الزمر",75,23),
    (40,"Ghafir","غافر",85,24),(41,"Fussilat","فصلت",54,24),(42,"Ash-Shura","الشورى",53,25),
    (43,"Az-Zukhruf","الزخرف",89,25),(44,"Ad-Dukhan","الدخان",59,25),(45,"Al-Jathiyah","الجاثية",37,25),
    (46,"Al-Ahqaf","الأحقاف",35,26),(47,"Muhammad","محمد",38,26),(48,"Al-Fath","الفتح",29,26),
    (49,"Al-Hujurat","الحجرات",18,26),(50,"Qaf","ق",45,26),(51,"Adh-Dhariyat","الذاريات",60,26),
    (52,"At-Tur","الطور",49,27),(53,"An-Najm","النجم",62,27),(54,"Al-Qamar","القمر",55,27),
    (55,"Ar-Rahman","الرحمن",78,27),(56,"Al-Waqi'ah","الواقعة",96,27),(57,"Al-Hadid","الحديد",29,27),
    (58,"Al-Mujadila","المجادلة",22,28),(59,"Al-Hashr","الحشر",24,28),(60,"Al-Mumtahina","الممتحنة",13,28),
    (61,"As-Saf","الصف",14,28),(62,"Al-Jumu'ah","الجمعة",11,28),(63,"Al-Munafiqun","المنافقون",11,28),
    (64,"At-Taghabun","التغابن",18,28),(65,"At-Talaq","الطلاق",12,28),(66,"At-Tahrim","التحريم",12,28),
    (67,"Al-Mulk","الملك",30,29),(68,"Al-Qalam","القلم",52,29),(69,"Al-Haqqah","الحاقة",52,29),
    (70,"Al-Ma'arij","المعارج",44,29),(71,"Nuh","نوح",28,29),(72,"Al-Jinn","الجن",28,29),
    (73,"Al-Muzzammil","المزمل",20,29),(74,"Al-Muddaththir","المدثر",56,29),(75,"Al-Qiyamah","القيامة",40,29),
    (76,"Al-Insan","الإنسان",31,29),(77,"Al-Mursalat","المرسلات",50,29),(78,"An-Naba","النبأ",40,30),
    (79,"An-Nazi'at","النازعات",46,30),(80,"Abasa","عبس",42,30),(81,"At-Takwir","التكوير",29,30),
    (82,"Al-Infitar","الإنفطار",19,30),(83,"Al-Mutaffifin","المطففين",36,30),(84,"Al-Inshiqaq","الإنشقاق",25,30),
    (85,"Al-Buruj","البروج",22,30),(86,"At-Tariq","الطارق",17,30),(87,"Al-A'la","الأعلى",19,30),
    (88,"Al-Ghashiyah","الغاشية",26,30),(89,"Al-Fajr","الفجر",30,30),(90,"Al-Balad","البلد",20,30),
    (91,"Ash-Shams","الشمس",15,30),(92,"Al-Layl","الليل",21,30),(93,"Ad-Duha","الضحى",11,30),
    (94,"Ash-Sharh","الشرح",8,30),(95,"At-Tin","التين",8,30),(96,"Al-Alaq","العلق",19,30),
    (97,"Al-Qadr","القدر",5,30),(98,"Al-Bayyinah","البينة",8,30),(99,"Az-Zalzalah","الزلزلة",8,30),
    (100,"Al-Adiyat","العاديات",11,30),(101,"Al-Qari'ah","القارعة",11,30),(102,"At-Takathur","التكاثر",8,30),
    (103,"Al-Asr","العصر",3,30),(104,"Al-Humazah","الهمزة",9,30),(105,"Al-Fil","الفيل",5,30),
    (106,"Quraysh","قريش",4,30),(107,"Al-Ma'un","الماعون",7,30),(108,"Al-Kawthar","الكوثر",3,30),
    (109,"Al-Kafirun","الكافرون",6,30),(110,"An-Nasr","النصر",3,30),(111,"Al-Masad","المسد",5,30),
    (112,"Al-Ikhlas","الإخلاص",4,30),(113,"Al-Falaq","الفلق",5,30),(114,"An-Nas","الناس",6,30),
]

def seed_quran():
    if SurahProgress.query.count() == 0:
        for num, name, name_ar, ayahs, juz in SURAHS:
            db.session.add(SurahProgress(surah_number=num, surah_name=name, surah_name_ar=name_ar,
                                          total_ayahs=ayahs, juz=juz))
        db.session.commit()

def seed_learning_plan():
    if LearningPhase.query.count() > 0:
        return
    phases = [
        (1, 'Q1: Foundation & CPTS', 'Jan-Mar 2026 | Pentest Foundations + CPTS Certification', '#1a5276'),
        (2, 'Q2: AI Security Core', 'Apr-Jun 2026 | AI/ML Security Deep Dive', '#2e86c1'),
        (3, 'Q3: Research & Build', 'Jul-Sep 2026 | Research + Projects + Output', '#148f77'),
        (4, 'Q4: Launch & Apply', 'Oct-Dec 2026 | Career Launch + PhD Prep', '#8e44ad'),
    ]
    for pid, name, desc, color in phases:
        db.session.add(LearningPhase(id=pid, name=name, description=desc, color=color))
    db.session.flush()

    weeks_data = [
        (1,1,1,'CPTS Kickoff','Resume CPTS, target 2 modules, ~45%'),
        (2,1,2,'CPTS Push','4 modules done, ~50%'),
        (3,1,3,'CPTS Deep Work','6 modules, first writeup published, ~58%'),
        (4,1,4,'CPTS 70%','Hit 70% milestone'),
        (5,1,5,'CPTS Advanced','Tackle harder modules, ~78%'),
        (6,1,6,'CPTS 85%','Push to 85%, HTB practice'),
        (7,1,7,'CPTS Sprint','Final modules, ~92%'),
        (8,1,8,'CPTS Completion','100% course + practice exam'),
        (9,1,9,'Exam Prep W1','Review weak areas, mock scenarios'),
        (10,1,10,'Exam Prep W2','Full mock exams, time management'),
        (11,1,11,'CPTS Exam Week','Take the CPTS exam'),
        (12,1,12,'Python & Cloud Foundations','Python scripting + AWS basics'),
        (13,1,13,'Q1 Review','Consolidate, document, plan Q2'),
        (14,2,14,'LLM Attack Surface','OWASP LLM Top 10, prompt injection basics'),
        (15,2,15,'Prompt Injection Deep Dive','Direct/indirect injection, jailbreaks'),
        (16,2,16,'Model-Level Threats','Adversarial examples, evasion attacks'),
        (17,2,17,'Data Poisoning & Backdoors','Training data attacks, supply chain'),
        (18,2,18,'AI Infrastructure Security','MLOps, model deployment, API security'),
        (19,2,19,'Cloud AI Security','AWS SageMaker, Azure ML security'),
        (20,2,20,'Privacy Attacks on ML','Model inversion, membership inference'),
        (21,2,21,'Red Teaming AI Systems','Structured AI red teaming methodology'),
        (22,2,22,'AI Security Tools','ART, Garak, PyRIT hands-on'),
        (23,2,23,'Research Reading Sprint','Read 10+ papers, identify your niche'),
        (24,2,24,'Niche Selection','Pick research focus, deep dive'),
        (25,2,25,'Blog & Share','Write AI Security blog series'),
        (26,2,26,'Q2 Consolidation','Review, blog post, professor outreach'),
        (27,3,27,'Project Planning','Define project scope, set up repo'),
        (28,3,28,'Project Sprint 1','Core implementation started'),
        (29,3,29,'Project Sprint 2','Core features working'),
        (30,3,30,'Project Sprint 3','Project 60% complete'),
        (31,3,31,'Project Polish','Project complete, documented'),
        (32,3,32,'Second Project / Contribution','Start project #2 or contribute to OSS'),
        (33,3,33,'Research Paper Reading','Read 15+ papers in niche'),
        (34,3,34,'Research Writing','Draft research proposal or blog series'),
        (35,3,35,'Conference Content','Submit talk proposal or write a whitepaper'),
        (36,3,36,'Certifications Prep','Study for complementary certs'),
        (37,3,37,'CTF & Competitions','Participate in AI security CTFs'),
        (38,3,38,'Portfolio Building','Polish GitHub, blog, LinkedIn'),
        (39,3,39,'Q3 Consolidation','Review, assess, plan Q4'),
        (40,4,40,'PhD Application Prep','Research statements, CV, professor emails'),
        (41,4,41,'PhD Applications W1','First batch of applications submitted'),
        (42,4,42,'PhD Applications W2','All applications submitted'),
        (43,4,43,'Job Hunt Launch','Start applying to AI security roles'),
        (44,4,44,'Job Applications Sprint','Apply to 10+ positions'),
        (45,4,45,'Interview Prep','Technical and behavioral prep'),
        (46,4,46,'Interview Season','Active interviewing'),
        (47,4,47,'Advanced Topics','Stay sharp - learn emerging threats'),
        (48,4,48,'Community Building','Talks, mentoring, networking'),
        (49,4,49,'Open Source Sprint','Major OSS contribution'),
        (50,4,50,'Final Project','Capstone project for the year'),
        (51,4,51,'Year in Review','Document everything you achieved'),
        (52,4,52,'Plan 2027','Set goals for next year'),
    ]
    for wid, pid, wnum, title, goal in weeks_data:
        db.session.add(LearningWeek(id=wid, phase_id=pid, week_number=wnum, title=title, goal=goal))
    db.session.flush()

    tasks_data = [
        (1,"weekday","Pick up exactly where you left off in CPTS - no reviewing basics you know"),
        (1,"weekday","Target: complete 2 full modules this week"),
        (1,"weekday","Document key techniques as you go (your future writeup material)"),
        (1,"weekend","Python: data types, functions, file handling refresher (1.5h)"),
        (2,"weekday","Continue CPTS - target 2 more modules"),
        (2,"weekday","When you hit a hard topic, slow down - don't skip"),
        (2,"weekday","Start a notes doc: techniques, tools, commands to remember"),
        (2,"weekend","1 HTB machine or CTF challenge"),
        (3,"weekday","CPTS: 2 more modules - harder ones, budget focus time"),
        (3,"weekday","Write your first proper CTF writeup and publish it"),
        (3,"weekday","Review your notes, identify weakest areas"),
        (3,"weekend","Python: build a tiny tool - port scanner or request fuzzer (2h)"),
        (4,"weekday","Push to hit the 70% CPTS milestone"),
        (4,"weekday","Consolidate notes into a clean reference doc"),
        (4,"weekday","Do one HTB machine and write it up"),
        (4,"weekend","Cloud: spin up EC2 + S3 on AWS free tier, explore IAM (2h)"),
        (5,"weekday","Tackle CPTS advanced modules - Active Directory, pivoting"),
        (5,"weekday","Practice lateral movement techniques on HTB"),
        (5,"weekday","Document advanced attack chains"),
        (5,"weekend","Cloud: IAM misconfigs, deploy CloudGoat, find vulns (2h)"),
        (6,"weekday","Continue CPTS - aim for 85% completion"),
        (6,"weekday","Complete 2 HTB ProLab-style challenges"),
        (6,"weekday","Write detailed methodology notes for each attack type"),
        (6,"weekend","Python: scripts for automating recon and enumeration (2h)"),
        (7,"weekday","CPTS final sprint - complete remaining modules"),
        (7,"weekday","Focus on privilege escalation and post-exploitation"),
        (7,"weekday","Build a cheat sheet for exam day"),
        (7,"weekend","Practice full attack chains end-to-end on HTB (3h)"),
        (8,"weekday","Complete CPTS 100% - all modules finished"),
        (8,"weekday","Take the practice exam under timed conditions"),
        (8,"weekday","Review practice exam results, identify weak spots"),
        (8,"weekend","Re-do practice exam sections you struggled with"),
        (9,"weekday","Deep review of weakest CPTS areas"),
        (9,"weekday","Practice report writing - exam requires a professional report"),
        (9,"weekday","Do 2 more HTB machines matching exam difficulty"),
        (9,"weekend","Full mock scenario: enumerate, exploit, report (4h)"),
        (10,"weekday","Final mock exam run - full simulation"),
        (10,"weekday","Polish your report template"),
        (10,"weekday","Review time management strategy for the exam"),
        (10,"weekend","Light review only - don't burn out before exam"),
        (11,"weekday","TAKE THE CPTS EXAM - you're ready"),
        (11,"weekday","Document everything during the exam for your report"),
        (11,"weekday","Write and submit the exam report"),
        (11,"weekend","Rest and recover - you earned it"),
        (12,"weekday","Python deep dive: NumPy, Pandas, API interactions"),
        (12,"weekday","AWS: set up a proper lab environment"),
        (12,"weekday","Start collecting AI Security paper links for Q2"),
        (12,"weekend","Cloud security basics: S3 misconfigs, open endpoints (2h)"),
        (13,"weekday","Q1 retrospective: what worked, what didn't"),
        (13,"weekday","Organize all notes and writeups from Q1"),
        (13,"weekday","Plan Q2 learning schedule"),
        (13,"weekend","Publish a Q1 summary blog post"),
        (14,"weekday","Read: OWASP LLM Top 10 (full document)"),
        (14,"weekday","Watch: DEF CON / BlackHat AI security talks (YouTube)"),
        (14,"weekday","Hands-on: prompt injection on open playground tools"),
        (14,"weekend","Set up a local LLM (Ollama) and try basic attacks"),
        (15,"weekday","Study: indirect prompt injection techniques"),
        (15,"weekday","Practice jailbreaking on different LLM providers"),
        (15,"weekday","Read Perez & Ribeiro 2022 paper on prompt injection"),
        (15,"weekend","Build a prompt injection test suite (Python)"),
        (16,"weekday","Study: adversarial examples, model evasion attacks"),
        (16,"weekday","Hands-on: Adversarial Robustness Toolbox (ART) library"),
        (16,"weekday","Read 2 papers on adversarial ML"),
        (16,"weekend","Create adversarial examples against image classifiers"),
        (17,"weekday","Read: data poisoning and backdoor attack research"),
        (17,"weekday","Study supply chain risks in ML pipelines"),
        (17,"weekday","Connect AI threats to traditional security frameworks"),
        (17,"weekend","Lab: demonstrate a simple data poisoning attack"),
        (18,"weekday","Study: how AI models are deployed (APIs, containers, MLOps)"),
        (18,"weekday","Security of ML pipelines: model registries, versioning"),
        (18,"weekday","Audit an open-source ML deployment for vulnerabilities"),
        (18,"weekend","Deploy a simple ML model via API, attack its endpoint"),
        (19,"weekday","AWS SageMaker security concepts and misconfigs"),
        (19,"weekday","Azure ML security features and attack surface"),
        (19,"weekday","Study model theft and model extraction attacks"),
        (19,"weekend","Cloud lab: secure vs insecure ML deployment comparison"),
        (20,"weekday","Read about model inversion attacks"),
        (20,"weekday","Study membership inference attacks"),
        (20,"weekday","Understand differential privacy and federated learning"),
        (20,"weekend","Implement a membership inference attack (notebook)"),
        (21,"weekday","Study structured AI red teaming methodologies"),
        (21,"weekday","Read Microsoft/Google AI red team reports"),
        (21,"weekday","Create your own AI red team checklist"),
        (21,"weekend","Red team an open-source AI application end-to-end"),
        (22,"weekday","Deep dive: Adversarial Robustness Toolbox (ART)"),
        (22,"weekday","Explore Garak - LLM vulnerability scanner"),
        (22,"weekday","Hands-on with Microsoft PyRIT"),
        (22,"weekend","Compare tools: write a comparison blog post"),
        (23,"weekday","Read 3 papers on LLM security"),
        (23,"weekday","Read 3 papers on adversarial ML / model robustness"),
        (23,"weekday","Read 3 papers on AI privacy"),
        (23,"weekend","Write a 1-page summary of the research landscape"),
        (24,"weekday","Pick your research niche based on Q2 exploration"),
        (24,"weekday","Read 4 papers specifically in your chosen niche"),
        (24,"weekday","Identify: what problems are unsolved in this area?"),
        (24,"weekend","Find 5 professors working in your niche"),
        (25,"weekday","Write blog post: AI Security Threat Landscape 2026"),
        (25,"weekday","Write blog post: Hands-on with AI Red Teaming"),
        (25,"weekday","Share on LinkedIn and Twitter/X - build visibility"),
        (25,"weekend","Draft initial PhD research statement (rough version)"),
        (26,"weekday","Revisit any AI sec topic that felt unclear"),
        (26,"weekday","Write: What I Learned About AI Security in 3 Months"),
        (26,"weekday","Reach out to 1 professor (informally, by email)"),
        (26,"weekend","Q2 retrospective and Q3 planning"),
        (27,"weekday","Define your AI security project: tool, framework, or research reproduction"),
        (27,"weekday","Set up GitHub repo with proper README and CI"),
        (27,"weekday","Design the architecture and create issues/milestones"),
        (27,"weekend","Read related work and existing tools in the space"),
        (28,"weekday","Code daily - focus on core functionality"),
        (28,"weekday","Write tests as you build"),
        (28,"weekday","Document design decisions in the repo"),
        (28,"weekend","Post progress update on LinkedIn/Twitter"),
        (29,"weekday","Continue building - tackle the hardest parts now"),
        (29,"weekday","Integrate with existing tools/frameworks where useful"),
        (29,"weekday","Ask for feedback from the security community"),
        (29,"weekend","Read 2 papers related to your project"),
        (30,"weekday","Push to 60% completion - core features should work"),
        (30,"weekday","Create demo scenarios / example usage"),
        (30,"weekday","Write a blog post about what you're building"),
        (30,"weekend","Weekend coding sprint - 4h focused session"),
        (31,"weekday","Complete the project - all planned features done"),
        (31,"weekday","Write comprehensive documentation"),
        (31,"weekday","Record a demo video or detailed walkthrough"),
        (31,"weekend","Publish and promote: GitHub, LinkedIn, Reddit"),
        (32,"weekday","Start a second smaller project or contribute to OSS AI security tools"),
        (32,"weekday","Contribute to Garak, ART, or another AI security framework"),
        (32,"weekday","Document your contributions"),
        (32,"weekend","Network: engage with AI security researchers online"),
        (33,"weekday","Read 5 recent papers in your research niche"),
        (33,"weekday","Read 5 seminal/foundational papers in the area"),
        (33,"weekday","Read 5 papers from top conferences (NeurIPS, ICML, USENIX)"),
        (33,"weekend","Write annotated bibliography of key papers"),
        (34,"weekday","Draft a research proposal for your niche"),
        (34,"weekday","Write a blog series covering your research area"),
        (34,"weekday","Identify potential collaborators"),
        (34,"weekend","Review and polish your PhD research statement"),
        (35,"weekday","Write a talk proposal for BSides, DEF CON, or similar"),
        (35,"weekday","Alternatively: write a whitepaper or technical report"),
        (35,"weekday","Create presentation slides for your research"),
        (35,"weekend","Practice presenting your work (record yourself)"),
        (36,"weekday","Study for complementary certs (AWS Security, OSCP, etc.)"),
        (36,"weekday","Focus on practice exams and weak areas"),
        (36,"weekday","Connect cert material to your AI security knowledge"),
        (36,"weekend","Hands-on labs for cert prep"),
        (37,"weekday","Participate in AI security CTF challenges"),
        (37,"weekday","Try AI village challenges from DEF CON"),
        (37,"weekday","Document your solutions as writeups"),
        (37,"weekend","Attempt harder challenges - push your limits"),
        (38,"weekday","Polish your GitHub profile and pin best repos"),
        (38,"weekday","Update blog with latest work"),
        (38,"weekday","Refresh LinkedIn with projects, certs, publications"),
        (38,"weekend","Build a personal portfolio website if you don't have one"),
        (39,"weekday","Q3 honest self-assessment: skills gained, gaps remaining"),
        (39,"weekday","Update your learning tracker with Q3 achievements"),
        (39,"weekday","Plan Q4 with concrete goals"),
        (39,"weekend","Write a Q3 retrospective blog post"),
        (40,"weekday","Finalize PhD research statement - make it compelling"),
        (40,"weekday","Polish CV: highlight projects, papers, CPTS cert"),
        (40,"weekday","Draft personalized emails for each professor"),
        (40,"weekend","Research 10 PhD programs with AI security faculty"),
        (41,"weekday","Submit first batch of PhD applications (3-4)"),
        (41,"weekday","Send emails to professors at target universities"),
        (41,"weekday","Prepare supplementary materials (code samples, portfolio)"),
        (41,"weekend","Follow up on earlier professor contacts"),
        (42,"weekday","Submit remaining PhD applications"),
        (42,"weekday","Send thank-you notes and follow-ups"),
        (42,"weekday","Prepare for potential interviews"),
        (42,"weekend","Practice research presentations for PhD interviews"),
        (43,"weekday","Update CV and LinkedIn for industry roles"),
        (43,"weekday","Identify 15-20 AI security / security engineer roles"),
        (43,"weekday","Tailor cover letters mentioning your projects"),
        (43,"weekend","Apply to first 5 positions"),
        (44,"weekday","Apply to 5+ more positions"),
        (44,"weekday","Network: reach out to hiring managers on LinkedIn"),
        (44,"weekday","Practice explaining your projects in 2 minutes"),
        (44,"weekend","Attend virtual security meetups / conferences"),
        (45,"weekday","Study common security interview questions"),
        (45,"weekday","Practice: explain AI security concepts simply"),
        (45,"weekday","Prepare system design answers for ML security"),
        (45,"weekend","Mock interviews with friends or online platforms"),
        (46,"weekday","Active interviewing - give it your best"),
        (46,"weekday","Send thank-you emails after each interview"),
        (46,"weekday","Continue applying - don't stop until you have offers"),
        (46,"weekend","Debrief each interview: what went well, what to improve"),
        (47,"weekday","Study emerging AI threats: AI agents, multi-modal attacks"),
        (47,"weekday","Read latest AI security research papers"),
        (47,"weekday","Experiment with new attack techniques"),
        (47,"weekend","Write a blog post on an emerging AI security topic"),
        (48,"weekday","Give a talk at a local meetup or online event"),
        (48,"weekday","Mentor someone starting in security"),
        (48,"weekday","Engage actively in AI security communities"),
        (48,"weekend","Attend a security conference (virtual or in-person)"),
        (49,"weekday","Make a significant contribution to an OSS security project"),
        (49,"weekday","Submit PRs to major AI security tools"),
        (49,"weekday","Document your contributions publicly"),
        (49,"weekend","Engage with project maintainers and community"),
        (50,"weekday","Define a capstone project that showcases everything you learned"),
        (50,"weekday","Build it - this is your masterpiece for the year"),
        (50,"weekday","Make it polished and professional"),
        (50,"weekend","Launch the capstone project publicly"),
        (51,"weekday","Write 2026 Year in Review: My AI Security Journey"),
        (51,"weekday","Update portfolio with all 2026 achievements"),
        (51,"weekday","Reflect: what skills are now strong, what needs growth"),
        (51,"weekend","Share your year-in-review on LinkedIn"),
        (52,"weekday","Set 2027 goals: career, research, certifications"),
        (52,"weekday","Plan Q1 2027 in detail"),
        (52,"weekday","Identify new areas to explore (AI governance, etc.)"),
        (52,"weekend","Celebrate - you completed a full year of disciplined learning!"),
    ]
    for wid, cat, desc in tasks_data:
        db.session.add(LearningTask(week_id=wid, category=cat, description=desc))
    db.session.commit()

def seed_books():
    if Book.query.count() > 0:
        return
    books = [
        ("The Web Application Hacker's Handbook","Dafydd Stuttard & Marcus Pinto",1,"security"),
        ("Penetration Testing","Georgia Weidman",1,"security"),
        ("Black Hat Python","Justin Seitz & Tim Arnold",1,"programming"),
        ("Automate the Boring Stuff with Python","Al Sweigart",1,"programming"),
        ("Adversarial Machine Learning","Joseph & Nelson & Rubinstein & Tygar",2,"ai_security"),
        ("Not with a Bug, But with a Sticker","Ram Shankar Siva Kumar & Hyrum Anderson",2,"ai_security"),
        ("Deep Learning","Ian Goodfellow, Yoshua Bengio & Aaron Courville",2,"ai_ml"),
        ("Hands-On Machine Learning","Aurelien Geron",2,"ai_ml"),
        ("AI and Machine Learning for Coders","Laurence Moroney",2,"ai_ml"),
        ("The Art of Software Security Assessment","Dowd, McDonald & Schuh",3,"security"),
        ("Practical Deep Learning for Cloud, Mobile & Edge","Anirudh Koul et al.",3,"ai_ml"),
        ("Building Secure & Reliable Systems","Google SRE Team",3,"security"),
        ("Writing for Computer Science","Justin Zobel",3,"research"),
        ("The PhD Application Handbook","Peter Bentley",4,"career"),
        ("Cracking the Coding Interview","Gayle McDowell",4,"career"),
        ("Security Engineering","Ross Anderson",4,"security"),
        ("Designing Data-Intensive Applications","Martin Kleppmann",4,"programming"),
    ]
    for i, (title, author, quarter, category) in enumerate(books):
        db.session.add(Book(title=title, author=author, quarter=quarter, category=category, sort_order=i))
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_quran()
        seed_learning_plan()
        seed_books()
    app.run(debug=True, port=5555, host='0.0.0.0')
