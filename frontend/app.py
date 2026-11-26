import os
import time
import requests
import pandas as pd
import streamlit as st

from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GAARD | Civic Issue Management",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM STYLING
# =========================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

/* GLOBAL */

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

.stApp {
    background: #F4F7FB !important;
    color: #102A43 !important;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ALL HEADINGS */

h1, h2, h3, h4, h5, h6 {
    color: #102A43 !important;
    font-weight: 800 !important;
}

/* NORMAL TEXT */

.stMarkdown p,
.stMarkdown li,
.stMarkdown span {
    color: #243B53 !important;
    font-weight: 600 !important;
}

/* CAPTIONS */

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: #486581 !important;
    font-weight: 700 !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #102A43 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: #183B56 !important;
    border-radius: 10px !important;
    padding: 12px !important;
    margin-bottom: 7px !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #087E8B !important;
}

/* METRIC CARDS */

div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 15px !important;
    padding: 20px !important;
    box-shadow: 0 4px 15px rgba(16,42,67,0.06);
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] p {
    color: #334E68 !important;
    font-weight: 800 !important;
}

div[data-testid="stMetricValue"] {
    color: #102A43 !important;
    font-weight: 800 !important;
}

/* FORM LABELS */

[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label {
    color: #102A43 !important;
    font-weight: 800 !important;
}

/* INPUT FIELDS */

input, textarea {
    color: #102A43 !important;
    background: #FFFFFF !important;
    font-weight: 600 !important;
}

/* BUTTONS */

div.stButton > button {
    border-radius: 10px !important;
    font-weight: 800 !important;
    min-height: 42px;
}

div.stButton > button[kind="primary"] {
    background: #087E8B !important;
    color: #FFFFFF !important;
    border: none !important;
}

div.stButton > button[kind="primary"]:hover {
    background: #066773 !important;
}

/* FILE UPLOADER */

div[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 2px dashed #829AB1 !important;
    border-radius: 14px !important;
    padding: 15px !important;
}

/* TABLES */

[data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 12px !important;
}

/* SECTION LABELS */

.section-label {
    color: #087E8B !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 1.4px !important;
}

/* INFO CARDS */

.info-card {
    background: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 14px !important;
    padding: 18px !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# API HELPER FUNCTIONS
# =========================================================

def api_request(method, endpoint, show_error=True, **kwargs):

    try:

        response = requests.request(
            method,
            f"{BACKEND_URL}/{endpoint.lstrip('/')}",
            timeout=20,
            **kwargs
        )

        try:
            data = response.json() if response.content else {}

        except ValueError:
            data = {
                "detail": response.text or "Invalid backend response"
            }

        if not response.ok:

            if show_error:
                st.error(
                    data.get("detail", "API request failed")
                )

            return None

        return data

    except requests.RequestException as error:

        if show_error:
            st.error(
                f"Backend connection error: {error}"
            )

        return None


def fetch_data(endpoint):

    return api_request("GET", endpoint)


def show_table(rows, empty_message="No records found."):

    if rows:

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            
        )

    else:

        st.info(empty_message)


# =========================================================
# COMPLAINT STATUS POLLING
# =========================================================

def poll_complaint(
    complaint_id,
    timeout_seconds=90,
    interval_seconds=2
):

    final_statuses = {
        "routed",
        "rejected",
        "review_required",
        "retake_required",
        "notification_failed",
        "processing_failed"
    }

    deadline = time.monotonic() + timeout_seconds

    latest = None

    progress = st.progress(
        0,
        text="GAARD is starting the AI workflow..."
    )

    while time.monotonic() < deadline:

        latest = api_request(
            "GET",
            f"complaints/{complaint_id}",
            show_error=False
        )

        if latest and latest.get("status") in final_statuses:

            progress.progress(
                100,
                text="Processing completed"
            )

            time.sleep(0.3)
            progress.empty()

            return latest

        elapsed = timeout_seconds - max(
            0,
            deadline - time.monotonic()
        )

        percentage = min(
            95,
            int(elapsed / timeout_seconds * 100)
        )

        progress.progress(
            percentage,
            text="Analyzing image and processing complaint..."
        )

        time.sleep(interval_seconds)

    progress.empty()

    return latest
# =========================================================
# DISPLAY COMPLAINT RESULT
# =========================================================

def render_complaint_result(result):

    status = result.get("status", "unknown")

    tracking_id = result.get(
        "tracking_id",
        f"GAARD-{result.get('id', 0):06d}"
    )

    st.subheader("Complaint processing result")

    st.markdown(
        f"""
        <div class="info-card">
            <p style="color:#176b87;font-size:12px;font-weight:800;">
                TRACKING REFERENCE
            </p>
            <h3 style="color:#102a43;margin:0;">
                {tracking_id}
            </h3>
            <p style="color:#627d98;">
                Location: {result.get('address') or 'Not provided'}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if status == "routed":

        st.success(
            "Your complaint was analyzed and routed successfully."
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Issue category",
            result.get("category") or "Not identified"
        )

        col2.metric(
            "Severity",
            result.get("severity") or "Not assessed"
        )

        col3.metric(
            "Department",
            result.get("department") or "Not assigned"
        )

        if result.get("email_status") == "accepted_by_smtp":

            st.info(
                "📧 Department notification was accepted by the email server."
            )

        elif result.get("email_status") == "failed":

            st.warning(
                "Complaint routed, but email notification failed."
            )

        else:

            st.caption(
                f"Email status: {result.get('email_status', 'pending')}"
            )

    elif status == "retake_required":

        st.warning(
            "📸 Retake image required. "
            "The uploaded image may be blurry, too dark, "
            "overexposed or too low in resolution."
        )

    elif status == "rejected":

        st.error(
            "The uploaded image does not appear to show "
            "a supported civic issue. Please upload a relevant image."
        )

    elif status == "review_required":

        st.warning(
            "Your complaint needs human review because "
            "the AI could not confidently classify the image."
        )

    elif status == "notification_failed":

        st.warning(
            "Complaint analyzed and routed, but the email notification failed."
        )

    elif status == "processing_failed":

        st.error(
            "Complaint processing failed. Please contact the administrator."
        )

        if result.get("ai_error"):

            with st.expander("Technical details"):

                st.code(result["ai_error"])

    else:

        st.info(
            "Your complaint is saved and may still be processing."
        )


# =========================================================
# APPLICATION HEADER
# =========================================================

st.title("🏙️ GAARD")

st.caption(
    "AI-powered Civic Issue Detection and Response System"
)

st.divider()


# =========================================================
# BACKEND CONNECTION
# =========================================================

health = fetch_data("health")

if health:

    st.success("Backend connected")

else:

    st.error(
        "Backend is not reachable. Start FastAPI and refresh."
    )


# =========================================================
# FETCH DATABASE DATA
# =========================================================

categories = fetch_data("categories")

departments = fetch_data("departments")

complaints = fetch_data("complaints")

routes = fetch_data("routing-rules")


if any(
    value is None
    for value in [
        categories,
        departments,
        complaints,
        routes
    ]
):

    st.warning(
        "Some dashboard data could not be loaded. Check the backend."
    )

    st.stop()


# =========================================================
# DASHBOARD METRICS
# =========================================================

total_complaints = len(complaints)

routed_count = sum(
    1
    for item in complaints
    if item.get("status") == "routed"
)

review_count = sum(
    1
    for item in complaints
    if item.get("status") in {
        "review_required",
        "retake_required"
    }
)

pending_count = sum(
    1
    for item in complaints
    if item.get("status") in {
        "received",
        "submitted",
        "processing"
    }
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.title("🏙️ GAARD")

    st.caption("Civic Management System")

    st.divider()

    active_page = st.radio(
        "MAIN MENU",
        [
            "📊 Overview",
            "📝 Submit Complaint",
            "📂 Complaints",
            "🏷️ Categories",
            "🏢 Departments",
            "🔀 Routing Rules"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.caption("GAARD Admin Portal")


# =========================================================
# DASHBOARD METRIC CARDS
# =========================================================

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Total complaints",
    total_complaints
)

m2.metric(
    "Successfully routed",
    routed_count
)

m3.metric(
    "Needs review",
    review_count
)

m4.metric(
    "Active departments",
    len(departments)
)

st.write("")

# =========================================================

# =========================================================
# 1. OVERVIEW DASHBOARD
# =========================================================

if active_page == "📊 Overview":

    st.markdown(
        '<p class="section-label">COMMAND CENTER</p>',
        unsafe_allow_html=True
    )

    st.header("Municipal Overview")

    # -----------------------------------------------------
    # RECENT COMPLAINTS
    # -----------------------------------------------------

    st.subheader("Recent Complaints")

    if complaints:

        recent = sorted(
            complaints,
            key=lambda item: item.get("id", 0),
            reverse=True
        )[:8]

        st.dataframe(
            pd.DataFrame(recent),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No complaints have been submitted yet.")

    st.divider()

    # -----------------------------------------------------
    # COMPLAINT STATUS
    # -----------------------------------------------------

    st.subheader("Complaint Status")

    if complaints:

        status_counts = pd.Series(
            [
                item.get("status", "unknown")
                for item in complaints
            ]
        ).value_counts().rename_axis(
            "Status"
        ).reset_index(
            name="Count"
        )

        st.bar_chart(
            status_counts.set_index("Status"),
            use_container_width=True
        )

    else:

        st.info("Status analytics will appear here.")

    st.divider()

    # -----------------------------------------------------
    # ISSUE CATEGORIES
    # -----------------------------------------------------

    st.subheader("Configured Issue Categories")

    show_table(
        categories,
        "No active categories configured."
    )


# =========================================================
# 2. CITIZEN COMPLAINT SUBMISSION
# =========================================================

elif active_page == "📝 Submit Complaint":

    st.markdown(
        '<p class="section-label">CITIZEN PORTAL</p>',
        unsafe_allow_html=True
    )

    st.header("Submit a Civic Complaint")

    st.caption(
        "Upload a photograph of the civic issue and enter its location."
    )

    # -----------------------------------------------------
    # IMAGE UPLOAD
    # -----------------------------------------------------

    st.subheader("1. Upload issue photograph")

    upload_version = st.session_state.get(
        "upload_widget_version",
        0
    )

    uploaded_image = st.file_uploader(
        "Choose an image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        key=f"citizen_image_{upload_version}",
        help="Upload a clear photograph of the civic issue."
    )

    if uploaded_image is not None:

        if st.session_state.get("retake_message"):

            st.session_state["retake_message"] = ""

        st.image(
            uploaded_image,
            caption="Selected issue photograph",
            use_container_width=True
        )

    # Retake warning

    retake_message = st.session_state.get(
        "retake_message"
    )

    if retake_message:

        st.warning(
            f"📸 Retake image required: {retake_message}"
        )

    st.divider()

    # -----------------------------------------------------
    # LOCATION INPUT
    # -----------------------------------------------------

    st.subheader("2. Enter issue location")

    address = st.text_input(
        "Area / locality / landmark",
        placeholder="Example: Mangamur Circle, Ongole",
        key="citizen_address",
        help="Enter the location manually. GPS is not used."
    )

    st.caption(
        "Enter the place where the civic issue was observed."
    )

    st.divider()

    # -----------------------------------------------------
    # SUBMIT COMPLAINT
    # -----------------------------------------------------

    if st.button(
        "🚀 Submit Complaint",
        type="primary",
        use_container_width=True,
        disabled=(
            uploaded_image is None
            or not address.strip()
        )
    ):

        # Description is intentionally omitted.
        # Gemini Vision will analyze the uploaded image.

        form_data = {
            "address": address.strip()
        }

        files = {
            "image": (
                uploaded_image.name,
                uploaded_image.getvalue(),
                uploaded_image.type or "application/octet-stream"
            )
        }

        with st.spinner("Submitting your complaint..."):

            submission = api_request(
                "POST",
                "complaints",
                data=form_data,
                files=files
            )

        if submission:

            complaint_id = submission["complaint_id"]

            st.session_state["last_complaint_id"] = complaint_id

            st.session_state["last_tracking_id"] = (
                submission.get("tracking_id")
            )

            st.session_state["retake_message"] = ""

            st.success(
                f"Complaint submitted successfully. "
                f"Tracking ID: {submission.get('tracking_id')}"
            )

            # Wait for the LangGraph workflow.

            latest = poll_complaint(complaint_id)

            if latest:

                st.session_state["last_result"] = latest

            else:

                st.session_state["last_result"] = {
                    "id": complaint_id,
                    "tracking_id": submission.get("tracking_id"),
                    "address": address.strip(),
                    "status": "processing",
                    "email_status": "pending"
                }

            # Clear uploaded image with a new widget key.

            st.session_state["upload_widget_version"] = (
                upload_version + 1
            )

            st.rerun()

    # -----------------------------------------------------
    # DISPLAY RESULT
    # -----------------------------------------------------

    last_result = st.session_state.get("last_result")

    if last_result:

        st.divider()

        render_complaint_result(last_result)

        if last_result.get("status") == "retake_required":

            st.session_state["retake_message"] = (
                "The image may be blurry, too dark, "
                "overexposed or too low in resolution. "
                "Please select a clearer image."
            )

            st.info(
                "Upload another image and submit again. "
                "The current implementation creates a new complaint "
                "and tracking ID."
            )

        if st.button(
            "Clear displayed result",
            key="clear_citizen_result"
        ):

            for key in [
                "last_result",
                "last_complaint_id",
                "last_tracking_id",
                "retake_message"
            ]:

                st.session_state.pop(key, None)

            st.rerun()
            
# =========================================================
# 3. COMPLAINT MANAGEMENT
# =========================================================

elif active_page == "📂 Complaints":

    st.markdown(
        '<p class="section-label">MONITORING</p>',
        unsafe_allow_html=True
    )

    st.header("Complaint Records")

    if complaints:

        ordered = sorted(
            complaints,
            key=lambda item: item.get("id", 0),
            reverse=True
        )

        st.dataframe(
            pd.DataFrame(ordered),
            use_container_width=True,
            hide_index=True,
            
        )

        selected_id = st.selectbox(
            "View complaint details",
            [item["id"] for item in ordered],
            format_func=lambda value: f"GAARD-{value:06d}"
        )

        if st.button("Load complaint details"):

            detail = api_request(
                "GET",
                f"complaints/{selected_id}"
            )

            if detail:

                st.json(detail)

    else:

        st.info("No complaints submitted yet.")

    if st.button("Refresh complaint list"):

        st.rerun()


# =========================================================
# 4. CATEGORY MANAGEMENT
# =========================================================

elif active_page == "🏷️ Categories":

    st.markdown(
        '<p class="section-label">CONFIGURATION</p>',
        unsafe_allow_html=True
    )

    st.header("Issue Category Management")

    # Add category

    with st.expander("➕ Add a new category"):

        with st.form("add_category_form"):

            new_name = st.text_input(
                "Category name"
            )

            new_description = st.text_area(
                "Category description"
            )

            add_category = st.form_submit_button(
                "Add category"
            )

        if add_category:

            if not new_name.strip():

                st.warning("Category name is required.")

            else:

                result = api_request(
                    "POST",
                    "categories",
                    json={
                        "name": new_name.strip(),
                        "description": new_description.strip()
                    }
                )

                if result:

                    st.success(result["message"])

                    st.rerun()

    # Display categories

    st.subheader("Active categories")

    show_table(
        categories,
        "No active categories available."
    )

    # Edit and deactivate category

    if categories:

        category_map = {
            f"{item['name']} (ID: {item['id']})": item
            for item in categories
        }

        selected = category_map[
            st.selectbox(
                "Select category to edit or deactivate",
                list(category_map.keys()),
                key="category_selector"
            )
        ]

        with st.form("edit_category_form"):

            edit_name = st.text_input(
                "Category name",
                value=selected["name"]
            )

            edit_description = st.text_area(
                "Description",
                value=selected.get("description") or ""
            )

            update_category = st.form_submit_button(
                "Save changes"
            )

        if update_category:

            result = api_request(
                "PATCH",
                f"categories/{selected['id']}",
                json={
                    "name": edit_name.strip(),
                    "description": edit_description.strip()
                }
            )

            if result:

                st.success(result["message"])

                st.rerun()

        confirm = st.checkbox(
            f"Confirm deactivation of {selected['name']}",
            key="confirm_category_deactivate"
        )

        if st.button(
            "Deactivate category",
            disabled=not confirm,
            key="deactivate_category_button"
        ):

            result = api_request(
                "DELETE",
                f"categories/{selected['id']}"
            )

            if result:

                st.success(result["message"])

                st.rerun()
                
# =========================================================
# 5. DEPARTMENT MANAGEMENT
# =========================================================

elif active_page == "🏢 Departments":

    st.markdown(
        '<p class="section-label">CONFIGURATION</p>',
        unsafe_allow_html=True
    )

    st.header("Department Management")

    # Add department

    with st.expander("➕ Add a new department"):

        with st.form("add_department_form"):

            department_name = st.text_input(
                "Department name"
            )

            department_email = st.text_input(
                "Department email"
            )

            jurisdiction = st.text_input(
                "Municipality / jurisdiction"
            )

            add_department = st.form_submit_button(
                "Add department"
            )

        if add_department:

            if not all([
                department_name.strip(),
                department_email.strip(),
                jurisdiction.strip()
            ]):

                st.warning(
                    "All department fields are required."
                )

            else:

                result = api_request(
                    "POST",
                    "departments",
                    json={
                        "name": department_name.strip(),
                        "email": department_email.strip(),
                        "jurisdiction": jurisdiction.strip()
                    }
                )

                if result:

                    st.success(result["message"])

                    st.rerun()

    # Display departments

    st.subheader("Registered departments")

    show_table(
        departments,
        "No active departments available."
    )

    # Edit and deactivate department

    if departments:

        department_map = {
            f"{item['name']} (ID: {item['id']})": item
            for item in departments
        }

        selected_department = department_map[
            st.selectbox(
                "Select department to edit or deactivate",
                list(department_map.keys()),
                key="department_selector"
            )
        ]

        with st.form("edit_department_form"):

            edit_name = st.text_input(
                "Department name",
                value=selected_department["name"]
            )

            edit_email = st.text_input(
                "Department email",
                value=selected_department["email"]
            )

            edit_jurisdiction = st.text_input(
                "Jurisdiction",
                value=selected_department["jurisdiction"]
            )

            update_department = st.form_submit_button(
                "Save changes"
            )

        if update_department:

            result = api_request(
                "PATCH",
                f"departments/{selected_department['id']}",
                json={
                    "name": edit_name.strip(),
                    "email": edit_email.strip(),
                    "jurisdiction": edit_jurisdiction.strip()
                }
            )

            if result:

                st.success(result["message"])

                st.rerun()

        confirm = st.checkbox(
            f"Confirm deactivation of {selected_department['name']}",
            key="confirm_department_deactivate"
        )

        if st.button(
            "Deactivate department",
            disabled=not confirm,
            key="deactivate_department_button"
        ):

            result = api_request(
                "DELETE",
                f"departments/{selected_department['id']}"
            )

            if result:

                st.success(result["message"])

                st.rerun()


# =========================================================
# 6. ROUTING RULE MANAGEMENT
# =========================================================

elif active_page == "🔀 Routing Rules":

    st.markdown(
        '<p class="section-label">WORKFLOW CONFIGURATION</p>',
        unsafe_allow_html=True
    )

    st.header("Category-to-Department Routing")

    # Existing rules

    st.subheader("Existing routing rules")

    show_table(
        routes,
        "No routing rules configured."
    )

    # Create a routing rule

    if categories and departments:

        category_map = {
            item["name"]: item["id"]
            for item in categories
        }

        department_map = {
            item["name"]: item["id"]
            for item in departments
        }

        with st.form("routing_form"):

            selected_category = st.selectbox(
                "Issue category",
                list(category_map.keys())
            )

            selected_department = st.selectbox(
                "Responsible department",
                list(department_map.keys())
            )

            priority = st.number_input(
                "Priority",
                min_value=1,
                max_value=10,
                value=1
            )

            create_route = st.form_submit_button(
                "Create routing rule"
            )

        if create_route:

            result = api_request(
                "POST",
                "routing-rules",
                json={
                    "category_id": category_map[selected_category],
                    "department_id": department_map[selected_department],
                    "priority": priority
                }
            )

            if result:

                st.success(result["message"])

                st.rerun()

    else:

        st.warning(
            "Create at least one active category "
            "and department first."
        )

    # Delete routing rule

    if routes:

        route_map = {
            (
                f"{item['category']} → "
                f"{item['department']} (ID: {item['id']})"
            ): item["id"]
            for item in routes
        }

        selected_route = st.selectbox(
            "Select a routing rule to remove",
            list(route_map.keys()),
            key="remove_route_selector"
        )

        if st.button("Delete selected routing rule"):

            result = api_request(
                "DELETE",
                f"routing-rules/{route_map[selected_route]}"
            )

            if result:

                st.success(result["message"])

                st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "GAARD · AI-powered Civic Issue Detection and Response System"
)