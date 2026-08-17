"""
PropWise - AI House Price Prediction
Flask Backend | SQLite | Port 8080
"""
import os, datetime, sqlite3, io
from functools import wraps
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import joblib, numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

load_dotenv()

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
DB_PATH      = os.path.join(BASE_DIR, '..', 'database', 'propwise.db')
ML_DIR       = os.path.join(BASE_DIR, '..', 'ml_model')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'propwise_secret_2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=24)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── DB ────────────────────────────────────────────────────────────────────────
def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name     TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role          TEXT DEFAULT 'user',
            is_active     INTEGER DEFAULT 1,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS login_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            status     TEXT DEFAULT 'success',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS predictions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            location         TEXT,
            area_sqft        REAL,
            bedrooms         INTEGER,
            bathrooms        INTEGER,
            floors           INTEGER,
            age_of_property  INTEGER,
            garage           INTEGER DEFAULT 0,
            garden           INTEGER DEFAULT 0,
            predicted_price  REAL,
            confidence_score REAL,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    db.commit()
    row = db.execute("SELECT id FROM users WHERE email='admin@propwise.com'").fetchone()
    if not row:
        pw = bcrypt.generate_password_hash('Admin@123').decode('utf-8')
        db.execute("INSERT INTO users (full_name,email,password_hash,role) VALUES (?,?,?,?)",
                   ('System Admin', 'admin@propwise.com', pw, 'admin'))
        db.commit()
        print("Admin created: admin@propwise.com / Admin@123")
    db.close()

# ── ML Model ──────────────────────────────────────────────────────────────────
print(f"Loading ML model from: {ML_DIR}")
try:
    model     = joblib.load(os.path.join(ML_DIR, 'model.pkl'))
    scaler    = joblib.load(os.path.join(ML_DIR, 'scaler.pkl'))
    le        = joblib.load(os.path.join(ML_DIR, 'label_encoder.pkl'))
    locations = joblib.load(os.path.join(ML_DIR, 'locations.pkl'))
    print("ML model loaded OK")
except Exception as e:
    print(f"ML model error: {e}")
    model = scaler = le = locations = None

# ── Helpers ───────────────────────────────────────────────────────────────────
def require_admin(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = int(get_jwt_identity())
        db  = get_db()
        row = db.execute("SELECT role FROM users WHERE id=?", (uid,)).fetchone()
        db.close()
        if not row or row['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def build_pdf(p):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
          rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=40)
    styles = getSampleStyleSheet()
    elems  = []

    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=28,
                  textColor=colors.HexColor('#1a1a2e'), spaceAfter=4)
    sub_style   = ParagraphStyle('S', parent=styles['Normal'], fontSize=11,
                  textColor=colors.HexColor('#4a4a6a'), spaceAfter=16)

    elems.append(Paragraph("PropWise", title_style))
    elems.append(Paragraph("AI House Price Prediction Report", sub_style))
    elems.append(Spacer(1, 0.1*inch))

    # User info table
    info_data = [
        ['Owner', p['full_name'], 'Email', p['email']],
        ['Report ID', str(p['id']), 'Generated', str(p['created_at'])[:19]],
    ]
    it = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1*inch, 2.3*inch])
    it.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(0,-1), colors.HexColor('#1a1a2e')),
        ('BACKGROUND', (2,0),(2,-1), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR',  (0,0),(0,-1), colors.white),
        ('TEXTCOLOR',  (2,0),(2,-1), colors.white),
        ('FONTNAME',   (0,0),(-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,0),(-1,-1), 9),
        ('GRID',       (0,0),(-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING',    (0,0),(-1,-1), 8),
        ('ROWBACKGROUNDS', (1,0),(1,-1), [colors.HexColor('#f0f0f8')]),
        ('ROWBACKGROUNDS', (3,0),(3,-1), [colors.HexColor('#f0f0f8')]),
    ]))
    elems.append(it)
    elems.append(Spacer(1, 0.25*inch))

    elems.append(Paragraph("Property Details", styles['Heading2']))
    prop_data = [
        ['Parameter', 'Value'],
        ['Location',        str(p['location'])],
        ['Built-up Area',   f"{float(p['area_sqft']):,.0f} sq ft"],
        ['Bedrooms',        str(p['bedrooms'])],
        ['Bathrooms',       str(p['bathrooms'])],
        ['Floors',          str(p['floors'])],
        ['Age of Property', f"{p['age_of_property']} years"],
        ['Garage',          'Yes' if p['garage'] else 'No'],
        ['Garden / Lawn',   'Yes' if p['garden'] else 'No'],
    ]
    pt = Table(prop_data, colWidths=[2.5*inch, 3.5*inch])
    pt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR',     (0,0),(-1,0), colors.white),
        ('FONTNAME',      (0,0),(-1,0), 'Helvetica-Bold'),
        ('FONTNAME',      (0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE',      (0,0),(-1,-1), 10),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, colors.HexColor('#f5f5fb')]),
        ('PADDING',       (0,0),(-1,-1), 9),
    ]))
    elems.append(pt)
    elems.append(Spacer(1, 0.25*inch))

    elems.append(Paragraph("Prediction Result", styles['Heading2']))
    price_str = f"Rs. {float(p['predicted_price']):,.2f}"
    conf_str  = f"{float(p['confidence_score']):.1f}%"
    res_data  = [
        ['Estimated Market Value', price_str],
        ['AI Confidence Score',    conf_str],
    ]
    rt = Table(res_data, colWidths=[3*inch, 3*inch])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), colors.HexColor('#e8eaf6')),
        ('FONTNAME',   (0,0),(-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0),(-1,-1), 13),
        ('ALIGN',      (0,0),(-1,-1), 'CENTER'),
        ('GRID',       (0,0),(-1,-1), 1.5, colors.HexColor('#1a1a2e')),
        ('PADDING',    (0,0),(-1,-1), 14),
        ('TEXTCOLOR',  (0,0),(-1,-1), colors.HexColor('#1a1a2e')),
    ]))
    elems.append(rt)
    elems.append(Spacer(1, 0.4*inch))
    elems.append(Paragraph(
        "Disclaimer: This is an AI-generated estimate for informational purposes only. "
        "Please consult a certified property valuator for official valuation.",
        ParagraphStyle('disc', parent=styles['Italic'], fontSize=8,
                       textColor=colors.HexColor('#888888'))
    ))
    doc.build(elems)
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    data      = request.get_json()
    full_name = (data.get('full_name') or '').strip()
    email     = (data.get('email') or '').strip().lower()
    password  = data.get('password') or ''
    if not all([full_name, email, password]):
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        db  = get_db()
        cur = db.execute(
            "INSERT INTO users (full_name,email,password_hash) VALUES (?,?,?)",
            (full_name, email, pw_hash))
        db.commit()
        uid = cur.lastrowid
        db.close()
        token = create_access_token(identity=str(uid))
        return jsonify({'token': token,
                        'user': {'id': uid, 'name': full_name,
                                 'email': email, 'role': 'user'}}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    ip       = request.remote_addr
    ua       = (request.headers.get('User-Agent') or '')[:300]
    db       = get_db()
    try:
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND is_active=1", (email,)).fetchone()
        if not user or not bcrypt.check_password_hash(user['password_hash'], password):
            if user:
                db.execute(
                    "INSERT INTO login_logs (user_id,ip_address,user_agent,status) VALUES (?,?,?,'failed')",
                    (user['id'], ip, ua))
                db.commit()
            db.close()
            return jsonify({'error': 'Invalid email or password'}), 401
        db.execute(
            "INSERT INTO login_logs (user_id,ip_address,user_agent,status) VALUES (?,?,?,'success')",
            (user['id'], ip, ua))
        db.commit()
        uid, name, role, em = user['id'], user['full_name'], user['role'], user['email']
        db.close()
        token = create_access_token(identity=str(uid))
        return jsonify({'token': token,
                        'user': {'id': uid, 'name': name,
                                 'email': em, 'role': role}}), 200
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 500

# ══════════════════════════════════════════════════════════════════════════════
# PREDICTION
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/locations', methods=['GET'])
def get_locations():
    fallback = ['Downtown', 'Suburb North', 'Suburb South', 'City Center',
                'Old Town', 'Riverside', 'Tech District', 'Green Valley',
                'Rohini', 'Dwarka', 'Karol Bagh', 'Janakpuri']
    locs = sorted(locations) if locations else fallback
    return jsonify({'locations': locs}), 200

@app.route('/api/predict', methods=['POST'])
@jwt_required()
def predict():
    if model is None:
        return jsonify({'error': 'ML model not loaded'}), 503
    uid  = int(get_jwt_identity())
    data = request.get_json()
    try:
        location  = str(data['location'])
        area      = float(data['area_sqft'])
        bedrooms  = int(data['bedrooms'])
        bathrooms = int(data['bathrooms'])
        floors    = int(data['floors'])
        age       = int(data['age_of_property'])
        garage    = int(data.get('garage', 0))
        garden    = int(data.get('garden', 0))
    except (KeyError, ValueError) as e:
        return jsonify({'error': f'Invalid input: {e}'}), 400

    # Handle custom / unknown locations gracefully
    known = list(locations) if locations else []
    loc_enc_val = location if location in known else (known[0] if known else 'Downtown')
    try:
        loc_enc = le.transform([loc_enc_val])[0]
    except Exception:
        loc_enc = 0

    X    = np.array([[loc_enc, area, bedrooms, bathrooms, floors, age, garage, garden]])
    X_sc = scaler.transform(X)
    price = float(model.predict(X_sc)[0])
    # Safe confidence calculation for GradientBoostingRegressor
    try:
        staged = list(model.staged_predict(X_sc))
        last20 = [float(p[0]) for p in staged[-20:]]
        conf   = max(0, min(100, 100 - (np.std(last20) / max(price, 1) * 100)))
    except Exception:
        conf   = 85.0

    db  = get_db()
    cur = db.execute(
        """INSERT INTO predictions
           (user_id,location,area_sqft,bedrooms,bathrooms,floors,
            age_of_property,garage,garden,predicted_price,confidence_score)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (uid, location, area, bedrooms, bathrooms,
         floors, age, garage, garden, price, conf))
    db.commit()
    pred_id = cur.lastrowid
    db.close()
    return jsonify({'prediction_id': pred_id,
                    'predicted_price': round(price, 2),
                    'confidence': round(conf, 1)}), 200

@app.route('/api/predictions/history', methods=['GET'])
@jwt_required()
def history():
    uid  = int(get_jwt_identity())
    db   = get_db()
    rows = db.execute(
        "SELECT * FROM predictions WHERE user_id=? ORDER BY created_at DESC LIMIT 50",
        (uid,)).fetchall()
    db.close()
    return jsonify({'predictions': [dict(r) for r in rows]}), 200

@app.route('/api/predictions/download/<int:pred_id>', methods=['GET'])
@jwt_required()
def download_report(pred_id):
    uid = int(get_jwt_identity())
    db  = get_db()
    p   = db.execute(
        "SELECT p.*,u.full_name,u.email FROM predictions p "
        "JOIN users u ON p.user_id=u.id WHERE p.id=? AND p.user_id=?",
        (pred_id, uid)).fetchone()
    db.close()
    if not p:
        return jsonify({'error': 'Not found'}), 404
    buf = build_pdf(dict(p))
    return send_file(buf, as_attachment=True,
                     download_name=f"propwise_report_{pred_id}.pdf",
                     mimetype='application/pdf')

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/admin/stats', methods=['GET'])
@require_admin
def admin_stats():
    db = get_db()
    total_users  = db.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0]
    total_logins = db.execute("SELECT COUNT(*) FROM login_logs WHERE status='success'").fetchone()[0]
    total_preds  = db.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    failed_logins= db.execute("SELECT COUNT(*) FROM login_logs WHERE status='failed'").fetchone()[0]
    daily = db.execute("""
        SELECT DATE(login_time) as date, COUNT(*) as count
        FROM login_logs WHERE login_time >= DATE('now','-7 days')
        GROUP BY DATE(login_time) ORDER BY date
    """).fetchall()
    db.close()
    return jsonify({
        'total_users': total_users, 'total_logins': total_logins,
        'total_predictions': total_preds, 'failed_logins': failed_logins,
        'daily_logins': [dict(d) for d in daily]
    }), 200

@app.route('/api/admin/users', methods=['GET'])
@require_admin
def admin_users():
    db    = get_db()
    users = db.execute("""
        SELECT u.id, u.full_name, u.email, u.role, u.is_active, u.created_at,
               COUNT(DISTINCT ll.id) as total_logins,
               MAX(ll.login_time)    as last_login,
               COUNT(DISTINCT p.id)  as total_predictions
        FROM users u
        LEFT JOIN login_logs ll ON u.id=ll.user_id AND ll.status='success'
        LEFT JOIN predictions  p  ON u.id=p.user_id
        GROUP BY u.id ORDER BY u.created_at DESC
    """).fetchall()
    db.close()
    return jsonify({'users': [dict(u) for u in users]}), 200

@app.route('/api/admin/login-logs', methods=['GET'])
@require_admin
def admin_login_logs():
    db   = get_db()
    logs = db.execute("""
        SELECT ll.id, u.full_name, u.email, ll.login_time,
               ll.ip_address, ll.status, ll.user_agent
        FROM login_logs ll JOIN users u ON ll.user_id=u.id
        ORDER BY ll.login_time DESC LIMIT 500
    """).fetchall()
    db.close()
    return jsonify({'logs': [dict(l) for l in logs]}), 200

@app.route('/api/admin/predictions', methods=['GET'])
@require_admin
def admin_predictions():
    db   = get_db()
    rows = db.execute("""
        SELECT p.*, u.full_name, u.email
        FROM predictions p JOIN users u ON p.user_id=u.id
        ORDER BY p.created_at DESC LIMIT 500
    """).fetchall()
    db.close()
    return jsonify({'predictions': [dict(r) for r in rows]}), 200

@app.route('/api/admin/predictions/download/<int:pred_id>', methods=['GET'])
@require_admin
def admin_download_report(pred_id):
    db = get_db()
    p  = db.execute(
        "SELECT p.*,u.full_name,u.email FROM predictions p "
        "JOIN users u ON p.user_id=u.id WHERE p.id=?", (pred_id,)).fetchone()
    db.close()
    if not p:
        return jsonify({'error': 'Not found'}), 404
    buf = build_pdf(dict(p))
    return send_file(buf, as_attachment=True,
                     download_name=f"propwise_admin_report_{pred_id}.pdf",
                     mimetype='application/pdf')

@app.route('/api/admin/users/<int:uid>/toggle', methods=['POST'])
@require_admin
def toggle_user(uid):
    db  = get_db()
    row = db.execute("SELECT is_active FROM users WHERE id=?", (uid,)).fetchone()
    if not row:
        db.close()
        return jsonify({'error': 'User not found'}), 404
    new_val = 0 if row['is_active'] else 1
    db.execute("UPDATE users SET is_active=? WHERE id=?", (new_val, uid))
    db.commit()
    db.close()
    return jsonify({'is_active': new_val}), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'ml': 'loaded' if model else 'not loaded'}), 200

# ── Serve Frontend ────────────────────────────────────────────────────────────
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 8080))
    print(f"\n{'='*52}")
    print(f"  PropWise  ->  http://localhost:{port}")
    print(f"  Admin:  admin@propwise.com / Admin@123")
    print(f"{'='*52}\n")
    app.run(debug=True, host='0.0.0.0', port=port)