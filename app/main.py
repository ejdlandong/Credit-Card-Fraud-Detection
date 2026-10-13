from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import onnxruntime as rt
import numpy as np
import time
from typing import Dict

app = FastAPI(title="Fraud Detection API", version="1.0")

# Load ONNX model at startup
session = rt.InferenceSession("models/model.onnx")
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name
probability_name = session.get_outputs()[1].name

class Transaction(BaseModel):
    # Accepts a dictionary of the 30 features
    features: Dict[str, float]

@app.post("/v1/predict")
async def predict(transaction: Transaction):
    start_time = time.perf_counter()
    
    try:
        # Extract exactly 30 features in standard order
        input_data = np.array(list(transaction.features.values()), dtype=np.float32).reshape(1, 30)
        
        # Execute ONNX graph
        prediction = session.run([output_name, probability_name], {input_name: input_data})
        
        pred_class = int(prediction[0][0])
        fraud_prob = float(prediction[1][0][1]) # Probability of class 1 (Fraud)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")

    latency_ms = (time.perf_counter() - start_time) * 1000

    return {
        "prediction": pred_class,
        "fraud_probability": round(fraud_prob, 4),
        "latency_ms": round(latency_ms, 2)
    }
    
@app.get("/healthz")
def health_check():
    return {"status": "ok"}