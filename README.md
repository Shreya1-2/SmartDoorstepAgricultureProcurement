Smart Doorstep Agricultural Procurement

An AI-powered, inclusive, mobile-first agricultural procurement operations prototype designed to help farmers submit
crop collection requests through multiple access channels and enable capacity-aware collection planning, fleet
management, tracking, digital receipts, and payment-status management.

Project Overview

Smart Doorstep Agricultural Procurement is a Streamlit-based prototype that connects farmers, procurement
operations, vehicles, and collection workflows through a unified platform.
The system is designed for farmers who may have:
• Smartphones
• Basic/button phones
• Limited internet connectivity
• No personal digital device
• Need for assisted access through field officers
The prototype supports multiple farmer-access channels and provides an operational dashboard for procurement
teams.

Problem Statement - Farmers often face long waiting times, lack of information regarding procurement schedules, and uncertainty about procurement status.

Proposed Solution:

Our Smart Doorstep Agricultural Procurement System is a Python and Streamlit-based intelligent procurement platform designed to bring the procurement service directly to farmers instead of requiring them to travel to procurement centres. The system provides multiple farmer access channels such as **Tamil voice requests, Touch App, SMS, IVR, Field Officer and Offline Queue**, making the platform accessible even for farmers with limited digital connectivity. The **Request Agent** understands and converts farmer requests into structured procurement information such as crop, quantity, location and collection date. The **Farmer Pool Agent** collects and organizes requests from multiple farmers into a centralized farmer pool. The **Scheduling Agent** analyzes crop quantities, priorities and vehicle capacity to generate capacity-aware collection plans while minimizing the number of vehicles required. The **Fleet Agent** manages available vehicles, drivers, route assignments and vehicle status. Finally, the **Tracking Agent** monitors the complete procurement lifecycle from request received, vehicle assignment and route movement to farmer pickup and collection completion. After successful collection, the system can generate a **digital procurement receipt** containing quantity, price, quality and payment status. Thus, the solution provides an end-to-end digital workflow for **farmer request → farmer pooling → intelligent scheduling → fleet allocation → doorstep collection → tracking → digital receipt and payment status**.

Key Objectives

The main objectives of this project are:
1. Enable farmers to submit agricultural procurement requests easily.
2. Support Tamil voice-based farmer requests.
3. Extract crop, quantity, collection date, and location from voice input.
4. Support multiple farmer-access channels.
5. Maintain a centralized farmer procurement pool.
6. Plan vehicle assignments based on crop quantity and vehicle capacity.
7. Manage vehicles and drivers.
8. Track farmer collection status.
9. Generate digital procurement receipts.
10. Track payment status.
11. Support offline request capture and later synchronization.

System Architecture 
The architecture is provided in the uploaded files.

Technology Stack

Prerequisites

Before running the project, install the following:

Required
• Python 3.9 or later
• pip
• Git (optional)
• A modern web browser
• VS Code or another Python IDE

Recommended
• Python 3.10 / 3.11
• At least 4 GB RAM
• Internet connection for installing dependencies
• Microphone for voice-request testing
• “Whisper's medium model can require significantly more system resources than the basic application itself.

Recommended Project Structure

Smart Doorstep Agricultural Procurement 

Create the project folder with the following structure:
smart-doorstep-agricultural-procurement/
app.py
requirements.txt
README.md

The complete Streamlit code should be saved in:
app.py

Installation & Setup

Step 1 — Clone or Create the Project

If using Git:
git clone <repository-url>

Then move into the project directory:
cd smart-doorstep-agricultural-procurement

If you are creating the project manually, simply create a folder and place app.py inside it.

Step 2 — Create a Virtual Environment

Creating a virtual environment is recommended to keep project dependencies isolated.

Windows
python -m venv venv

Activate it:
venv\Scripts\activate

After activation, the terminal should show something similar to:
(venv)

Step 3 — Upgrade pip
python -m pip install --upgrade pip

Install Dependencies

Create a file named:
requirements.txt

Add:
streamlit
pandas
Pillow
openai-whisper
imageio-ffmpeg
torch

Then install all dependencies:

pip install -r requirements.txt

Smart Doorstep Agricultural Procurement • Page 4

Whisper Setup

The project uses OpenAI Whisper for Tamil voice transcription.

The code contains:
import whisper
and loads:
whisper.load_model("medium")

The application uses Whisper to convert recorded Tamil speech into text.

Example farmer request:

The system attempts to identify:

Crop → nnnn
Quantity → 2 Tons
Date → Tomorrow
Location → Melur

Microphone Requirements

The Touch App uses Streamlit's:

st.audio_input()
Therefore:
1. Open the application in a supported browser.
2. Allow microphone permission.
3. Record the farmer's voice.
4. Stop recording.
5. The audio is sent to Whisper for transcription.

Running the Application

After activating the virtual environment and installing dependencies, run:

streamlit run app.py

Streamlit will display a local URL, normally similar to:
http://localhost:8501

Open that URL in your browser.

Running Without Whisper

The application is designed to continue running even when Whisper is unavailable.
The code checks:

try:

import whisper
WHISPER_AVAILABLE = True
except Exception:
WHISPER_AVAILABLE = False

If Whisper is unavailable:

• The main application can still run.

Smart Doorstep Agricultural Procurement • Page 5

• Dashboard functionality remains available.
• SMS simulator remains available.
• IVR simulator remains available.
• Field Officer workflow remains available.
• Offline Queue remains available.
• Fleet management remains available.
• Tracking remains available.
• Digital receipt workflow remains available.

Only live Whisper-based voice transcription is disabled.

Application Modules

1. Procurement Dashboard
The dashboard displays:
• Active farmers
• Total crop quantity
• Number of locations
• Estimated vehicles required
• Available fleet
• Completed collections
• Offline requests
It also displays the current farmer pool in tabular form.

2. Universal Farmer Access

The system supports five access mechanisms.

Touch App
Provides:
• Tamil voice input
• Whisper transcription
• Crop identification
• Quantity extraction
• Date extraction
• Location detection

SMS Simulator

Supports structured messages such as:
CROP NEL QTY 2 DATE TOM LOCATION MELUR

The system extracts:
Crop → nnnn
Quantity → 2 Tons
Smart Doorstep Agricultural Procurement • Page 6
Date → Tomorrow
Location → Melur

IVR Simulator

Provides a simulated telephone menu with options for:
1 — New Collection Request
2 — Check Request Status
3 — Vehicle Status

Field Officer
A field officer can create a farmer request on behalf of a farmer.
The form supports:
• Farmer name
• Crop
• Quantity
• Collection date
• Village
• Priority

Offline Queue
Requests can be stored locally when connectivity is unavailable.
When connectivity is restored, queued requests can be synchronized into the farmer pool.

3. nnn Farmer Pool
All valid farmer requests are added to a centralized in-memory farmer pool.

Each farmer request contains information such as:
ID
Name
Village
Crop
Quantity
Collection Date
Priority
Source
Request Status

Example:
{
"id": "F001",
"name": "Farmer 1",
"village": "Viraganoor",
"crop": "nnnn",
"quantity": 2,
"date": "Tomorrow",
"priority": "High",
"source": "Demo",
"request_status": "Request Received"
}

4. AI Collection Planning

The planning module calculates a feasible vehicle allocation based on:

• Farmer quantity
• Vehicle capacity

Smart Doorstep Agricultural Procurement • Page 7
• Priority
• Collection date
• Location
• Number of farmers

The main packing function is:
pack_farmers_into_vehicles()

The default vehicle capacity is:
DEFAULT_VEHICLE_CAPACITY = 8

Therefore, each generated route must respect the configured 8-ton capacity.

Vehicle Packing Logic

The system first validates farmer quantities.
If an individual farmer requires more than the configured vehicle capacity, the system raises an error.

The algorithm then:

1. Sorts farmers.
2. Calculates the theoretical minimum number of vehicles.
3. Creates candidate vehicle groups.
4. Uses backtracking to find a feasible allocation.
5. Checks vehicle capacity.
6. Searches for the minimum feasible number of vehicles.
7. Sorts farmers within each route.
8. Returns the generated routes.

Conceptually:

Farmer Requests
↓
Validate Quantities
↓
Sort Requests
↓
Calculate Minimum Vehicles
↓
Backtracking Packing
↓
Capacity Validation
↓
Generated Collection Routes

5. Fleet Management

The prototype contains three default vehicles.

Example fleet:

V001 → TN-01-AB-1234
V002 → TN-01-CD-5678
V003 → TN-01-EF-9012

Each vehicle contains:

Smart Doorstep Agricultural Procurement • Page 8

• Vehicle ID
• Vehicle number
• Capacity
• Driver
• Driver phone
• Status
• Route assignment

Vehicle Lifecycle

The intended vehicle lifecycle is:

Available
↓
Assigned
↓
On Route
↓
Farmer Pickup
↓
Completed

The fleet module allows operators to move vehicles through these statuses.

6. Collection Tracking

The Tracking module connects farmer requests with the collection process.

Farmer request lifecycle:

Request Received
↓
Vehicle Assigned
↓
On Route
↓
Farmer Pickup
↓
Collection Completed

The interface displays completed and pending stages for each selected farmer.

7. Digital Procurement Receipt

After a farmer's status becomes:

Collection Completed

The procurement module allows the operator to generate a digital receipt.

Receipt information includes:

Receipt ID
Procurement ID
Farmer
Crop
Quantity
Quality
Price per Ton
Total Amount
Payment Status
Generated Time

Smart Doorstep Agricultural Procurement • Page 9

Payment Calculation

The total procurement value is calculated using:

Total Amount = Quantity × Price Per Ton

Example:

Quantity = 2 Tons
Price = n22,000 / Ton
Total = 2 × n22,000
Total = n44,000

The prototype supports:

Pending
Processing
Paid
Payment states.

Request ID Generation

Each procurement request receives a unique ID.

Example format:

PROC-A1B2C3D4

The code generates the identifier using UUID:

"PROC-" + str(uuid.uuid4())[:8].upper()

Receipt ID Generation

Digital receipts use a separate identifier.

Example:

REC-A1B2C3D4

Generated using:

"REC-" + str(uuid.uuid4())[:8].upper()

Data Storage

The current prototype primarily uses Streamlit Session State.

For example:

st.session_state.farmer_pool is used to maintain farmer requests during the active application session.

Other session-state objects include:

request_id
crop
quantity
collection_date
farmer_text
location
status
vehicles
offline_queue
receipt_records
generated_routes

Important

Smart Doorstep Agricultural Procurement • Page 10

This prototype does not currently implement a persistent production database.
Therefore, application/session restart can cause in-memory prototype data to be lost.

For production deployment, a persistent database should be introduced.

Security Considerations

The current version is a prototype and should not be treated as a production-secure application.

For production deployment, consider implementing:

• User authentication
• Role-based access control
• Secure password management
• HTTPS
• Database encryption
• API authentication
• Input validation
• Audit logging
• Secure farmer identity management
• Secure payment integration
• Protection of farmer personal information
• Secure secrets/environment-variable management

Do not hard-code production credentials, API keys, database passwords, or payment credentials inside app.py.

Current Prototype Limitations

The current implementation has several prototype-level limitations.

1. In-memory storage
Farmer, vehicle, route, offline queue, and receipt data are maintained using Streamlit session state.

2. SMS is simulated
The SMS module currently processes manually entered text.
A production implementation would require an SMS gateway.

3. IVR is simulated
The IVR workflow is a UI simulation rather than a live telecom integration.

4. Offline queue is simulated
The current offline mechanism stores requests in the application session rather than implementing a true mobile local
database and synchronization protocol.

5. Route optimization is prototype-level

The current packing engine focuses mainly on capacity-aware farmer allocation. A production routing engine should
also consider:

• GPS coordinates

Smart Doorstep Agricultural Procurement • Page 11

• Road distance
• Travel time
• Traffic
• Vehicle availability
• Pickup time windows
• Fuel cost
• Driver working hours

6. Payment is simulated

The payment status is manually selected and does not currently connect to a banking or payment gateway.

7. Location detection

Voice/text location detection currently relies on predefined location aliases.

Production Architecture — Recommended

A production version can evolve toward:

Farmer Applications
↓
Mobile SMS IVR
↓
API Gateway
↓
Authentication Layer
↓
Procurement Backend API
↓
Farmer Service Route Service Fleet Service
↓
Database
↓
Tracking Service Receipt Service Payment Service

Possible production technologies include:

Frontend → Streamlit / React / Mobile App

Backend → FastAPI / Django

Database → PostgreSQL

Cache → Redis

AI → Whisper / Speech API

Maps → Mapping & Routing API

Authentication → OAuth / JWT

Deployment → Docker + Cloud

These are architectural recommendations rather than technologies currently implemented by the prototype.

Demo Workflow

To demonstrate the complete system:

Step 1
Smart Doorstep Agricultural Procurement • Page 12

Start the application:
streamlit run app.py

Step 2
Open:
http://localhost:8501

Step 3
Click:
Load Demo Farmers
This loads the predefined demo farmer dataset.

Step 4
Open:
Dashboard

Review:
• Farmers
• Total crop
• Locations
• Vehicle requirement

Step 5
Open:
AI Planning

Click:
Generate Optimal Collection Routes

Step 6
Open:

Fleet

Assign generated routes to vehicles.

Step 7
Move vehicles through:

Available
→ Assigned
→ On Route
→ Farmer Pickup
→ Completed

Step 8

Open:

Tracking
Select a farmer and update:
Request Received
→ Vehicle Assigned
→ On Route
→ Farmer Pickup

Smart Doorstep Agricultural Procurement • Page 13
→ Collection Completed

Step 9

Open:

Procurement
Select a completed farmer.

Enter:
Procurement Price
Quality
Payment Status
Then click:
Generate Digital Receipt

Testing Checklist
Before demonstrating the project, test the following:

Dashboard
• [ ] Demo farmers load correctly
• [ ] Farmer count is displayed
• [ ] Total quantity is calculated
• [ ] Vehicle requirement is displayed

Touch App
• [ ] Microphone permission works
• [ ] Audio recording works
• [ ] Whisper transcription works
• [ ] Tamil request is processed
• [ ] Crop is detected
• [ ] Quantity is detected
• [ ] Location is detected

SMS
• [ ] SMS format is accepted
• [ ] Crop is detected
• [ ] Quantity is detected
• [ ] Location is detected
• [ ] Request ID is generated

IVR
• [ ] New request works
• [ ] Status lookup works
• [ ] Vehicle status is displayed

Field Officer
• [ ] Farmer request can be created

Smart Doorstep Agricultural Procurement • Page 14

• [ ] Quantity validation works
• [ ] Request ID is generated

Offline Queue

• [ ] Request can be stored
• [ ] Queue is displayed
• [ ] Synchronization works

AI Planning

• [ ] Routes are generated
• [ ] Vehicle capacity is respected
• [ ] Farmers are assigned
• [ ] Duplicate assignment validation works

Fleet

• [ ] Routes can be assigned
• [ ] Vehicle status changes
• [ ] Driver information is displayed

Tracking

• [ ] Farmer can be selected
• [ ] Collection status can be updated

Procurement

• [ ] Completed farmers are shown
• [ ] Total procurement value is calculated
• [ ] Receipt is generated
• [ ] Payment status is displayed

Troubleshooting

Streamlit command not found

Try:
python -m streamlit run app.py

Python command not found

Verify Python installation:
python --version

or:

py --version

Whisper installation error

Smart Doorstep Agricultural Procurement • Page 15

Upgrade pip:
python -m pip install --upgrade pip

Then install:
pip install openai-whisper

If required, install PyTorch separately according to your system configuration.

FFmpeg-related issue

The project uses:
imageio-ffmpeg

Install it using:
pip install imageio-ffmpeg

The application attempts to add the bundled FFmpeg executable to the system PATH at runtime.

Microphone not working

Check:
1. Browser microphone permission.
2. Windows microphone permission.
3. Correct microphone device.
4. Browser security settings.
5. Whether the application is running through a supported browser.

Application does not start

Try:
python -m streamlit run app.py

If an error appears, check the Python traceback in the terminal.

Resetting the Prototype

The sidebar contains:
Clear Farmer Pool

This clears the current farmer pool and related prototype data.

For a fresh demonstration, use:
Load Demo Farmers

Future Enhancements

Potential future improvements include:
• Real farmer authentication
• PostgreSQL database

Smart Doorstep Agricultural Procurement • Page 16
• Real SMS gateway
• Real IVR integration
• Mobile application
• GPS-based farmer locations
• Real-time vehicle tracking
• Google Maps / OpenStreetMap routing
• Advanced route optimization
• Weather-aware collection planning
• Crop price integration
• Digital payment gateway
• Automated receipt PDF generation
• Multilingual voice processing
• Offline-first mobile architecture
• Push notifications
• Procurement analytics
• Admin and farmer role management
• Cloud deployment
• Docker containerization
• API-based architecture

Core Data Flow

Farmer
↓
Access Channel
↓
Touch App
↓
↓
IVR
↓
Field Officer
↓
Offline Queue
↓
Request Processing
↓
Crop + Quantity + Date + Location
↓
Farmer Pool
↓
Capacity-Aware Planning
↓
Vehicle Assignment
↓
Collection Tracking
↓
Collection Completed
↓
Digital Receipt
↓
Payment Status

Smart Doorstep Agricultural Procurement • Page 17

AI Components

The current prototype contains two major AI-oriented components.

1. Speech Recognition

Whisper is used to convert Tamil voice input into text.
Tamil Speech
↓
Whisper
↓
Tamil Text
↓
Request Parser
↓
Structured Procurement Request

2. Collection Planning

The route planning component evaluates farmer requests and vehicle capacity to generate feasible vehicle groupings.
Farmer Demand
↓
Priority + Date + Location + Quantity
↓
Capacity Constraint
↓
Packing / Backtracking
↓
Collection Routes

License
Add the project's applicable license here.

Example:

This project is developed as a prototype for demonstration and
academic/hackathon purposes.

Project Information

Project Name:

Smart Doorstep Agricultural Procurement

Application Type:

AI-powered agricultural procurement operations prototype

Platform:

Streamlit Web Application

Primary Language:

Python
AI Technology:
Whisper Speech Recognition + rule-based request parsing + capacity-aware planning

Conclusion
Smart Doorstep Agricultural Procurement • Page 18
The Smart Doorstep Agricultural Procurement prototype provides a unified workflow for collecting farmer procurement
requests through multiple access channels, consolidating farmer demand, planning capacity-aware vehicle routes,
managing fleet operations, tracking collection progress, and generating digital procurement receipts with payment
status.
The current implementation is suitable as a prototype/demo architecture. For production deployment, persistent
storage, authentication, real communication gateways, GPS/routing services, secure payment integration, and scalable
