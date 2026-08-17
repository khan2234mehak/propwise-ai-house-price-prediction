# PropWise - AI House Price Prediction

## Run in 3 Steps

### Step 1 - Install packages
```
cd propwise\backend
pip install -r requirements.txt
```

### Step 2 - Start server
```
python app.py
```

### Step 3 - Open browser
```
http://localhost:8080
```

---

## Admin Login
- Email: admin@propwise.com
- Password: Admin@123

## Features
- AI house price prediction
- PDF report download
- Admin panel with login logs
- User management

## Folder Structure
```
propwise/
  backend/    <- app.py (Flask server, port 8080)
  frontend/   <- index.html
  ml_model/   <- model.pkl + train_model.py
  database/   <- auto-created SQLite DB
```

## Note
ML model pkl files are already included.
No need to run train_model.py unless you want to retrain.
