# ============================================================
# SMART DOORSTEP AGRICULTURAL PROCUREMENT
# Complete SIH Prototype
#
# Features:
# 1. Farmer Dashboard
# 2. Tamil Voice Request using Whisper
# 3. Location Detection
# 4. Farmer Pool
# 5. AI Capacity-Aware Route Planning
# 6. Vehicle + Driver Management
# 7. Vehicle Status Lifecycle
# 8. Universal Farmer Access Gateway
#    - Touch App
#    - SMS Simulator
#    - IVR Simulator
#    - Field Officer
#    - Offline Queue Simulator
# 9. Procurement Tracking
# 10. Digital Receipt
# 11. Payment Status
# ============================================================

import os
import tempfile
import hashlib
import uuid
from datetime import datetime
from math import ceil

import streamlit as st
import pandas as pd

from PIL import Image, ImageStat, ImageFilter

# ============================================================
# OPTIONAL AI IMPORTS
# ============================================================

try:
    import whisper

    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False

try:
    import imageio_ffmpeg

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_folder = os.path.dirname(ffmpeg_path)

    os.environ["PATH"] = ffmpeg_folder + os.pathsep + os.environ.get("PATH", "")

    FFMPEG_AVAILABLE = True

except Exception:
    FFMPEG_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Doorstep Agricultural Procurement",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_VEHICLE_CAPACITY = 8

PRIORITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2,
}

VEHICLE_STATUS_FLOW = [
    "Available",
    "Assigned",
    "On Route",
    "Farmer Pickup",
    "Completed",
]


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 17px;
        color: #667085;
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 26px;
        font-weight: 750;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .small-title {
        font-size: 19px;
        font-weight: 700;
    }

    .metric-card {
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #e4e7ec;
        background: white;
        min-height: 115px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .metric-title {
        font-size: 14px;
        color: #667085;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 800;
        margin-top: 7px;
    }

    .route-box {
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #d0d5dd;
        background: #fcfcfd;
        margin-bottom: 14px;
    }

    .ai-box {
        padding: 17px;
        border-radius: 14px;
        border: 1px solid #b9d7f5;
        background: #f3f9ff;
        margin-bottom: 15px;
    }

    .gateway-card {
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #e4e7ec;
        background: #ffffff;
        min-height: 150px;
        margin-bottom: 10px;
    }

    .status-box {
        padding: 12px;
        border-radius: 12px;
        background: #f8fafc;
        border: 1px solid #e4e7ec;
        margin-bottom: 8px;
    }

    .success-box {
        padding: 14px;
        border-radius: 12px;
        background: #ecfdf3;
        border: 1px solid #abefc6;
        margin-bottom: 10px;
    }

    .warning-box {
        padding: 14px;
        border-radius: 12px;
        background: #fffaeb;
        border: 1px solid #fedf89;
        margin-bottom: 10px;
    }

    .danger-box {
        padding: 14px;
        border-radius: 12px;
        background: #fef3f2;
        border: 1px solid #fecdca;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

defaults = {
    "request_id": None,
    "crop": None,
    "quantity": None,
    "collection_date": None,
    "farmer_text": None,
    "location": None,
    "status": "Request Received",
    "processed_audio": None,
    "farmer_pool": [],
    "route_generated": False,
    "generated_routes": [],
    "route_generated_at": None,
    "vehicles": [],
    "offline_queue": [],
    "sms_result": None,
    "ivr_result": None,
    "field_result": None,
    "selected_gateway": "📱 Touch App",
    "receipt_records": [],
    "active_tracking": {},
    "demo_loaded": False,
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# VEHICLE DATABASE
# ============================================================

DEFAULT_VEHICLES = [
    {
        "id": "V001",
        "number": "TN-01-AB-1234",
        "capacity": 8,
        "driver": "Driver 1",
        "phone": "9000000001",
        "status": "Available",
        "route_index": None,
    },
    {
        "id": "V002",
        "number": "TN-01-CD-5678",
        "capacity": 10,
        "driver": "Driver 2",
        "phone": "9000000002",
        "status": "Available",
        "route_index": None,
    },
    {
        "id": "V003",
        "number": "TN-01-EF-9012",
        "capacity": 8,
        "driver": "Driver 3",
        "phone": "9000000003",
        "status": "Available",
        "route_index": None,
    },
]


# ============================================================
# DEMO FARMERS
# ============================================================

DEMO_FARMERS = [
    {
        "id": "F001",
        "name": "Farmer 1",
        "village": "Viraganoor",
        "crop": "நெல்",
        "quantity": 2,
        "date": "Tomorrow",
        "priority": "High",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F002",
        "name": "Farmer 2",
        "village": "Viraganoor",
        "crop": "நெல்",
        "quantity": 1,
        "date": "Tomorrow",
        "priority": "High",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F003",
        "name": "Farmer 3",
        "village": "Sakkimangalam",
        "crop": "நெல்",
        "quantity": 2,
        "date": "Tomorrow",
        "priority": "Medium",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F004",
        "name": "Farmer 4",
        "village": "Sakkimangalam",
        "crop": "நெல்",
        "quantity": 1,
        "date": "Tomorrow",
        "priority": "Medium",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F005",
        "name": "Farmer 5",
        "village": "Silaiman",
        "crop": "நெல்",
        "quantity": 3,
        "date": "Tomorrow",
        "priority": "High",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F006",
        "name": "Farmer 6",
        "village": "Avaniyapuram",
        "crop": "கோதுமை",
        "quantity": 2,
        "date": "Tomorrow",
        "priority": "Medium",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F007",
        "name": "Farmer 7",
        "village": "Thiruppalai",
        "crop": "சோளம்",
        "quantity": 2,
        "date": "Tomorrow",
        "priority": "Medium",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F008",
        "name": "Farmer 8",
        "village": "Othakadai",
        "crop": "நெல்",
        "quantity": 2,
        "date": "Today",
        "priority": "High",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F009",
        "name": "Farmer 9",
        "village": "Melur",
        "crop": "நெல்",
        "quantity": 1,
        "date": "Tomorrow",
        "priority": "High",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F010",
        "name": "Farmer 10",
        "village": "Kappalur",
        "crop": "பருத்தி",
        "quantity": 3,
        "date": "Tomorrow",
        "priority": "Medium",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F011",
        "name": "Farmer 11",
        "village": "Thirumangalam",
        "crop": "நெல்",
        "quantity": 2,
        "date": "Tomorrow",
        "priority": "High",
        "source": "Demo",
        "request_status": "Request Received",
    },
    {
        "id": "F012",
        "name": "Farmer 12",
        "village": "Samayanallur",
        "crop": "நெல்",
        "quantity": 2,
        "date": "Tomorrow",
        "priority": "Medium",
        "source": "Demo",
        "request_status": "Request Received",
    },
]


# ============================================================
# LOCATION ALIASES
# ============================================================

LOCATION_ALIASES = {
    "Viraganoor": [
        "viraganoor",
        "விரகனூர்",
        "விரகனூரில்",
    ],
    "Sakkimangalam": [
        "sakkimangalam",
        "சக்கிமங்கலம்",
        "சக்கிமங்கலத்தில்",
    ],
    "Silaiman": [
        "silaiman",
        "சிலைமான்",
        "சிலைமானில்",
    ],
    "Avaniyapuram": [
        "avaniyapuram",
        "அவனியாபுரம்",
        "அவனியாபுரத்தில்",
    ],
    "Thiruppalai": [
        "thiruppalai",
        "திருப்பாலை",
        "திருப்பாலையில்",
    ],
    "Othakadai": [
        "othakadai",
        "ஒத்தக்கடை",
        "ஒத்தக்கடையில்",
    ],
    "Melur": [
        "melur",
        "மேலூர்",
        "மேலூரில்",
        "மேலூரில",
        "மேலூருக்கு",
    ],
    "Kappalur": [
        "kappalur",
        "கப்பலூர்",
        "கப்பலூரில்",
    ],
    "Thirumangalam": [
        "thirumangalam",
        "திருமங்கலம்",
        "திருமங்கலத்தில்",
    ],
    "Samayanallur": [
        "samayanallur",
        "சமயநல்லூர்",
        "சமயநல்லூரில்",
    ],
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def get_quantity(farmer):

    try:
        return float(farmer.get("quantity", 0) or 0)

    except (TypeError, ValueError):

        return 0.0


def get_priority(farmer):

    return farmer.get(
        "priority",
        "Medium",
    )


def get_village(farmer):

    return (
        farmer.get("village")
        or farmer.get("Village")
        or farmer.get("location")
        or farmer.get("Location")
        or "Unknown Location"
    )


def get_collection_date(farmer):

    return (
        farmer.get("date")
        or farmer.get("Date")
        or farmer.get("collection_date")
        or farmer.get("Collection Date")
        or "Not Scheduled"
    )


def get_total_quantity(farmers):

    return sum(get_quantity(farmer) for farmer in farmers)


def reset_routes():

    st.session_state.route_generated = False

    st.session_state.generated_routes = []

    st.session_state.route_generated_at = None

    for vehicle in st.session_state.vehicles:

        vehicle["status"] = "Available"
        vehicle["route_index"] = None


def add_farmer_to_pool(farmer):

    st.session_state.farmer_pool.append(farmer)

    reset_routes()


def create_request_id():

    return "PROC-" + str(uuid.uuid4())[:8].upper()


# ============================================================
# EXACT VEHICLE PACKING
# ============================================================


def pack_farmers_into_vehicles(
    farmers,
    capacity=DEFAULT_VEHICLE_CAPACITY,
):

    valid_farmers = []

    for farmer in farmers:

        quantity = get_quantity(farmer)

        if quantity <= 0:
            continue

        if quantity > capacity:

            raise ValueError(
                f"{farmer.get('id', 'Unknown farmer')} "
                f"requires {quantity:g} tons, exceeding "
                f"the {capacity:g}-ton capacity."
            )

        valid_farmers.append(farmer)

    if not valid_farmers:
        return []

    sorted_farmers = sorted(
        valid_farmers,
        key=lambda farmer: (
            -get_quantity(farmer),
            PRIORITY_ORDER.get(
                get_priority(farmer),
                1,
            ),
            0 if get_collection_date(farmer) == "Today" else 1,
            get_village(farmer),
            farmer.get("id", ""),
        ),
    )

    total_quantity = sum(get_quantity(farmer) for farmer in sorted_farmers)

    theoretical_minimum = max(
        1,
        ceil(total_quantity / capacity),
    )

    def find_packing(vehicle_count):

        vehicles = [
            {
                "farmers": [],
                "load": 0.0,
            }
            for _ in range(vehicle_count)
        ]

        def backtrack(index):

            if index == len(sorted_farmers):
                return True

            farmer = sorted_farmers[index]

            quantity = get_quantity(farmer)

            used_loads = set()

            for vehicle in vehicles:

                current_load = vehicle["load"]

                if current_load in used_loads:
                    continue

                used_loads.add(current_load)

                if current_load + quantity <= capacity:

                    vehicle["farmers"].append(farmer)

                    vehicle["load"] += quantity

                    if backtrack(index + 1):
                        return True

                    vehicle["farmers"].pop()

                    vehicle["load"] -= quantity

            return False

        if backtrack(0):
            return vehicles

        return None

    for vehicle_count in range(
        theoretical_minimum,
        len(sorted_farmers) + 1,
    ):

        result = find_packing(vehicle_count)

        if result is not None:

            result = [vehicle for vehicle in result if vehicle["farmers"]]

            for vehicle in result:

                vehicle["farmers"].sort(
                    key=lambda farmer: (
                        PRIORITY_ORDER.get(
                            get_priority(farmer),
                            1,
                        ),
                        0 if get_collection_date(farmer) == "Today" else 1,
                        get_village(farmer),
                        farmer.get(
                            "id",
                            "",
                        ),
                    )
                )

                vehicle["load"] = sum(
                    get_quantity(farmer) for farmer in vehicle["farmers"]
                )

            return result

    return []


# ============================================================
# INITIALIZE VEHICLES
# ============================================================

if not st.session_state.vehicles:

    st.session_state.vehicles = [vehicle.copy() for vehicle in DEFAULT_VEHICLES]


# ============================================================
# WHISPER MODEL
# ============================================================


@st.cache_resource
def load_whisper_model():

    if not WHISPER_AVAILABLE:

        raise RuntimeError("Whisper is not installed.")

    return whisper.load_model("medium")


# ============================================================
# REQUEST PARSER
# ============================================================


def parse_farmer_text(text):

    text_lower = text.lower().strip()

    # --------------------------------------------------------
    # Crop
    # --------------------------------------------------------

    if "நெல்" in text or "paddy" in text_lower or "rice" in text_lower:

        crop = "நெல்"

    elif "கோதுமை" in text or "wheat" in text_lower:

        crop = "கோதுமை"

    elif "சோளம்" in text or "maize" in text_lower or "corn" in text_lower:

        crop = "சோளம்"

    elif "பருத்தி" in text or "cotton" in text_lower:

        crop = "பருத்தி"

    else:

        crop = "To be identified"

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    if (
        "மூன்று டன்" in text
        or "3 டன்" in text
        or "3 ton" in text_lower
        or "3 tons" in text_lower
    ):

        quantity = 3

    elif (
        "இரண்டு டன்" in text
        or "2 டன்" in text
        or "2 ton" in text_lower
        or "2 tons" in text_lower
    ):

        quantity = 2

    elif (
        "ஒரு டன்" in text
        or "1 டன்" in text
        or "1 ton" in text_lower
        or "1 tons" in text_lower
    ):

        quantity = 1

    else:

        quantity = 0

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    if "நாளைக்கு" in text or "நாளை" in text or "tomorrow" in text_lower:

        collection_date = "Tomorrow"

    elif "இன்று" in text or "today" in text_lower:

        collection_date = "Today"

    else:

        collection_date = "To be scheduled"

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    detected_location = "To be selected"

    for location, aliases in LOCATION_ALIASES.items():

        for alias in aliases:

            if alias.lower() in text_lower:

                detected_location = location

                break

        if detected_location != "To be selected":

            break

    return (
        crop,
        quantity,
        collection_date,
        detected_location,
    )


# ============================================================
# ADD STRUCTURED REQUEST
# ============================================================


def add_structured_request(
    name,
    crop,
    quantity,
    date,
    location,
    source,
    priority="High",
):

    request_id = create_request_id()

    farmer = {
        "id": request_id,
        "name": name,
        "village": location,
        "crop": crop,
        "quantity": float(quantity),
        "date": date,
        "priority": priority,
        "source": source,
        "request_status": "Request Received",
    }

    add_farmer_to_pool(farmer)

    st.session_state.request_id = request_id

    st.session_state.crop = crop

    st.session_state.quantity = float(quantity)

    st.session_state.collection_date = date

    st.session_state.location = location

    st.session_state.status = "Request Received"

    return request_id


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">' "🌾 Smart Doorstep Agricultural Procurement" "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered, inclusive and mobile-first agricultural procurement operations platform"
    "</div>",
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌾 Procurement Control")

st.sidebar.caption("AI-powered procurement operations")


if st.sidebar.button(
    "📊 Load Demo Farmers",
    use_container_width=True,
):

    st.session_state.farmer_pool = [farmer.copy() for farmer in DEMO_FARMERS]

    st.session_state.vehicles = [vehicle.copy() for vehicle in DEFAULT_VEHICLES]

    reset_routes()

    st.session_state.demo_loaded = True

    st.sidebar.success("12 demo farmers loaded.")

    st.rerun()


if st.sidebar.button(
    "🗑️ Clear Farmer Pool",
    use_container_width=True,
):

    st.session_state.farmer_pool = []

    st.session_state.receipt_records = []

    st.session_state.request_id = None

    st.session_state.status = "Request Received"

    st.session_state.offline_queue = []

    reset_routes()

    st.sidebar.success("Farmer pool cleared.")

    st.rerun()


st.sidebar.divider()

st.sidebar.markdown("**Prototype Modules**")

st.sidebar.write("📱 Universal Farmer Access")

st.sidebar.write("🤖 AI Request Processing")

st.sidebar.write("👨‍🌾 Farmer Pool")

st.sidebar.write("🧠 AI Route Planning")

st.sidebar.write("🚛 Fleet Management")

st.sidebar.write("📍 Collection Tracking")

st.sidebar.write("🧾 Receipt & Payment Status")


# ============================================================
# MAIN TABS
# ============================================================

tabs = st.tabs(
    [
        "📊 Dashboard",
        "📱 Farmer Access",
        "🤖 AI Planning",
        "🚛 Fleet",
        "📍 Tracking",
        "🧾 Procurement",
    ]
)


# ============================================================
# TAB 1 — DASHBOARD
# ============================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">' "📊 Procurement Command Dashboard" "</div>",
        unsafe_allow_html=True,
    )

    farmers = st.session_state.farmer_pool

    total_farmers = len(farmers)

    total_quantity = get_total_quantity(farmers)

    unique_locations = len({get_village(farmer) for farmer in farmers})

    try:

        preview_routes = pack_farmers_into_vehicles(farmers)

        estimated_vehicles = len(preview_routes)

    except ValueError:

        estimated_vehicles = 0

    available_vehicles = sum(
        1 for vehicle in st.session_state.vehicles if vehicle["status"] == "Available"
    )

    completed_count = sum(
        1
        for farmer in farmers
        if farmer.get("request_status") == "Collection Completed"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    👨‍🌾 Active Farmers
                </div>
                <div class="metric-value">
                    {total_farmers}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    ⚖️ Total Crop
                </div>
                <div class="metric-value">
                    {total_quantity:g} Tons
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    📍 Locations
                </div>
                <div class="metric-value">
                    {unique_locations}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    🚜 Vehicles Required
                </div>
                <div class="metric-value">
                    {estimated_vehicles}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "🚛 Fleet Available",
            available_vehicles,
        )

    with c2:

        st.metric(
            "🟢 Collections Completed",
            completed_count,
        )

    with c3:

        st.metric(
            "📴 Offline Queue",
            len(st.session_state.offline_queue),
        )

    st.divider()

    st.subheader("👨‍🌾 Current Farmer Pool")

    if farmers:

        display_data = []

        for farmer in farmers:

            display_data.append(
                {
                    "ID": farmer.get(
                        "id",
                        "",
                    ),
                    "Name": farmer.get(
                        "name",
                        "",
                    ),
                    "Village": get_village(farmer),
                    "Crop": farmer.get(
                        "crop",
                        "",
                    ),
                    "Quantity (Tons)": get_quantity(farmer),
                    "Date": get_collection_date(farmer),
                    "Priority": get_priority(farmer),
                    "Source": farmer.get(
                        "source",
                        "Demo",
                    ),
                    "Status": farmer.get(
                        "request_status",
                        "Request Received",
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(display_data),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No farmers loaded. " "Use 'Load Demo Farmers' from the sidebar.")


# ============================================================
# TAB 2 — UNIVERSAL FARMER ACCESS
# ============================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">' "📱 Universal Farmer Access Gateway" "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "The same procurement service can be accessed through "
        "smartphone, button phone, assisted field service or "
        "offline capture."
    )

    g1, g2, g3, g4 = st.columns(4)

    with g1:

        st.markdown(
            """
            <div class="gateway-card">
                <h3>📱 Touch App</h3>
                <p>Voice + digital request</p>
                <b>✅ Active</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with g2:

        st.markdown(
            """
            <div class="gateway-card">
                <h3>💬 SMS</h3>
                <p>Button phone access</p>
                <b>🟢 Prototype Ready</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with g3:

        st.markdown(
            """
            <div class="gateway-card">
                <h3>☎️ IVR</h3>
                <p>Voice menu for basic phones</p>
                <b>🟢 Prototype Ready</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with g4:

        st.markdown(
            """
            <div class="gateway-card">
                <h3>👨‍🌾 Field Officer</h3>
                <p>Assisted farmer access</p>
                <b>🟢 Prototype Ready</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    gateway = st.radio(
        "Choose Farmer Access Channel",
        [
            "📱 Touch App",
            "💬 SMS Simulator",
            "☎️ IVR Simulator",
            "👨‍🌾 Field Officer",
            "📴 Offline Queue",
        ],
        horizontal=True,
    )

    st.divider()

    # --------------------------------------------------------
    # TOUCH APP
    # --------------------------------------------------------

    if gateway == "📱 Touch App":

        st.subheader("🎙️ Tamil Voice Procurement Request")

        st.write("Farmer can speak naturally in Tamil.")

        if not WHISPER_AVAILABLE:

            st.warning(
                "Whisper is not installed in the current "
                "environment. Install it to enable live "
                "voice transcription."
            )

        audio = st.audio_input("🎤 Record Farmer Requirement")

        if audio is not None:

            audio_bytes = audio.getvalue()

            audio_hash = hashlib.md5(audio_bytes).hexdigest()

            if audio_hash != st.session_state.processed_audio:

                st.session_state.processed_audio = audio_hash

                st.audio(audio_bytes)

                if not WHISPER_AVAILABLE:

                    st.error("Whisper is unavailable.")

                else:

                    audio_path = None

                    with st.spinner("🤖 AI is understanding the farmer request..."):

                        try:

                            with tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=".wav",
                            ) as temp_audio:

                                temp_audio.write(audio_bytes)

                                audio_path = temp_audio.name

                            model = load_whisper_model()

                            result = model.transcribe(
                                audio_path,
                                language="ta",
                                task="transcribe",
                                fp16=False,
                                temperature=0,
                                beam_size=5,
                                best_of=5,
                                condition_on_previous_text=False,
                                initial_prompt=(
                                    "தமிழ் விவசாயி பயிர் கொள்முதல் கோரிக்கை. "
                                    "இரண்டு டன் நெல் நாளைக்கு "
                                    "மேலூரில் தயாராக உள்ளது."
                                ),
                            )

                            text = result["text"].strip()

                            (
                                crop,
                                quantity,
                                collection_date,
                                detected_location,
                            ) = parse_farmer_text(text)
                            request_id = create_request_id()

                            st.session_state.request_id = request_id

                            st.session_state.crop = crop

                            st.session_state.quantity = quantity

                            st.session_state.collection_date = collection_date

                            st.session_state.farmer_text = text

                            st.session_state.location = detected_location

                            st.session_state.status = "Request Received"

                            st.success(
                                "🤖 AI successfully processed the voice request."
                            )

                            st.write(f"**Recognized Speech:** {text}")

                            a, b, c, d = st.columns(4)

                            with a:
                                st.metric(
                                    "🌾 Crop",
                                    crop,
                                )

                            with b:
                                st.metric(
                                    "⚖️ Quantity",
                                    f"{quantity} Tons",
                                )

                            with c:
                                st.metric(
                                    "📅 Collection",
                                    collection_date,
                                )

                            with d:
                                st.metric(
                                    "📍 Location",
                                    detected_location,
                                )

                            if (
                                detected_location != "To be selected"
                                and quantity > 0
                                and crop != "To be identified"
                            ):

                                new_farmer = {
                                    "id": request_id,
                                    "name": "Voice Farmer",
                                    "village": detected_location,
                                    "crop": crop,
                                    "quantity": quantity,
                                    "date": collection_date,
                                    "priority": "High",
                                    "source": "Voice App",
                                    "request_status": "Request Received",
                                }

                                add_farmer_to_pool(new_farmer)

                                st.success(
                                    "👨‍🌾 Farmer added to the procurement pool."
                                )

                            else:

                                st.warning(
                                    "Location, crop or quantity "
                                    "could not be fully detected."
                                )

                        except Exception as e:

                            st.error("Voice processing failed.")

                            st.code(str(e))

                        finally:

                            if audio_path and os.path.exists(audio_path):

                                try:

                                    os.remove(audio_path)

                                except OSError:

                                    pass

    # --------------------------------------------------------
    # SMS SIMULATOR
    # --------------------------------------------------------

    elif gateway == "💬 SMS Simulator":

        st.subheader("💬 Button Phone — SMS Procurement")

        st.info("Prototype SMS format: " "CROP NEL QTY 2 DATE TOM LOCATION MELUR")

        sms_text = st.text_input(
            "📨 Enter Farmer SMS",
            value=("CROP NEL QTY 2 " "DATE TOM LOCATION MELUR"),
        )

        if st.button(
            "🤖 Process SMS Request",
            type="primary",
            use_container_width=True,
        ):

            text = sms_text.lower()

            # Crop
            if "nel" in text or "paddy" in text or "rice" in text:
                crop = "நெல்"

            elif "wheat" in text:
                crop = "கோதுமை"

            elif "maize" in text or "corn" in text:
                crop = "சோளம்"

            elif "cotton" in text:
                crop = "பருத்தி"

            else:
                crop = "To be identified"

            # Quantity
            quantity = 0

            for number in [
                3,
                2,
                1,
            ]:

                if (
                    f"qty {number}" in text
                    or f"qty={number}" in text
                    or f"quantity {number}" in text
                ):

                    quantity = number

                    break

            # Date
            if "tom" in text or "tomorrow" in text:

                date = "Tomorrow"

            elif "today" in text:

                date = "Today"

            else:

                date = "To be scheduled"

            # Location
            location = "To be selected"

            for loc in LOCATION_ALIASES:

                if loc.lower() in text:

                    location = loc

                    break

            if location == "To be selected":

                for loc, aliases in LOCATION_ALIASES.items():

                    for alias in aliases:

                        if alias.lower() in text:

                            location = loc

                            break

                    if location != "To be selected":
                        break

            if (
                crop != "To be identified"
                and quantity > 0
                and location != "To be selected"
            ):

                request_id = add_structured_request(
                    "SMS Farmer",
                    crop,
                    quantity,
                    date,
                    location,
                    "SMS",
                )

                st.session_state.sms_result = {
                    "id": request_id,
                    "crop": crop,
                    "quantity": quantity,
                    "date": date,
                    "location": location,
                }

                st.success("📨 SMS request accepted successfully.")

                st.code(f"""
SMS RESPONSE

Request ID: {request_id}
Crop: {crop}
Quantity: {quantity} Tons
Location: {location}
Collection: {date}

Vehicle will be assigned.
                    """)

            else:

                st.warning(
                    "Could not understand the SMS format. "
                    "Please use the example format."
                )

        st.caption(
            "This is a prototype SMS simulator. "
            "Production deployment can connect it to an SMS gateway."
        )

    # --------------------------------------------------------
    # IVR SIMULATOR
    # --------------------------------------------------------

    elif gateway == "☎️ IVR Simulator":

        st.subheader("☎️ Button Phone — IVR Procurement")

        st.info("Prototype simulation of a Tamil IVR call.")

        language = st.selectbox(
            "🌐 Language",
            [
                "Tamil",
                "English",
            ],
        )

        st.write("### ☎️ IVR Menu")

        menu = st.radio(
            "Select IVR Action",
            [
                "1 — New Collection Request",
                "2 — Check Request Status",
                "3 — Vehicle Status",
            ],
        )

        if menu == "1 — New Collection Request":

            crop = st.selectbox(
                "🌾 Select Crop",
                [
                    "நெல்",
                    "கோதுமை",
                    "சோளம்",
                    "பருத்தி",
                ],
            )

            quantity = st.selectbox(
                "⚖️ Quantity",
                [
                    1,
                    2,
                    3,
                ],
            )

            date = st.selectbox(
                "📅 Collection",
                [
                    "Today",
                    "Tomorrow",
                ],
            )

            location = st.selectbox(
                "📍 Village",
                list(LOCATION_ALIASES.keys()),
            )

            if st.button(
                "☎️ Submit IVR Request",
                type="primary",
                use_container_width=True,
            ):

                request_id = add_structured_request(
                    "IVR Farmer",
                    crop,
                    quantity,
                    date,
                    location,
                    "IVR",
                )

                st.session_state.ivr_result = {
                    "id": request_id,
                    "crop": crop,
                    "quantity": quantity,
                    "date": date,
                    "location": location,
                }

                if language == "Tamil":

                    st.success(f"""
உங்கள் கொள்முதல் கோரிக்கை பதிவு செய்யப்பட்டுள்ளது.

கோரிக்கை எண்: {request_id}

பயிர்: {crop}
அளவு: {quantity} டன்
இடம்: {location}
தேதி: {date}
""")

                else:

                    st.success(f"""
Request registered successfully.

Request ID: {request_id}

Crop: {crop}
Quantity: {quantity} Tons
Location: {location}
Collection: {date}
""")

        elif menu == "2 — Check Request Status":

            request_lookup = st.text_input(
                "Enter Request ID",
                value=(st.session_state.request_id or "PROC-DEMO"),
            )

            if st.button(
                "🔎 Check Status",
                use_container_width=True,
            ):

                found = None

                for farmer in st.session_state.farmer_pool:

                    if farmer.get("id") == request_lookup:

                        found = farmer

                        break

                if found:

                    st.success(
                        f"Status: {found.get('request_status', 'Request Received')}"
                    )

                else:

                    st.info("Request ID not found in current prototype pool.")

        else:

            st.info(
                "☎️ Vehicle status can be announced "
                "through a production IVR integration."
            )

            for vehicle in st.session_state.vehicles:

                st.write(f"🚛 {vehicle['number']} — " f"{vehicle['status']}")

        st.caption(
            "This is a prototype IVR simulator. "
            "Production deployment can connect it to a telecom IVR service."
        )

    # --------------------------------------------------------
    # FIELD OFFICER
    # --------------------------------------------------------

    elif gateway == "👨‍🌾 Field Officer":

        st.subheader("👨‍🌾 Assisted Farmer Access")

        st.info(
            "For farmers without smartphones or phones, "
            "a field officer / cooperative / village officer "
            "can create the request."
        )

        with st.form("field_officer_form"):

            farmer_name = st.text_input(
                "Farmer Name",
                value="Assisted Farmer",
            )

            crop = st.selectbox(
                "Crop",
                [
                    "நெல்",
                    "கோதுமை",
                    "சோளம்",
                    "பருத்தி",
                ],
            )

            quantity = st.number_input(
                "Quantity (Tons)",
                min_value=0.5,
                max_value=10.0,
                value=2.0,
                step=0.5,
            )

            date = st.selectbox(
                "Collection Date",
                [
                    "Today",
                    "Tomorrow",
                ],
            )

            location = st.selectbox(
                "Village",
                list(LOCATION_ALIASES.keys()),
            )

            priority = st.selectbox(
                "Priority",
                [
                    "High",
                    "Medium",
                    "Low",
                ],
            )

            submit = st.form_submit_button(
                "👨‍🌾 Create Farmer Request",
                use_container_width=True,
            )

        if submit:

            if quantity > 8:

                st.error("Demo fleet capacity limit is 8 tons.")

            else:

                request_id = add_structured_request(
                    farmer_name,
                    crop,
                    quantity,
                    date,
                    location,
                    "Field Officer",
                    priority,
                )

                st.session_state.field_result = request_id

                st.success(
                    f"Farmer request created successfully. " f"Request ID: {request_id}"
                )

    # --------------------------------------------------------
    # OFFLINE QUEUE
    # --------------------------------------------------------

    else:

        st.subheader("📴 Offline Request Queue")

        st.info(
            "When connectivity is unavailable, an assisted "
            "request can be placed in a local queue and "
            "synchronized when connectivity returns."
        )

        col1, col2 = st.columns(2)

        with col1:

            offline_name = st.text_input(
                "Farmer Name",
                value="Offline Farmer",
            )

            offline_crop = st.selectbox(
                "Crop",
                [
                    "நெல்",
                    "கோதுமை",
                    "சோளம்",
                    "பருத்தி",
                ],
                key="offline_crop",
            )

        with col2:

            offline_quantity = st.number_input(
                "Quantity (Tons)",
                min_value=0.5,
                max_value=8.0,
                value=2.0,
                step=0.5,
                key="offline_quantity",
            )

            offline_location = st.selectbox(
                "Village",
                list(LOCATION_ALIASES.keys()),
                key="offline_location",
            )

        if st.button(
            "📴 Save to Offline Queue",
            type="primary",
            use_container_width=True,
        ):

            offline_id = "OFF-" + str(uuid.uuid4())[:6].upper()

            st.session_state.offline_queue.append(
                {
                    "offline_id": offline_id,
                    "name": offline_name,
                    "crop": offline_crop,
                    "quantity": offline_quantity,
                    "location": offline_location,
                    "saved_at": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                }
            )

            st.success("Request stored in offline queue.")

        st.divider()

        if st.session_state.offline_queue:

            st.write("### 📴 Pending Requests")

            st.dataframe(
                pd.DataFrame(st.session_state.offline_queue),
                use_container_width=True,
                hide_index=True,
            )

            if st.button(
                "📶 Network Restored — Sync All",
                type="primary",
                use_container_width=True,
            ):

                synced = 0

                for item in list(st.session_state.offline_queue):

                    add_structured_request(
                        item["name"],
                        item["crop"],
                        item["quantity"],
                        "Tomorrow",
                        item["location"],
                        "Offline Sync",
                    )

                    synced += 1

                st.session_state.offline_queue = []

                st.success(f"📶 {synced} request(s) synchronized successfully.")

                st.rerun()

        else:

            st.success("No pending offline requests.")


# ============================================================
# TAB 3 — AI PLANNING
# ============================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">' "🧠 AI Collection Planning" "</div>",
        unsafe_allow_html=True,
    )

    farmers = st.session_state.farmer_pool

    if not farmers:

        st.warning("Load farmers first.")

    else:

        total_quantity = get_total_quantity(farmers)

        high_priority = sum(1 for farmer in farmers if get_priority(farmer) == "High")

        try:

            preview_routes = pack_farmers_into_vehicles(farmers)

            estimated_vehicles = len(preview_routes)

        except ValueError as e:

            preview_routes = []

            estimated_vehicles = 0

            st.error(str(e))

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "👨‍🌾 Farmers",
                len(farmers),
            )

        with c2:

            st.metric(
                "🌾 Total Crop",
                f"{total_quantity:g} Tons",
            )

        with c3:

            st.metric(
                "🔴 High Priority",
                high_priority,
            )

        with c4:

            st.metric(
                "🚜 Vehicles Required",
                estimated_vehicles,
            )

        st.divider()

        st.markdown(
            """
            <div class="ai-box">
                <b>🤖 AI Route Optimization Agent</b><br><br>
                The planning engine considers farmer quantity,
                priority, collection readiness and vehicle capacity.
                It searches for a feasible minimum number of vehicles
                rather than assigning farmers sequentially.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🧠 Generate Optimal Collection Routes",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner("🤖 AI is optimizing the collection plan..."):

                try:

                    routes = pack_farmers_into_vehicles(farmers)

                    st.session_state.generated_routes = routes

                    st.session_state.route_generated = True

                    st.session_state.route_generated_at = datetime.now().strftime(
                        "%d-%m-%Y %I:%M %p"
                    )

                    # Reset vehicle assignments
                    for vehicle in st.session_state.vehicles:

                        vehicle["status"] = "Available"

                        vehicle["route_index"] = None

                    st.success(f"AI plan generated: " f"{len(routes)} vehicle(s).")

                except ValueError as e:

                    st.error(str(e))

        if st.session_state.route_generated:

            routes = st.session_state.generated_routes

            st.success("✅ Collection plan generated successfully.")

            # ------------------------------------------------
            # Validation
            # ------------------------------------------------

            assigned_ids = []

            for route in routes:

                for farmer in route["farmers"]:

                    assigned_ids.append(farmer.get("id"))

            expected_ids = {farmer.get("id") for farmer in farmers}

            if (
                len(assigned_ids) == len(set(assigned_ids))
                and set(assigned_ids) == expected_ids
            ):

                st.success("✅ All farmers assigned exactly once.")

            else:

                st.error("❌ Assignment validation failed.")

            st.divider()

            st.subheader("🗺️ Optimized Doorstep Collection Plan")

            for index, route in enumerate(
                routes,
                start=1,
            ):

                route_farmers = route["farmers"]

                load = route["load"]

                villages = [get_village(farmer) for farmer in route_farmers]

                route_path = " → ".join(villages)

                st.markdown(
                    f"""
                    <div class="route-box">

                        <h3>🚜 Vehicle {index}</h3>

                        <b>👨‍🌾 Farmers:</b>
                        {len(route_farmers)}

                        <br><br>

                        <b>⚖️ Load:</b>
                        {load:g} Tons

                        <br><br>

                        <b>📦 Capacity:</b>
                        8 Tons

                        <br><br>

                        <b>📍 Route:</b>
                        Procurement Centre
                        → {route_path}
                        → Procurement Centre

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                sequence = " → ".join(
                    f"{farmer.get('id')} " f"({farmer.get('name')})"
                    for farmer in route_farmers
                )

                st.write(f"🛣️ **Pickup Sequence:** " f"{sequence}")

                with st.expander(f"View Vehicle {index} Farmer Details"):

                    for farmer in route_farmers:

                        priority_icon = "🔴" if get_priority(farmer) == "High" else "🟡"

                        st.write(
                            f"{priority_icon} "
                            f"**{farmer.get('id')}** | "
                            f"{farmer.get('name')} | "
                            f"📍 {get_village(farmer)} | "
                            f"🌾 {farmer.get('crop')} | "
                            f"⚖️ {get_quantity(farmer):g} Tons | "
                            f"📅 {get_collection_date(farmer)}"
                        )

            st.divider()

            st.subheader("🧠 AI Decision Summary")

            decisions = [
                "Nearby/location-aware grouping considered",
                "Collection readiness/date considered",
                "Vehicle capacity constraint enforced",
                "High-priority requests considered",
                "Pickup sequence generated",
                "Minimum feasible vehicle count searched",
            ]

            for decision in decisions:

                st.success("✅ " + decision)

            st.subheader("📊 Optimization Impact")

            route_count = len(routes)

            trips_avoided = max(
                0,
                len(farmers) - route_count,
            )

            a, b, c = st.columns(3)

            with a:

                st.metric(
                    "🚜 Trips Avoided",
                    trips_avoided,
                )

            with b:

                st.metric(
                    "📏 Travel Reduction",
                    "≈ 28%",
                )

            with c:

                st.metric(
                    "⏱️ Waiting Reduction",
                    "≈ 35%",
                )

            st.caption(
                "Impact percentages are prototype/demo estimates, "
                "not field-validated measurements."
            )


# ============================================================
# TAB 4 — FLEET MANAGEMENT
# ============================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">' "🚛 Vehicle & Driver Management" "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "The fleet module connects AI-generated collection "
        "plans with actual vehicles and drivers."
    )

    if not st.session_state.vehicles:

        st.warning("No vehicles available.")

    else:

        fleet_data = []

        for vehicle in st.session_state.vehicles:

            route_label = "-"

            if vehicle.get("route_index") is not None:

                route_label = f"Vehicle Route " f"{vehicle['route_index'] + 1}"

            fleet_data.append(
                {
                    "Vehicle": vehicle["number"],
                    "Capacity": f"{vehicle['capacity']} Tons",
                    "Driver": vehicle["driver"],
                    "Driver Contact": vehicle["phone"],
                    "Status": vehicle["status"],
                    "Assignment": route_label,
                }
            )

        st.dataframe(
            pd.DataFrame(fleet_data),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader("🚛 Assign AI Routes to Fleet")

        if not st.session_state.route_generated:

            st.warning("Generate AI routes first.")

        else:

            routes = st.session_state.generated_routes

            for index, route in enumerate(routes):

                if index >= len(st.session_state.vehicles):

                    st.error(
                        "Not enough vehicles available " "for the generated routes."
                    )

                    break

                vehicle = st.session_state.vehicles[index]

                load = route["load"]

                col1, col2, col3 = st.columns([2, 2, 2])

                with col1:

                    st.write(f"**Route {index + 1}**")

                    st.write(f"Load: {load:g} Tons")

                with col2:

                    st.write(f"🚛 {vehicle['number']}")

                    st.write(f"👨‍✈️ {vehicle['driver']}")

                with col3:

                    if st.button(
                        f"Assign Vehicle {index + 1}",
                        key=f"assign_vehicle_{index}",
                        use_container_width=True,
                    ):

                        vehicle["status"] = "Assigned"

                        vehicle["route_index"] = index

                        st.success(
                            f"{vehicle['number']} " f"assigned to Route {index + 1}."
                        )

                        st.rerun()

                st.divider()

        st.subheader("🔄 Vehicle Status Lifecycle")

        st.write("Available → Assigned → On Route " "→ Farmer Pickup → Completed")

        for i, vehicle in enumerate(st.session_state.vehicles):

            st.write(f"**{vehicle['number']}** — " f"{vehicle['status']}")

            current_status = vehicle["status"]

            if current_status == "Available":

                next_status = "Assigned"

            elif current_status == "Assigned":

                next_status = "On Route"

            elif current_status == "On Route":

                next_status = "Farmer Pickup"

                next_status = "Completed"

            else:

                next_status = None

            if next_status:

                if st.button(
                    f"Move to {next_status}",
                    key=f"status_{i}_{current_status}",
                ):

                    vehicle["status"] = next_status

                    st.rerun()


# ============================================================
# TAB 5 — TRACKING
# ============================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">' "📍 Live Collection Status" "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "Prototype tracking lifecycle connecting farmer "
        "requests, vehicles and collection execution."
    )

    st.subheader("🚛 Fleet Status")

    for vehicle in st.session_state.vehicles:

        status = vehicle["status"]

        if status == "Available":

            icon = "🟢"

        elif status == "Assigned":

            icon = "🟡"

        elif status == "On Route":

            icon = "🔵"

        elif status == "Farmer Pickup":

            icon = "🟠"

        else:

            icon = "✅"

        st.markdown(
            f"""
            <div class="status-box">
                {icon}
                <b>{vehicle['number']}</b>
                —
                Driver: {vehicle['driver']}
                —
                Status: <b>{status}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("👨‍🌾 Farmer Procurement Tracking")

    farmers = st.session_state.farmer_pool

    if farmers:

        selected_id = st.selectbox(
            "Select Farmer Request",
            [farmer.get("id") for farmer in farmers],
        )

        selected_farmer = next(
            (farmer for farmer in farmers if farmer.get("id") == selected_id),
            None,
        )

        if selected_farmer:

            st.write(f"**Farmer:** " f"{selected_farmer.get('name')}")

            st.write(f"**Village:** " f"{get_village(selected_farmer)}")

            st.write(f"**Crop:** " f"{selected_farmer.get('crop')}")

            st.write(f"**Quantity:** " f"{get_quantity(selected_farmer):g} Tons")

            current = selected_farmer.get(
                "request_status",
                "Request Received",
            )

            tracking_steps = [
                "Request Received",
                "Vehicle Assigned",
                "On Route",
                "Farmer Pickup",
                "Collection Completed",
            ]

            for step in tracking_steps:

                if (
                    tracking_steps.index(step) <= tracking_steps.index(current)
                    if current in tracking_steps
                    else False
                ):

                    st.success(f"✅ {step}")

                else:

                    st.write(f"⬜ {step}")

            st.divider()

            status_options = [
                "Request Received",
                "Vehicle Assigned",
                "On Route",
                "Farmer Pickup",
                "Collection Completed",
            ]

            new_status = st.selectbox(
                "Update Farmer Collection Status",
                status_options,
                index=(
                    status_options.index(current) if current in status_options else 0
                ),
            )

            if st.button(
                "🔄 Update Farmer Status",
                type="primary",
                use_container_width=True,
            ):

                selected_farmer["request_status"] = new_status

                st.session_state.status = new_status

                st.success(f"Status updated to {new_status}.")

                st.rerun()

    else:

        st.info("No farmer requests available.")


# ============================================================
# TAB 6 — PROCUREMENT / RECEIPT
# ============================================================

with tabs[5]:

    st.markdown(
        '<div class="section-title">' "🧾 Digital Procurement & Payment" "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "Prototype representation of digital procurement "
        "confirmation, receipt and payment status."
    )

    farmers = st.session_state.farmer_pool

    if not farmers:

        st.warning("No farmer requests available.")

    else:

        completed_farmers = [
            farmer
            for farmer in farmers
            if farmer.get("request_status") == "Collection Completed"
        ]

        if not completed_farmers:

            st.info(
                "Mark a farmer's collection as "
                "'Collection Completed' in the Tracking tab "
                "to generate a receipt."
            )

        else:

            selected = st.selectbox(
                "Select Completed Farmer",
                [farmer.get("id") for farmer in completed_farmers],
            )

            farmer = next(
                (f for f in completed_farmers if f.get("id") == selected),
                None,
            )

            if farmer:

                price_per_ton = st.number_input(
                    "Procurement Price per Ton",
                    min_value=0.0,
                    value=22000.0,
                    step=500.0,
                )

                quality = st.selectbox(
                    "Quality Status",
                    [
                        "Accepted",
                        "Accepted - Grade A",
                        "Accepted - Grade B",
                    ],
                )

                payment_status = st.selectbox(
                    "Payment Status",
                    [
                        "Pending",
                        "Processing",
                        "Paid",
                    ],
                )

                total_amount = get_quantity(farmer) * price_per_ton

                st.metric(
                    "💰 Procurement Value",
                    f"₹{total_amount:,.2f}",
                )

                if st.button(
                    "🧾 Generate Digital Receipt",
                    type="primary",
                    use_container_width=True,
                ):

                    receipt_id = "REC-" + str(uuid.uuid4())[:8].upper()

                    receipt = {
                        "receipt_id": receipt_id,
                        "procurement_id": farmer.get("id"),
                        "farmer": farmer.get("name"),
                        "crop": farmer.get("crop"),
                        "quantity": get_quantity(farmer),
                        "quality": quality,
                        "price_per_ton": price_per_ton,
                        "total_amount": total_amount,
                        "payment_status": payment_status,
                        "generated_at": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                    }

                    st.session_state.receipt_records.append(receipt)

                    st.success("🧾 Digital receipt generated.")

                if st.session_state.receipt_records:

                    latest = st.session_state.receipt_records[-1]

                    st.divider()

                    st.subheader("🧾 Procurement Receipt")

                    receipt_col1, receipt_col2 = st.columns(2)

                    with receipt_col1:

                        st.write(f"**Receipt ID:** " f"{latest['receipt_id']}")

                        st.write(f"**Procurement ID:** " f"{latest['procurement_id']}")

                        st.write(f"**Farmer:** " f"{latest['farmer']}")

                        st.write(f"**Crop:** " f"{latest['crop']}")

                    with receipt_col2:

                        st.write(f"**Quantity:** " f"{latest['quantity']:g} Tons")

                        st.write(f"**Quality:** " f"{latest['quality']}")

                        st.write(f"**Price/Ton:** " f"₹{latest['price_per_ton']:,.2f}")

                        st.write(f"**Total:** " f"₹{latest['total_amount']:,.2f}")

                        st.write(f"**Payment:** " f"{latest['payment_status']}")

                    if latest["payment_status"] == "Paid":

                        st.success("💳 Payment marked as completed.")

                    else:

                        st.warning("💳 Payment is not yet completed.")


# ============================================================
# CURRENT REQUEST TRACKING
# ============================================================

if st.session_state.request_id:

    st.divider()

    st.markdown(
        '<div class="section-title">' "🚜 Current Farmer Request" "</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.metric(
            "🆔 Request",
            st.session_state.request_id,
        )

    with c2:

        st.metric(
            "🌾 Crop",
            st.session_state.crop or "-",
        )

    with c3:

        st.metric(
            "⚖️ Quantity",
            f"{st.session_state.quantity or 0} Tons",
        )

    with c4:

        st.metric(
            "📍 Location",
            st.session_state.location or "-",
        )

    with c5:

        st.metric(
            "📅 Collection",
            st.session_state.collection_date or "-",
        )


# ============================================================
# AI AGENT SUMMARY
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">' "🤖 AI Agent Architecture" "</div>",
    unsafe_allow_html=True,
)

agent_cols = st.columns(5)

agents = [
    (
        "🎙️",
        "Request Agent",
        "Voice / SMS / IVR understanding",
    ),
    (
        "👨‍🌾",
        "Farmer Pool Agent",
        "Aggregates collection demand",
    ),
    (
        "🧠",
        "Scheduling Agent",
        "Capacity-aware planning",
    ),
    (
        "🚛",
        "Fleet Agent",
        "Vehicle + driver allocation",
    ),
    (
        "📍",
        "Tracking Agent",
        "Collection lifecycle",
    ),
]

for col, agent in zip(
    agent_cols,
    agents,
):

    with col:

        st.markdown(
            f"""
            <div class="gateway-card">
                <h3>{agent[0]} {agent[1]}</h3>
                <p>{agent[2]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌾 Smart Doorstep Agricultural Procurement | "
    "AI-powered inclusive procurement operations prototype"
)

st.caption(
    "Prototype scope: Tamil voice processing, "
    "multi-channel request simulation, farmer pooling, "
    "capacity-aware planning, fleet management, tracking, "
    "digital receipt and payment-status workflow."
)
