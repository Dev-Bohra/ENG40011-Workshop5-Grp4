# AR Dementia Care Prototype (Backend / Vision System)

A proof-of-concept assistive system designed to reduce caregiver supervision requirements for dementia patients through computer vision–based task monitoring and remote caregiver alerts.

This branch contains the **backend vision system**, including the YOLOv8 detection pipeline, fire detection logic, evidence capture, Flask server, and Supabase integration.

The **caregiver dashboard frontend (Vite/Vue application)** is located in the:

```text
caregiver-app
```

branch of this repository.

The system uses YOLOv8 object detection to identify task completion events (e.g., drinking water or breakfast preparation) and a custom-trained fire detection model to trigger caregiver alerts in real time.

## Features

* Real-time object detection using YOLOv8
* Fire detection with persistent alert logic
* Evidence image capture for completed tasks
* Remote caregiver monitoring through Supabase
* Live camera feed streaming
* Task completion logging with image evidence

## Demo Tasks

### 1. Drink Water Task

* Detects a water bottle
* Captures evidence image
* Marks hydration task as completed

### 2. Breakfast Task

Detects both:

* Apple
* Cup

Captures evidence image and marks the breakfast task as completed.

### 3. Fire Safety Monitoring

* Detects visible flames using a custom YOLOv8 model
* Sends persistent caregiver alerts
* Prevents alert flickering using a hold timer

## Technology Stack

* Python
* Flask
* OpenCV
* YOLOv8 (Ultralytics)
* Supabase
* Flask-CORS

## Project Structure

```txt
project-root/
│── app.py
│── requirements.txt
│── yolov8n.pt
│── evidence/
│── models/
│   └── flame_exp1/
│       └── flame_yolov8n_30ep/
│           └── weights/
│               └── best.pt
│── assets/
│   └── database_schema.png
```

## Database Structure

The system uses Supabase to manage caregiver alerts, task tracking, and evidence image storage.

![Database Schema](assets/database_schema.png)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Supabase

Replace the placeholders in:

```python
app.py
```

with your project values:

```python
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
SUPABASE_BUCKET = "task-evidence"
```

Create a storage bucket named:

```txt
task-evidence
```

### 3. Run the Backend Server

```bash
python app.py
```

## Network Requirement

For the caregiver dashboard and backend system to communicate correctly, both devices must be connected to the **same local network**.

Recommended:

* Mobile hotspot
* Home Wi-Fi
* Local router network

**Do not use Eduroam**, as device-to-device communication may be restricted.

Example setup:

```text
Laptop 1 → Backend / Vision System
Laptop 2 → Caregiver Dashboard (caregiver-app branch)

Both connected to same Wi-Fi or hotspot
```

## Endpoints

| Endpoint               | Description           |
| ---------------------- | --------------------- |
| `/`                    | API status            |
| `/video`               | Live camera stream    |
| `/alert-status`        | Fire alert state      |
| `/evidence/<filename>` | Evidence image access |

## Notes

This repository contains a proof-of-concept prototype developed for an Engineering Technology Innovation Project (ETIP).

This branch contains the **backend vision model system only**. The caregiver dashboard frontend is available separately in the:

```text
caregiver-app
```

branch.

The system is intended for demonstration and research purposes only.
