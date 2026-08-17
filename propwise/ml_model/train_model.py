"""
PropWise - ML Model Training
Run this ONCE from the ml_model folder:
  cd ml_model
  python train_model.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib, os

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

np.random.seed(42)
n = 3000

locations = ['Downtown', 'Suburb North', 'Suburb South', 'City Center',
             'Old Town', 'Riverside', 'Tech District', 'Green Valley',
             'Rohini', 'Dwarka', 'Karol Bagh', 'Janakpuri']

location_multiplier = {
    'Downtown': 1.5, 'Suburb North': 1.1, 'Suburb South': 1.0,
    'City Center': 1.6, 'Old Town': 0.9, 'Riverside': 1.3,
    'Tech District': 1.4, 'Green Valley': 1.2,
    'Rohini': 1.1, 'Dwarka': 1.15, 'Karol Bagh': 1.35, 'Janakpuri': 1.2
}

loc_col   = np.random.choice(locations, n)
area      = np.random.randint(500, 5000, n).astype(float)
bedrooms  = np.random.randint(1, 7, n)
bathrooms = np.random.randint(1, 5, n)
floors    = np.random.randint(1, 4, n)
age       = np.random.randint(0, 50, n)
garage    = np.random.randint(0, 2, n)
garden    = np.random.randint(0, 2, n)

base_price = (
    area * 120 + bedrooms * 15000 + bathrooms * 10000
    + floors * 8000 - age * 2000 + garage * 20000 + garden * 12000
    + np.array([location_multiplier[l] * 50000 for l in loc_col])
    + np.random.normal(0, 20000, n)
)
price = np.clip(base_price, 50000, 3000000)

df = pd.DataFrame({
    'location': loc_col, 'area_sqft': area, 'bedrooms': bedrooms,
    'bathrooms': bathrooms, 'floors': floors, 'age_of_property': age,
    'garage': garage, 'garden': garden, 'price': price
})

le = LabelEncoder()
df['location_enc'] = le.fit_transform(df['location'])
feature_cols = ['location_enc','area_sqft','bedrooms','bathrooms','floors','age_of_property','garage','garden']
X = df[feature_cols].values
y = df['price'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = GradientBoostingRegressor(n_estimators=300, learning_rate=0.08, max_depth=5, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"MAE : Rs.{mean_absolute_error(y_test, y_pred):,.0f}")
print(f"R2  : {r2_score(y_test, y_pred):.4f}")

# Save directly in ml_model folder (same as this script)
joblib.dump(model,     os.path.join(SAVE_DIR, 'model.pkl'))
joblib.dump(scaler,    os.path.join(SAVE_DIR, 'scaler.pkl'))
joblib.dump(le,        os.path.join(SAVE_DIR, 'label_encoder.pkl'))
joblib.dump(locations, os.path.join(SAVE_DIR, 'locations.pkl'))
print("Model saved to: " + SAVE_DIR)
