# Caregiver Dashboard App

Frontend caregiver dashboard for the ETIP dementia care prototype.

This application allows caregivers to monitor task completion, alerts, and evidence captured by the patient-side system.

## Before Running

This project assumes the following are already installed and working:

* Node.js
* npm
* Existing backend / patient-side system setup

If these are already configured from previous project setup, no additional installation should be required beyond the commands below.

---

## Setup

Install dependencies:

```bash
npm install
```

Run the application:

```bash
npm run dev
```

You should receive a local Vite link in terminal similar to:

```text
http://localhost:5173
```

Open this in a browser.

---

## Supabase Setup

Open:

```text
src/supabase.js
```

Replace:

```javascript
const supabaseUrl = 'Insert URL';
const supabaseAnonKey = 'Insert Supabase Key';
```

with the correct:

* Supabase Project URL
* Supabase Anon Public Key

These can be found in:

```text
Supabase Dashboard
→ Settings
→ API
```

**Note:**
Use the **anon public key only**. Do not use the service role key.

---

## Network Requirement

For the caregiver dashboard and patient-side application to communicate correctly, both devices should be connected to the **same local network**.

Recommended:

* Mobile hotspot
* Home Wi-Fi
* Local router network

**Do not use Eduroam**, as device-to-device communication may be restricted and the live connection may fail.

Example setup:

```text
Laptop 1 → Patient-side application
Laptop 2 → Caregiver dashboard

Both connected to same Wi-Fi / hotspot
```

---

## Tech Stack

* Vue
* Vite
* JavaScript
* Supabase

---

## Notes

This was developed as a prototype for ETIP Group 4.

Some functionality depends on:

* Supabase configuration
* Database setup
* Evidence image storage
* Patient-side detection system being active
