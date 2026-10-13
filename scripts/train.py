import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import os

# Ensure models directory exists
os.makedirs("models", exist_ok=True)

# 1. Load Data
print("Loading dataset...")
df = pd.read_csv('data/creditcard.csv')

# 2. Balance Dataset (492 fraud, 508 normal)
fraud = df[df['Class'] == 1]
normal = df[df['Class'] == 0].sample(n=508, random_state=42)
balanced_df = pd.concat([fraud, normal]).sample(frac=1, random_state=42)

X = balanced_df.drop('Class', axis=1)
y = balanced_df['Class']

# 3. Preprocess Features
print("Applying RobustScaler and float32 casting...")
scaler = RobustScaler()
X[['Time', 'Amount']] = scaler.fit_transform(X[['Time', 'Amount']])
X = X.astype(np.float32)

# 4. Train Model
print("Training Random Forest...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 5. Export to ONNX
print("Converting and saving ONNX model...")
initial_type = [('float_input', FloatTensorType([None, X.shape[1]]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)

with open("models/model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("Success: Model saved to models/model.onnx")