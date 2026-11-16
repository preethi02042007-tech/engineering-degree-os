"""
My Engineering Degree OS
A clean, student-friendly Streamlit application to manage Semesters 1 through 8.
Technical Stack: Python, Streamlit, Pandas.
Data Persistence: CSV files under /data directory.
"""

import os
import datetime
import pandas as pd
import streamlit as st

# ==========================================
# PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="My Engineering Degree OS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom student-friendly CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 1.85rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .stAlert {
        border-radius: 8px;
    }
    .badge-completed {
        background-color: #DCFCE7;
        color: #166534;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-inprogress {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-notstarted {
        background-color: #F1F5F9;
        color: #475569;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ==========================================
# SAFE DATA LOADING UTILITIES
# ==========================================
def load_csv_safe(filename: str, default_df: pd.DataFrame = None) -> pd.DataFrame:
    """Loads a CSV file safely. Shows a friendly warning instead of crashing if missing."""
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        st.warning(f"⚠️ Notice: Data file `{filename}` was not found in `/data`. Using fallback default template.")
        if default_df is not None:
            return default_df
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"⚠️ Error reading `{filename}`: {str(e)}")
        return default_df if default_df is not None else pd.DataFrame()

def save_csv_safe(df: pd.DataFrame, filename: str) -> bool:
    """Saves a DataFrame to CSV safely under the DATA_DIR directory."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        file_path = os.path.join(DATA_DIR, filename)
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        st.error(f"Failed to save `{filename}`: {str(e)}")
        return False

# Load primary datasets
semesters_df = load_csv_safe("semesters.csv")
courses_df = load_csv_safe("courses.csv")
uni_syllabus_df = load_csv_safe("university_syllabus.csv")
calendar_df = load_csv_safe("academic_calendar.csv")
assessments_df = load_csv_safe("assessments.csv")
scores_df = load_csv_safe("scores.csv")
checklist_df = load_csv_safe("plan_checklist.csv")

# ==========================================
# SIDEBAR NAVIGATION & STUDENT PROFILE
# ==========================================
with st.sidebar:
    st.markdown("### 🎓 Degree OS")
    st.markdown("**Engineering Academic Workspace**")
    st.caption("Semester 1 through Semester 8")
    
    st.divider()

    nav_options = [
        "1. Dashboard",
        "2. Semesters 1-8",
        "3. Courses & Syllabus",
        "4. University Syllabus",
        "5. Academic / Leave Calendar",
        "6. Internal Assessments",
        "7. Status Tracker",
        "8. Scorecard",
        "9. Plan & Checklist",
        "10. Ask Degree AI",
        "11. Data Admin"
    ]
    
    selected_page = st.radio(
        "Navigation",
        options=nav_options,
        index=0
    )
    
    st.divider()
    
    # Active Academic Status Quick View
    current_sem_row = semesters_df[semesters_df["status"] == "In Progress"] if not semesters_df.empty and "status" in semesters_df.columns else pd.DataFrame()
    current_sem_num = int(current_sem_row["semester"].values[0]) if not current_sem_row.empty else 5
    
    st.markdown(f"**Current Status:** Semester {current_sem_num}")
    st.markdown(f"**Target Degree:** B.Tech CSE (4 Yrs)")
    st.caption("AI Product Development - Degree OS")

# ==========================================
# PAGE 1: DASHBOARD
# ==========================================
if selected_page == "1. Dashboard":
    st.markdown('<div class="main-header">Academic Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Overview of your engineering progress, credit milestones, and upcoming events</div>', unsafe_allow_html=True)

    # Key Calculations
    total_required_credits = 160
    if not uni_syllabus_df.empty and "total_credits_required" in uni_syllabus_df.columns:
        try:
            total_required_credits = int(uni_syllabus_df["total_credits_required"].values[0])
        except Exception:
            total_required_credits = 160

    completed_credits = 0
    if not courses_df.empty and "credits" in courses_df.columns and "status" in courses_df.columns:
        completed_credits = int(courses_df[courses_df["status"] == "Completed"]["credits"].sum())
    
    degree_completion_pct = min(100.0, round((completed_credits / total_required_credits) * 100, 1)) if total_required_credits > 0 else 0.0

    # Next assessment
    next_assessment_text = "No upcoming assessments"
    if not assessments_df.empty and "due_date" in assessments_df.columns and "status" in assessments_df.columns:
        pending_ass = assessments_df[assessments_df["status"] != "Completed"].copy()
        if not pending_ass.empty:
            pending_ass["due_date_parsed"] = pd.to_datetime(pending_ass["due_date"], errors="coerce")
            pending_ass = pending_ass.sort_values(by="due_date_parsed")
            first_ass = pending_ass.iloc[0]
            next_assessment_text = f"{first_ass['assessment_type']} - {first_ass['course_title']} ({first_ass['due_date']})"

    # Next holiday / leave
    next_holiday_text = "No upcoming holidays"
    if not calendar_df.empty and "category" in calendar_df.columns and "date" in calendar_df.columns:
        leave_events = calendar_df[calendar_df["category"] == "Leave"].copy()
        if not leave_events.empty:
            leave_events["date_parsed"] = pd.to_datetime(leave_events["date"], errors="coerce")
            leave_events = leave_events.sort_values(by="date_parsed")
            first_leave = leave_events.iloc[0]
            next_holiday_text = f"{first_leave['event_name']} ({first_leave['date']})"

    # Metric Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Semester", f"Semester {current_sem_num}", "Year 3 (Active)")
    with col2:
        st.metric("Degree Completion", f"{degree_completion_pct}%", f"{completed_credits} / {total_required_credits} Credits")
    with col3:
        st.metric("Next Assessment", next_assessment_text.split(" - ")[0] if " - " in next_assessment_text else "None", next_assessment_text.split(" (")[0] if " (" in next_assessment_text else "")
    with col4:
        st.metric("Next Leave / Holiday", next_holiday_text.split(" (")[0], next_holiday_text.split(" (")[1].replace(")", "") if " (" in next_holiday_text else "")

    st.markdown("#### Degree Credit Progress")
    st.progress(degree_completion_pct / 100.0)
    st.caption(f"Completed {completed_credits} credits of {total_required_credits} total required engineering credits.")

    st.markdown("---")

    # Score Summary Prototype & Semester Progress Table
    col_left, col_right = st.columns([1.2, 1.8])

    with col_left:
        st.markdown("#### 📊 Score Summary")
        if not scores_df.empty and {"scored_marks", "max_marks"}.issubset(scores_df.columns):
            # The current scores.csv contains marks and a text grade,
            # but does not contain grade_point or credits.
            score_data = scores_df.copy()
            score_data["scored_marks"] = pd.to_numeric(
                score_data["scored_marks"], errors="coerce"
            ).fillna(0)
            score_data["max_marks"] = pd.to_numeric(
                score_data["max_marks"], errors="coerce"
            ).fillna(0)

            # Exclude rows explicitly marked Pending from earned-mark totals.
            if "grade" in score_data.columns:
                graded_data = score_data[
                    score_data["grade"].astype(str).str.strip().str.lower()
                    != "pending"
                ]
            else:
                graded_data = score_data

            tot_scored = graded_data["scored_marks"].sum()
            tot_max = graded_data["max_marks"].sum()
            overall_pct = (
                round((tot_scored / tot_max) * 100, 2)
                if tot_max > 0 else 0.0
            )

            st.write(f"**Cumulative Marks Percentage:** `{overall_pct}%`")
            st.write(f"**Graded Assessments to date:** `{len(graded_data)} records`")

            if {"grade_point", "credits"}.issubset(score_data.columns):
                score_data["grade_point"] = pd.to_numeric(
                    score_data["grade_point"], errors="coerce"
                ).fillna(0)
                score_data["credits"] = pd.to_numeric(
                    score_data["credits"], errors="coerce"
                ).fillna(0)
                tot_cr = score_data["credits"].sum()
                weighted_gp = (
                    score_data["grade_point"] * score_data["credits"]
                ).sum()
                simple_weighted_avg = (
                    round(weighted_gp / tot_cr, 2) if tot_cr > 0 else 0.0
                )
                st.write(
                    f"**Prototype Weighted Average:** `{simple_weighted_avg} / 10.0`"
                )
                st.caption(
                    "Prototype credit-weighted grade point; not an official university CGPA."
                )
            else:
                st.info(
                    "GPA is not calculated because scores.csv does not yet "
                    "contain both grade_point and credits columns."
                )
        else:
            st.info(
                "No usable marks found. Check that scores.csv contains "
                "scored_marks and max_marks columns."
            )

    with col_right:
        st.markdown("#### 🗓️ Semesters 1 to 8 Snapshot")
        if not semesters_df.empty:
            summary_table = semesters_df[["semester", "academic_year", "title", "target_credits", "status"]].copy()
            st.dataframe(summary_table, use_container_width=True, hide_index=True)
        else:
            st.warning("Semesters data not available.")

# ==========================================
# PAGE 2: SEMESTERS 1-8
# ==========================================
elif selected_page == "2. Semesters 1-8":
    st.markdown('<div class="main-header">Semesters 1 through 8</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Eight semester roadmap, progression status, and detailed semester breakdown</div>', unsafe_allow_html=True)

    if semesters_df.empty:
        st.warning("No semester records found in `data/semesters.csv`.")
    else:
        # All 8 semester cards in grid
        st.markdown("#### Semester Cards")
        cols = st.columns(4)
        for idx, row in semesters_df.iterrows():
            col = cols[idx % 4]
            with col:
                status_color = "🟢" if row["status"] == "Completed" else ("🟡" if row["status"] == "In Progress" else "⚪")
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{status_color} Semester {row['semester']}</h4>
                    <p style="font-size:0.85rem; color:#475569; margin-bottom:0.25rem;"><b>{row['academic_year']}</b></p>
                    <p style="font-size:0.9rem; font-weight:600; color:#1E293B;">{row['title']}</p>
                    <p style="font-size:0.8rem; color:#64748B;">Credits: {row['target_credits']} | Status: <b>{row['status']}</b></p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Filterable Semester Details")
        sem_list = sorted(semesters_df["semester"].unique().tolist())
        selected_sem = st.selectbox("Select Semester to inspect:", options=sem_list, index=4)

        sem_info = semesters_df[semesters_df["semester"] == selected_sem].iloc[0]
        st.markdown(f"### Semester {selected_sem}: {sem_info['title']}")
        st.write(f"**Academic Year:** {sem_info['academic_year']} | **Target Credits:** {sem_info['target_credits']} | **Status:** {sem_info['status']}")
        if "notes" in sem_info and pd.notna(sem_info["notes"]):
            st.info(f"**Focus Areas:** {sem_info['notes']}")

        # Courses in this semester
        if not courses_df.empty and "semester" in courses_df.columns:
            sem_courses = courses_df[courses_df["semester"] == selected_sem]
            st.markdown(f"**Courses in Semester {selected_sem} ({len(sem_courses)} registered):**")
            st.dataframe(
                sem_courses[["course_code", "title", "credits", "category", "status"]],
                use_container_width=True,
                hide_index=True
            )

# ==========================================
# PAGE 3: COURSES & SYLLABUS
# ==========================================
elif selected_page == "3. Courses & Syllabus":
    st.markdown('<div class="main-header">Courses & Syllabus Topics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Browse course codes, titles, credits, syllabus topics, and completion status</div>', unsafe_allow_html=True)

    if courses_df.empty:
        st.warning("No courses found in `data/courses.csv`.")
    else:
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
        with col_f1:
            sem_options = ["All Semesters"] + sorted(courses_df["semester"].unique().tolist())
            chosen_sem = st.selectbox("Filter by Semester", options=sem_options, index=0)
        with col_f2:
            categories = ["All Categories"] + sorted(courses_df["category"].dropna().unique().tolist()) if "category" in courses_df.columns else ["All"]
            chosen_cat = st.selectbox("Filter by Category", options=categories)
        with col_f3:
            search_query = st.text_input("Search Course Code / Title / Syllabus", placeholder="e.g. Algorithms, Networks, CS501")

        filtered_df = courses_df.copy()
        if chosen_sem != "All Semesters":
            filtered_df = filtered_df[filtered_df["semester"] == chosen_sem]
        if chosen_cat != "All Categories" and "category" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["category"] == chosen_cat]
        if search_query:
            q = search_query.lower()
            filtered_df = filtered_df[
                filtered_df["title"].str.lower().str.contains(q, na=False) |
                filtered_df["course_code"].str.lower().str.contains(q, na=False) |
                filtered_df["syllabus_topics"].str.lower().str.contains(q, na=False)
            ]

        # Summary KPIs
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total Courses in View", len(filtered_df))
        with k2:
            st.metric("Total Credits", int(filtered_df["credits"].sum()) if not filtered_df.empty else 0)
        with k3:
            comp_count = len(filtered_df[filtered_df["status"] == "Completed"]) if not filtered_df.empty else 0
            st.metric("Completed Courses", comp_count)

        st.dataframe(
            filtered_df[["semester", "course_code", "title", "credits", "category", "syllabus_topics", "status"]],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# PAGE 4: UNIVERSITY SYLLABUS
# ==========================================
elif selected_page == "4. University Syllabus":
    st.markdown('<div class="main-header">University Syllabus & Programme Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Official university curriculum guidelines, regulation references, and structure</div>', unsafe_allow_html=True)

    if uni_syllabus_df.empty:
        st.warning("University syllabus overview is missing from `data/university_syllabus.csv`.")
    else:
        info = uni_syllabus_df.iloc[0]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Programme Name:**\n\n{info.get('programme_name', 'B.Tech')}")
            st.markdown(f"**Degree:**\n\n{info.get('degree', 'B.Tech')}")
        with c2:
            st.markdown(f"**Total Required Credits:**\n\n{info.get('total_credits_required', 160)}")
            st.markdown(f"**Programme Duration:**\n\n{info.get('duration_years', '4 Years')}")
        with c3:
            st.markdown(f"**Affiliated University:**\n\n{info.get('affiliated_university', 'State Tech University')}")
            st.markdown(f"**Regulations Year:**\n\n{info.get('regulations_year', '2023')}")

        st.markdown("---")
        st.markdown("#### Programme Overview & Educational Objectives")
        st.write(info.get('programme_overview', 'Programme overview not specified.'))

        st.markdown("---")
        st.markdown("#### 🔗 Syllabus Source & Official Reference URL")
        current_url = info.get("syllabus_source_url", "https://university.ac.in")
        new_url = st.text_input("Curriculum Reference Link / Regulation Source:", value=current_url)

        if st.button("Update Syllabus Reference Link"):
            uni_syllabus_df.at[0, "syllabus_source_url"] = new_url
            if save_csv_safe(uni_syllabus_df, "university_syllabus.csv"):
                st.success("✅ University syllabus reference link updated successfully!")

        st.caption(f"Current verified source: [Open Official Curriculum Document]({new_url})")

# ==========================================
# PAGE 5: ACADEMIC / LEAVE CALENDAR
# ==========================================
elif selected_page == "5. Academic / Leave Calendar":
    st.markdown('<div class="main-header">Academic & Leave Calendar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Track internal assessment windows, semester examinations, and university holidays</div>', unsafe_allow_html=True)

    if calendar_df.empty:
        st.warning("Calendar records not found in `data/calendar.csv`.")
    else:
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            academic_years = ["All Years"] + sorted(calendar_df["academic_year"].dropna().unique().tolist())
            sel_year = st.selectbox("Academic Year", options=academic_years)
        with col_c2:
            semesters_avail = ["All Semesters"] + sorted(calendar_df["semester"].dropna().unique().tolist())
            sel_sem = st.selectbox("Semester", options=semesters_avail)
        with col_c3:
            types = ["All Events", "Academic", "Leave"]
            sel_type = st.selectbox("Event Category", options=types)

        filtered_cal = calendar_df.copy()
        if sel_year != "All Years":
            filtered_cal = filtered_cal[filtered_cal["academic_year"] == sel_year]
        if sel_sem != "All Semesters":
            filtered_cal = filtered_cal[filtered_cal["semester"] == sel_sem]
        if sel_type != "All Events":
            filtered_cal = filtered_cal[filtered_cal["category"] == sel_type]

        filtered_cal["date_parsed"] = pd.to_datetime(filtered_cal["date"], errors="coerce")
        filtered_cal = filtered_cal.sort_values(by="date_parsed")

        st.dataframe(
            filtered_cal[["date", "event_name", "category", "academic_year", "semester", "notes"]],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# PAGE 6: INTERNAL ASSESSMENTS
# ==========================================
elif selected_page == "6. Internal Assessments":
    st.markdown('<div class="main-header">Internal Assessments (IA1, IA2 & Evaluations)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Monitor IA1, IA2, assignments, lab continuous evaluations, project reviews, and exam schedules</div>', unsafe_allow_html=True)

    if assessments_df.empty:
        st.warning("No assessment data available in `data/assessments.csv`.")
    else:
        # Filter controls
        f1, f2, f3 = st.columns(3)
        with f1:
            course_opts = ["All Courses"] + sorted(assessments_df["course_title"].dropna().unique().tolist())
            sel_course = st.selectbox("Course Filter", options=course_opts)
        with f2:
            ass_types = ["All Types"] + sorted(assessments_df["assessment_type"].dropna().unique().tolist())
            sel_type = st.selectbox("Assessment Type", options=ass_types)
        with f3:
            status_opts = ["All Statuses", "Completed", "In Progress", "Scheduled"]
            sel_status = st.selectbox("Assessment Status", options=status_opts)

        filtered_ass = assessments_df.copy()
        if sel_course != "All Courses":
            filtered_ass = filtered_ass[filtered_ass["course_title"] == sel_course]
        if sel_type != "All Types":
            filtered_ass = filtered_ass[filtered_ass["assessment_type"] == sel_type]
        if sel_status != "All Statuses":
            filtered_ass = filtered_ass[filtered_ass["status"] == sel_status]

        # Calculate score percentages for completed assessments
        filtered_ass["score_%"] = filtered_ass.apply(
            lambda r: f"{round((r['scored_marks']/r['max_marks'])*100, 1)}%" if r['max_marks'] > 0 and r['status'] == "Completed" else "-",
            axis=1
        )

        st.dataframe(
            filtered_ass[["assessment_type", "course_code", "course_title", "due_date", "scored_marks", "max_marks", "score_%", "weightage_percentage", "status"]],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# PAGE 7: STATUS TRACKER
# ==========================================
elif selected_page == "7. Status Tracker":
    st.markdown('<div class="main-header">Degree Status Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Unified completion tracker for all subjects across Semester 1 to Semester 8</div>', unsafe_allow_html=True)

    if courses_df.empty:
        st.warning("No course data available.")
    else:
        total_courses = len(courses_df)
        completed = len(courses_df[courses_df["status"] == "Completed"])
        in_progress = len(courses_df[courses_df["status"] == "In Progress"])
        not_started = len(courses_df[courses_df["status"] == "Not Started"])

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Degree Courses", total_courses)
        with c2:
            st.metric("Completed", completed, f"{round((completed/total_courses)*100, 1)}%")
        with c3:
            st.metric("In Progress", in_progress, f"{round((in_progress/total_courses)*100, 1)}%")
        with c4:
            st.metric("Not Started", not_started, f"{round((not_started/total_courses)*100, 1)}%")

        st.markdown("---")
        st.markdown("#### Filter by Status")
        status_filter = st.radio("Show:", ["All", "In Progress", "Not Started", "Completed"], horizontal=True)

        view_df = courses_df.copy()
        if status_filter != "All":
            view_df = view_df[view_df["status"] == status_filter]

        st.dataframe(
            view_df[["semester", "course_code", "title", "credits", "category", "status"]],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# PAGE 8: SCORECARD
# ==========================================
elif selected_page == "8. Scorecard":
    st.markdown('<div class="main-header">Academic Scorecard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Assessment marks and semester-wise performance tracking</div>', unsafe_allow_html=True)

    st.info(
        "This Scorecard uses assessment records from assessments.csv. "
        "Only assessments marked Completed are counted as earned marks."
    )

    # The marks columns belong to assessments.csv, not scores.csv.
    required_columns = ["semester", "course_code", "course_title",
                        "assessment_type", "due_date", "scored_marks",
                        "max_marks", "status"]

    missing_columns = [col for col in required_columns
                       if col not in assessments_df.columns]

    if assessments_df.empty:
        st.warning("No assessment records found in data/assessments.csv.")
    elif missing_columns:
        st.error(
            "The assessments.csv file is missing these columns: "
            + ", ".join(missing_columns)
        )
    else:
        scorecard_df = assessments_df.copy()

        # Convert marks into numbers so calculations work correctly.
        scorecard_df["scored_marks"] = pd.to_numeric(
            scorecard_df["scored_marks"], errors="coerce"
        ).fillna(0)
        scorecard_df["max_marks"] = pd.to_numeric(
            scorecard_df["max_marks"], errors="coerce"
        ).fillna(0)
        scorecard_df["semester"] = pd.to_numeric(
            scorecard_df["semester"], errors="coerce"
        )

        # Count only completed assessments in earned marks.
        completed_mask = (
            scorecard_df["status"].astype(str).str.strip().str.lower()
            == "completed"
        )

        st.markdown("#### Semester-wise Performance Summary")
        sem_list = sorted(
            scorecard_df["semester"].dropna().unique().tolist()
        )
        summary_rows = []

        for semester_number in sem_list:
            semester_df = scorecard_df[
                scorecard_df["semester"] == semester_number
            ]
            completed_df = semester_df[
                semester_df["status"].astype(str).str.strip().str.lower()
                == "completed"
            ]

            marks_scored = completed_df["scored_marks"].sum()
            maximum_marks = completed_df["max_marks"].sum()
            percentage = (
                round((marks_scored / maximum_marks) * 100, 2)
                if maximum_marks > 0 else None
            )

            summary_rows.append({
                "Semester": f"Semester {int(semester_number)}",
                "Total Assessments": len(semester_df),
                "Completed Assessments": len(completed_df),
                "Marks Scored": f"{marks_scored:g} / {maximum_marks:g}",
                "Percentage": (
                    f"{percentage}%" if percentage is not None
                    else "Not available yet"
                )
            })

        if summary_rows:
            summary_table = pd.DataFrame(summary_rows)
            st.dataframe(
                summary_table,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No valid semester numbers were found in assessments.csv.")

        st.markdown("---")
        st.markdown("#### Detailed Assessment Marks")

        semester_options = ["All Semesters"] + [
            f"Semester {int(number)}" for number in sem_list
        ]
        selected_score_semester = st.selectbox(
            "Select Semester:", options=semester_options
        )

        inspect_df = scorecard_df.copy()
        if selected_score_semester != "All Semesters":
            semester_number = int(
                selected_score_semester.replace("Semester ", "")
            )
            inspect_df = inspect_df[
                inspect_df["semester"] == semester_number
            ]

        def calculate_assessment_percentage(row):
            is_completed = (
                str(row["status"]).strip().lower() == "completed"
            )
            if is_completed and row["max_marks"] > 0:
                return (
                    f"{(row['scored_marks'] / row['max_marks']) * 100:.1f}%"
                )
            return "Pending"

        inspect_df["Percentage"] = inspect_df.apply(
            calculate_assessment_percentage, axis=1
        )

        display_columns = [
            "semester", "course_code", "course_title",
            "assessment_type", "due_date", "scored_marks",
            "max_marks", "Percentage", "status"
        ]
        st.dataframe(
            inspect_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# PAGE 9: PLAN & CHECKLIST
# ==========================================
elif selected_page == "9. Plan & Checklist":
    st.markdown('<div class="main-header">Academic Plan & Action Checklist</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage course milestones, project deliverables, certifications, and revision plans</div>', unsafe_allow_html=True)

    if checklist_df.empty:
        checklist_df = pd.DataFrame(columns=["item_id", "title", "category", "semester", "target_date", "status", "notes"])

    # Checklist Overview
    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        st.metric("Total Checklist Items", len(checklist_df))
    with col_k2:
        done_cnt = len(checklist_df[checklist_df["status"] == "Completed"]) if not checklist_df.empty else 0
        st.metric("Completed Tasks", done_cnt)
    with col_k3:
        pending_cnt = len(checklist_df[checklist_df["status"] != "Completed"]) if not checklist_df.empty else 0
        st.metric("Pending Tasks", pending_cnt)

    st.markdown("---")
    st.markdown("#### 📝 Current Checklist Items")
    
    # Allow inline editing with st.data_editor
    edited_checklist = st.data_editor(
        checklist_df,
        use_container_width=True,
        num_rows="dynamic",
        key="checklist_editor"
    )

    if st.button("💾 Save Checklist Updates to `data/plan_checklist.csv`"):
        if save_csv_safe(edited_checklist, "plan_checklist.csv"):
            st.success("✅ Checklist updated and saved successfully!")
            st.rerun()

    st.markdown("---")
    st.markdown("#### ➕ Add New Checklist Item")
    with st.form("add_checklist_item_form"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            new_id = f"CHK{len(checklist_df) + 1:02d}"
            item_id = st.text_input("Item ID", value=new_id)
            title = st.text_input("Task Title", placeholder="e.g. Complete Lab Record")
        with f_col2:
            category = st.selectbox("Category", ["Study", "Exam Prep", "Assignment", "Lab Work", "Certification", "Career/Project", "Administration"])
            target_date = st.date_input("Target Date", value=datetime.date.today())
        with f_col3:
            semester = st.number_input("Semester", min_value=1, max_value=8, value=current_sem_num)
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        notes = st.text_input("Notes / Resources", placeholder="e.g. Reference chapter 4, lab instructor signoff")

        submitted = st.form_submit_button("Add Item")
        if submitted:
            if not title:
                st.error("Please enter a task title.")
            else:
                new_row = pd.DataFrame([{
                    "item_id": item_id,
                    "title": title,
                    "category": category,
                    "semester": int(semester),
                    "target_date": str(target_date),
                    "status": status,
                    "notes": notes
                }])
                checklist_df = pd.concat([checklist_df, new_row], ignore_index=True)
                if save_csv_safe(checklist_df, "plan_checklist.csv"):
                    st.success(f"Item `{title}` added successfully!")
                    st.rerun()

# ==========================================
# PAGE 10: ASK DEGREE AI
# ==========================================
elif selected_page == "10. Ask Degree AI":
    st.markdown('<div class="main-header">Ask Degree AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your student academic assistant for degree questions, syllabus lookup, and progress queries</div>', unsafe_allow_html=True)

    gemini_key = os.getenv("GEMINI_API_KEY", "")

    # Quick Suggestion Prompts
    st.markdown("**Suggested Quick Questions:**")
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    quick_query = None
    with quick_col1:
        if st.button("📅 Next Assessment?", use_container_width=True):
            quick_query = "What is my next upcoming assessment?"
    with quick_col2:
        if st.button("🌴 Next Holiday / Leave?", use_container_width=True):
            quick_query = "When is my next holiday or academic leave?"
    with quick_col3:
        if st.button("📚 Semester 5 Courses?", use_container_width=True):
            quick_query = "What courses am I taking in Semester 5?"
    with quick_col4:
        if st.button("📊 Degree Completion %?", use_container_width=True):
            quick_query = "What is my degree completion percentage and credits?"

    user_query = st.text_input(
        "Ask anything about your engineering degree, syllabus, assessments, or schedule:",
        value=quick_query if quick_query else "",
        placeholder="e.g. How many credits have I completed? or When is my next exam?"
    )

    if user_query:
        query_lower = user_query.lower()
        st.markdown("#### 🤖 Degree OS Response:")

        # Robust local logic based on loaded CSV data
        handled_locally = False
        local_response = ""

        if any(w in query_lower for w in ["next assessment", "next exam", "upcoming exam", "upcoming assessment", "ia1", "ia2"]):
            handled_locally = True
            if not assessments_df.empty and "due_date" in assessments_df.columns:
                pending = assessments_df[assessments_df["status"] != "Completed"].copy()
                if not pending.empty:
                    pending["due_date_parsed"] = pd.to_datetime(pending["due_date"], errors="coerce")
                    pending = pending.sort_values(by="due_date_parsed")
                    top3 = pending.head(3)
                    lines = [f"• **{r['assessment_type']}** for **{r['course_title']}** ({r['course_code']}) on **{r['due_date']}** (Status: {r['status']})" for _, r in top3.iterrows()]
                    local_response = "Here are your next upcoming assessments:\n\n" + "\n".join(lines)
                else:
                    local_response = "All recorded assessments are currently marked as Completed!"
            else:
                local_response = "Assessment records are currently unavailable."

        elif any(w in query_lower for w in ["holiday", "leave", "vacation", "break", "calendar"]):
            handled_locally = True
            if not calendar_df.empty and "category" in calendar_df.columns:
                leaves = calendar_df[calendar_df["category"] == "Leave"].copy()
                if not leaves.empty:
                    leaves["date_parsed"] = pd.to_datetime(leaves["date"], errors="coerce")
                    leaves = leaves.sort_values(by="date_parsed")
                    top_leaves = leaves.head(3)
                    lines = [f"• **{r['event_name']}** on **{r['date']}** ({r['academic_year']}, Semester {r['semester']})" for _, r in top_leaves.iterrows()]
                    local_response = "Here are your upcoming scheduled leaves and holidays:\n\n" + "\n".join(lines)
                else:
                    local_response = "No scheduled leaves found in the calendar."
            else:
                local_response = "Calendar records are currently unavailable."

        elif any(w in query_lower for w in ["credit", "completion", "progress", "degree %", "how many credits"]):
            handled_locally = True
            tot_req = int(uni_syllabus_df["total_credits_required"].values[0]) if not uni_syllabus_df.empty and "total_credits_required" in uni_syllabus_df.columns else 160
            comp_cr = int(courses_df[courses_df["status"] == "Completed"]["credits"].sum()) if not courses_df.empty else 0
            in_prog_cr = int(courses_df[courses_df["status"] == "In Progress"]["credits"].sum()) if not courses_df.empty else 0
            pct = round((comp_cr / tot_req) * 100, 1)
            local_response = (
                f"**Degree Completion Progress:**\n\n"
                f"• **Completed Credits:** {comp_cr} / {tot_req} credits ({pct}%)\n"
                f"• **Currently In Progress (Semester 5):** {in_prog_cr} credits\n"
                f"• **Remaining Credits to Graduate:** {tot_req - comp_cr} credits"
            )

        elif "semester 5" in query_lower or "current semester" in query_lower:
            handled_locally = True
            if not courses_df.empty:
                sem5_c = courses_df[courses_df["semester"] == 5]
                c_list = [f"• **{r['course_code']}**: {r['title']} ({r['credits']} Credits, {r['category']})" for _, r in sem5_c.iterrows()]
                local_response = f"**Semester 5 Registered Courses ({len(sem5_c)} total):**\n\n" + "\n".join(c_list)
            else:
                local_response = "No course data available."

        elif any(w in query_lower for w in ["score", "grade", "percentage", "cgpa", "gpa"]):
            handled_locally = True
            if not scores_df.empty:
                tot_sc = scores_df["scored_marks"].sum()
                tot_mx = scores_df["max_marks"].sum()
                pct = round((tot_sc / tot_mx) * 100, 2)
                weighted_gp = (scores_df["grade_point"] * scores_df["credits"]).sum()
                tot_cr = scores_df["credits"].sum()
                proto_gpa = round(weighted_gp / tot_cr, 2)
                local_response = (
                    f"**Scorecard Summary (Prototype Metrics):**\n\n"
                    f"• **Cumulative Percentage:** {pct}%\n"
                    f"• **Prototype Weighted Grade Point Average:** {proto_gpa} / 10.0\n"
                    f"• **Graded Semesters:** Semesters 1 through 4\n"
                    f"*(Note: Official university CGPA formulas vary and should be checked with university regulations.)*"
                )
            else:
                local_response = "No scores recorded yet."

        elif any(w in query_lower for w in ["checklist", "plan", "task", "todo"]):
            handled_locally = True
            if not checklist_df.empty:
                active_chk = checklist_df[checklist_df["status"] != "Completed"]
                items = [f"• **{r['title']}** [{r['category']}] (Due: {r['target_date']}) - Status: {r['status']}" for _, r in active_chk.iterrows()]
                local_response = f"**Active Checklist Items ({len(active_chk)} items):**\n\n" + "\n".join(items)
            else:
                local_response = "Your checklist is empty!"

        # Output the answer
        if handled_locally:
            st.success(local_response)
            st.caption("ℹ️ Answer generated directly from verified local CSV data.")
        else:
            # If not covered by specific keywords and Gemini API key is unavailable
            if not gemini_key:
                st.warning("⚠️ **AI API not connected** (GEMINI_API_KEY is not set).")
                st.info(
                    "Displaying local knowledge summary instead:\n\n"
                    f"• **Degree:** B.Tech Computer Science and Engineering\n"
                    f"• **Active Semester:** Semester 5\n"
                    f"• **Completed Credits:** {courses_df[courses_df['status']=='Completed']['credits'].sum() if not courses_df.empty else 84} / 160\n"
                    "• Try asking about your: 'next assessment', 'next holiday', 'semester 5 courses', 'credits progress', or 'checklist'."
                )
            else:
                # If Gemini API key is configured, perform live generative answering
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_key)
                    context_data = f"""
                    Degree Information:
                    - Programme: B.Tech CSE (4 Years, 160 Credits)
                    - Current Semester: 5 (In Progress)
                    - Completed Credits: {courses_df[courses_df['status']=='Completed']['credits'].sum() if not courses_df.empty else 84}
                    - Assessments: {assessments_df.to_dict(orient='records')[:8] if not assessments_df.empty else []}
                    - Courses: {courses_df[courses_df['semester']==5].to_dict(orient='records') if not courses_df.empty else []}
                    - Checklist: {checklist_df.to_dict(orient='records') if not checklist_df.empty else []}
                    """
                    prompt = f"You are the Degree OS Academic Advisor. Answer the student's question based strictly on their curriculum context:\n\nContext:\n{context_data}\n\nQuestion:\n{user_query}"
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    st.success(response.text)
                    st.caption("⚡ Powered by Gemini API")
                except Exception as ex:
                    st.error(f"Error calling Gemini API: {str(ex)}")

# ==========================================
# PAGE 11: DATA ADMIN
# ==========================================
elif selected_page == "11. Data Admin":
    st.markdown('<div class="main-header">Data Administration</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Directly edit, modify, and save all system CSV tables using Streamlit data editors</div>', unsafe_allow_html=True)

    table_choice = st.selectbox(
        "Choose Data Table to Edit:",
        [
            "courses.csv",
            "semesters.csv",
            "assessments.csv",
            "scores.csv",
            "calendar.csv",
            "plan_checklist.csv",
            "university_syllabus.csv"
        ]
    )

    target_df = load_csv_safe(table_choice)

    if target_df.empty:
        st.warning(f"Table `{table_choice}` is currently empty or missing.")
    else:
        st.markdown(f"#### Editing `{table_choice}` ({len(target_df)} rows)")
        st.caption("You can edit cells, add rows, or delete rows directly in the table below:")

        edited_df = st.data_editor(
            target_df,
            use_container_width=True,
            num_rows="dynamic",
            key=f"editor_{table_choice}"
        )

        btn_col1, btn_col2 = st.columns([1, 4])
        with btn_col1:
            if st.button("💾 Save Changes to CSV", type="primary"):
                if save_csv_safe(edited_df, table_choice):
                    st.success(f"✅ Successfully saved changes to `{table_choice}`!")
                    st.rerun()

        with btn_col2:
            csv_data = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {table_choice}",
                data=csv_data,
                file_name=table_choice,
                mime="text/csv"
            )

st.markdown("---")
st.markdown("<p style='text-align:center; color:#94A3B8; font-size:0.85rem;'>My Engineering Degree OS • AI Product Development Build Assignment • Build small. Make it work. Launch it.</p>", unsafe_allow_html=True)
