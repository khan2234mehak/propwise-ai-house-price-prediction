# 🏠 PropWise — AI-Powered House Price Prediction

**PropWise** is a full-stack AI-powered real estate application that predicts house prices based on property characteristics such as location, area, bedrooms, bathrooms, floors, property age, garage, and garden availability.

The application combines **Machine Learning, Flask REST APIs, SQLite, JWT authentication, and a responsive frontend** into a complete real-world web application.

---
## 🚀 Live Demo

👉 **[Try PropWise Live](https://propwise-ai-house-price-prediction.onrender.com)**

## 🚀 Features

### 🤖 AI House Price Prediction

* Predicts estimated property prices using a trained **Gradient Boosting Regressor**
* Uses property features such as:

  * Location
  * Area in sq. ft.
  * Bedrooms
  * Bathrooms
  * Floors
  * Property age
  * Garage
  * Garden

### 🔐 Authentication & Security

* User registration and login
* JWT-based authentication
* Password hashing using **Bcrypt**
* Role-based access for users and administrators
* Login activity tracking

### 📊 Prediction History

* Users can view their previous predictions
* Prediction details are stored in SQLite
* Each prediction contains property information, estimated price, and confidence score

### 📄 PDF Reports

* Generate downloadable PDF reports for predictions
* Reports include:

  * User information
  * Property details
  * Estimated market value
  * AI confidence score
  * Disclaimer

### 👨‍💼 Admin Dashboard

Administrators can:

* View system statistics
* Manage users
* Activate/deactivate users
* View login logs
* View all predictions
* Download prediction reports

### 🌐 REST API

The backend provides APIs for:

* Authentication
* Property prediction
* Prediction history
* Admin management
* Location data
* Health monitoring

---

## 🧠 Machine Learning

PropWise uses a **Gradient Boosting Regressor** for house price prediction.

### ML Pipeline

```text
Property Input
      ↓
Location Encoding
      ↓
Feature Scaling
      ↓
Gradient Boosting Regressor
      ↓
Predicted House Price
      ↓
Prediction History / PDF Report
```

### Model Features

| Feature      | Description              |
| ------------ | ------------------------ |
| Location     | Property location        |
| Area         | Built-up area in sq. ft. |
| Bedrooms     | Number of bedrooms       |
| Bathrooms    | Number of bathrooms      |
| Floors       | Number of floors         |
| Property Age | Age of the property      |
| Garage       | Garage availability      |
| Garden       | Garden/lawn availability |

The trained model and preprocessing files are included in the `ml_model` directory.

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* Flask-CORS
* Flask-JWT-Extended
* Flask-Bcrypt
* REST API

### Machine Learning

* Scikit-learn
* Gradient Boosting Regressor
* Pandas
* NumPy
* Joblib
* StandardScaler
* LabelEncoder

### Database

* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript

### Other

* ReportLab for PDF generation
* python-dotenv for environment configuration

---

## 📁 Project Structure

```text
propwise/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── .env
│
├── database/
│   └── propwise.db
│
├── frontend/
│   └── index.html
│
├── ml_model/
│   ├── model.pkl
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   ├── locations.pkl
│   └── train_model.py
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/khan2234mehak/propwise-ai-house-price-prediction.git
```

```bash
cd propwise-ai-house-price-prediction
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file inside the `backend` folder:

```env
JWT_SECRET_KEY=your_secret_key_here
```

For security, do not commit the real `.env` file to GitHub.

### 5. Start the Flask server

```bash
python app.py
```

The application runs on:

```text
http://localhost:8080
```

Open the URL in your browser.

---

## 🔑 Demo Admin Account

For local/demo testing:

```text
Email: admin@propwise.com
Password: Admin@123
```

> ⚠️ Change the default credentials before using the application in a production environment.

---

## 🔌 API Endpoints

### Authentication

```text
POST /api/auth/register
POST /api/auth/login
```

### Prediction

```text
GET  /api/locations
POST /api/predict
GET  /api/predictions/history
GET  /api/predictions/download/<id>
```

### Admin

```text
GET  /api/admin/stats
GET  /api/admin/users
GET  /api/admin/login-logs
GET  /api/admin/predictions
GET  /api/admin/predictions/download/<id>
POST /api/admin/users/<id>/toggle
```

### Health Check

```text
GET /api/health
```

---

## 📊 Model Training

The project includes the training script:

```text
ml_model/train_model.py
```

To retrain the model:

```bash
cd ml_model
python train_model.py
```

The script generates the required model artifacts:

```text
model.pkl
scaler.pkl
label_encoder.pkl
locations.pkl
```

The application can use the already-trained `.pkl` files, so retraining is not required for normal usage.

---

## 🗄️ Database

PropWise uses **SQLite** to store application data.

The database manages:

* User accounts
* User roles
* Login logs
* Property predictions
* Prediction history

The database tables are automatically initialized when the Flask application starts.

---

## 🔒 Security

The application implements several security mechanisms:

* JWT authentication
* Bcrypt password hashing
* Role-based authorization
* Protected admin routes
* Environment-based JWT secret configuration
* SQLite foreign-key constraints

For production deployment, additional security configuration such as restricted CORS origins, secure secrets, HTTPS, and stronger credential management is recommended.

---

## 🎯 Use Cases

PropWise can be used as:

* 🏠 A property price estimation tool
* 📊 A real estate analytics application
* 🤖 A machine learning deployment project
* 🎓 An academic/project portfolio application
* 💼 A demonstration of integrating ML with a full-stack web application

---

## 🔮 Future Improvements

* [ ] Integrate a real-world housing dataset
* [ ] Add more advanced ML models
* [ ] Compare multiple regression algorithms
* [ ] Add model performance visualization
* [ ] Add interactive price trends
* [ ] Add property recommendations
* [ ] Deploy the application to a cloud platform
* [ ] Add Docker support
* [ ] Add automated testing
* [ ] Improve production-level security

---

## 👩‍💻 Author

**Mehak Khan**

GitHub:
https://github.com/khan2234mehak

---

## ⭐ Project Highlights

**PropWise demonstrates end-to-end implementation of:**

```text
Machine Learning
       +
Flask REST API
       +
SQLite Database
       +
JWT Authentication
       +
Admin Dashboard
       +
PDF Report Generation
       +
Frontend Interface
```

A complete **AI + Full-Stack Real Estate Prediction Platform** built with Python and modern web technologies.

---

## 📜 Disclaimer

PropWise provides AI-generated property price estimates for **educational and informational purposes only**. The predictions should not be considered official property valuations or financial advice.
