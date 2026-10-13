# Cloud-Deployed Credit Card Fraud Classifier

**CPE180P: Cloud AI & MLOps | Mapúa University**

A production-ready, containerized machine-learning inference service for real-time credit card fraud classification. It uses FastAPI and ONNX Runtime inside Docker to validate transaction requests and execute the exported classification model.

## Quick Start: Local Testing

Prerequisites: Git, Docker, and Python 3. Replace `<repository-url>` with the URL of this repository.

Clone the repository:

```bash
git clone <repository-url>
cd Credit-Card-Fraud-Detection
```

Build the Docker image:

```bash
docker build -t fraud-detection-api .
```

Run the API container:

```bash
docker run -d -p 8000:8000 --name fraud-api-server fraud-detection-api
```

Verify service health:

```bash
curl http://localhost:8000/healthz
```

Run the 200-request benchmark from the repository root. The client uses the `requests` package; install it with `python3 -m pip install requests` if needed.

```bash
python3 tests/client.py --url http://localhost:8000 --n 200
```

## Architecture & Environment

The project simulates a cloud deployment using WSL2 Ubuntu. The client node is `evan_josh`, and the cloud node is `sakura`.

FastAPI serves traffic on TCP port 8000. The `/v1/predict` route accepts a JSON body with a `features` object containing exactly 30 numerical values: `Time`, `V1` through `V28`, and `Amount`. Pydantic validates the named fields and rejects missing or extra fields. The API assembles values in the model's feature order, converts them to a `float32` tensor, and passes the tensor to ONNX Runtime. Docker packages the API and ONNX model in an isolated, non-root runtime container.

## Repository Layout

```text
.
├── app/
│   └── main.py                 # FastAPI application and ONNX Runtime integration
├── data/
│   └── creditcard.csv          # Engineered 1,000-record training/evaluation corpus
├── models/
│   └── model.onnx              # Exported ONNX classification model
├── scripts/
│   └── train.py                # Offline model training and ONNX export
├── tests/
│   └── client.py               # Latency benchmark and integration test harness
├── deploy/
│   ├── deploy.sh               # Automated image build, container swap, and health check
│   ├── setup_vm.sh             # Server initialization and UFW configuration
│   └── fraud-api.service       # Systemd unit for container persistence
├── Dockerfile                  # Multi-stage container definition
└── requirements.txt            # Python dependencies
```

## Data & Model Provenance

The project uses the Kaggle Credit Card Fraud Detection benchmark provided by the ULB Machine Learning Group. The engineered balanced subset contains 1,000 records: 492 fraudulent transactions and 508 legitimate transactions.

The numerical input schema consists of `Time`, `V1` through `V28`, and `Amount` (30 features total). Prediction requests pass these named values inside the top-level `features` object.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/v1/predict` | POST | Validates the 30-feature schema and executes the ONNX graph. Returns the predicted class, fraud probability, and inference latency. |
| `/healthz` | GET | Operational health check. Returns `{"status":"ok"}` when the API is responding. |

## Deployment & Automation (`deploy/` folder)

The deployment scripts automate setup and container lifecycle management:

- Run `./deploy/deploy.sh` from the repository root to build the image, remove any existing `fraud-api-server` container, launch the replacement on port 8000, and validate `/healthz`.
- Run `./deploy/setup_vm.sh` on a new Ubuntu host to install Docker and supporting tools, enable Docker at boot, and configure UFW to allow SSH (TCP 22) and API traffic (TCP 8000).
- `deploy/fraud-api.service` runs the container under systemd with `Restart=always`, so systemd brings it back after a service failure or host reboot. Install and enable this unit when using systemd to manage the container. The unit and `deploy.sh` both manage a container named `fraud-api-server`; use one management mode at a time to avoid container-name conflicts.

To enable the systemd unit after the image is available:

```bash
sudo cp deploy/fraud-api.service /etc/systemd/system/fraud-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now fraud-api.service
```

## Security & Validation

- Pydantic enforces the exact 30-feature schema. Missing, extra, non-numeric, or malformed feature values are rejected with HTTP 422 before model inference.
- Docker isolates the service process and filesystem, and the API runs as a non-root container user.
- The API does not configure authentication or TLS. Put it behind appropriate access controls and encrypted transport before exposing it to untrusted clients.

## Moving to a Real Cloud Server

Provision an Ubuntu VM on a provider such as AWS EC2 or Sakura Cloud. Install your SSH public key during provisioning, then connect over SSH. Configure the host firewall to deny unsolicited inbound traffic while permitting SSH and the API port:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

From the VM, clone the repository and run the included initialization and deployment scripts:

```bash
git clone <repository-url>
cd Credit-Card-Fraud-Detection
chmod +x deploy/setup_vm.sh deploy/deploy.sh
./deploy/setup_vm.sh
./deploy/deploy.sh
```

The setup script installs Docker and adds the same UFW allow rules. Confirm that the cloud provider's network firewall also permits TCP 22 and 8000. Use the systemd unit described above if systemd should own container startup and restart behavior; do not run both container-management modes at the same time.

## Measured Results

| Metric | Result |
|---|---|
| Server p95 latency | ~3.72 ms over 200 requests; passes the <100 ms target. |
| Schema validation | Invalid requests are safely rejected with HTTP 422. |

The supplied benchmark client reports average client round-trip latency. The p95 value above is the separately measured project result.

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Port is already allocated | An old container is still running. | Run `docker rm -f fraud-api-server`. |
| HTTP 422 Unprocessable Entity | The client payload is missing features or does not match the required schema. | Ensure the `features` object contains exactly the 30 numerical fields: `Time`, `V1`–`V28`, and `Amount`. |
| `IndentationError` in `app/main.py` | Python route formatting is invalid. | Ensure `@app.get` has zero leading spaces. |

## Team & References

| Name | Student ID | Role |
|---|---|---|
| Evan Landong  | Lead MLOps Engineer / Student |
| Ronald Allen Cabral | Data & Training Lead |
| Jersey Calisle Estrella | Backend API Developer |

Dataset reference: Machine Learning Group, Université Libre de Bruxelles. *Credit Card Fraud Detection*. Kaggle. https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud