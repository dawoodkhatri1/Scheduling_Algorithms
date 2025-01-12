import time
from PIL import Image
import streamlit as st

# Scheduling Algorithms
def sjf(process_list):
    t = 0
    gantt = []
    completed = {}

    while process_list:
        available = [p for p in process_list if p[1] <= t]

        if not available:
            t += 1
            gantt.append("Idle")
            continue

        available.sort()
        process = available[0]

        burst_time, arrival_time, pid = process
        t += burst_time
        gantt.append(pid)

        ct = t
        tt = ct - arrival_time
        wt = tt - burst_time

        process_list.remove(process)
        completed[pid] = [ct, tt, wt]

    return gantt, completed


def fcfs(process_list):
    t = 0
    gantt = []
    completed = {}

    process_list.sort(key=lambda p: p[1])

    while process_list:
        if process_list[0][1] > t:
            t += 1
            gantt.append("Idle")
            continue

        process = process_list.pop(0)
        pid, burst_time, arrival_time = process[2], process[0], process[1]
        gantt.append(pid)

        t += burst_time
        ct = t
        tt = ct - arrival_time
        wt = tt - burst_time

        completed[pid] = [ct, tt, wt]

    return gantt, completed


def priority(process_list):
    t = 0
    gantt = []
    completed = {}

    while process_list:
        available = [p for p in process_list if p[3] <= t]

        if not available:
            t += 1
            gantt.append("Idle")
            continue

        available.sort(key=lambda p: p[0])  # Sort by priority
        process = available[0]
        process_list.remove(process)

        pid, priority_level, burst_time, arrival_time = process[1], process[0], process[2], process[3]
        gantt.append(pid)

        t += burst_time
        ct = t
        tt = ct - arrival_time
        wt = tt - burst_time

        completed[pid] = [ct, tt, wt]

    return gantt, completed


def round_robin(process_list, time_quanta):
    t = 0
    gantt = []
    completed = {}
    burst_times = {p[2]: p[0] for p in process_list}

    while process_list:
        available = [p for p in process_list if p[1] <= t]

        if not available:
            gantt.append("Idle")
            t += 1
            continue

        process = available[0]
        process_list.remove(process)

        pid, burst_time, arrival_time = process[2], process[0], process[1]

        if burst_time <= time_quanta:
            t += burst_time
            gantt.append(pid)
            ct = t
            tt = ct - arrival_time
            wt = tt - burst_times[pid]
            completed[pid] = [ct, tt, wt]
        else:
            t += time_quanta
            burst_time -= time_quanta
            process_list.append([burst_time, arrival_time, pid])
            gantt.append(pid)

    return gantt, completed

# Streamlit UI
st.set_page_config(
    page_title="Scheduling Algorithms",
    page_icon="🚀",
    layout="centered"
)

# Add a header with animation
st.markdown("""
    <style>
        .animated-title {
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0); }
        }
    </style>
    <div class="animated-title" style="text-align: center;">
        <h2 style='color: #4CAF50;'>Efficient Process Scheduling Made Simple</h2>
    </div>
""", unsafe_allow_html=True)

# Load the image
image = Image.open("banner2.jpeg")  # Correct path or URL
st.image(image, caption="Process Scheduling Algorithms", use_container_width=True)

# Sidebar options
st.sidebar.title("Process List Selection")

# Manage button states using session_state
if "processes" not in st.session_state:
    st.session_state["processes"] = []
if "custom" not in st.session_state:
    st.session_state["custom"] = False
if "predefined" not in st.session_state:
    st.session_state["predefined"] = False

if st.sidebar.button("User Input Process List"):
    st.session_state["custom"] = True
    st.session_state["predefined"] = False

if st.sidebar.button("Predefined Process List"):
    st.session_state["predefined"] = True
    st.session_state["custom"] = False

# Process List Selection Logic
if st.session_state["custom"]:
    num_processes = st.sidebar.number_input("Number of Processes", min_value=1, max_value=20, value=5)
    st.session_state["processes"] = []
    for i in range(num_processes):
        st.sidebar.write(f"### Process P{i+1}")
        burst_time = st.sidebar.number_input(f"Burst Time of P{i+1}", min_value=1, value=5, key=f"burst_{i}")
        arrival_time = st.sidebar.number_input(f"Arrival Time of P{i+1}", min_value=0, value=0, key=f"arrival_{i}")
        st.session_state["processes"].append([burst_time, arrival_time, f"P{i+1}"])

elif st.session_state["predefined"]:
    st.session_state["processes"] = [
        [6, 2, "P1"],
        [2, 5, "P2"],
        [8, 1, "P3"],
        [3, 0, "P4"],
        [4, 4, "P5"]
    ]

# Algorithm selection
st.sidebar.title("Choose Scheduling Algorithm")
algorithm = st.sidebar.selectbox(
    "Select an algorithm:",
    ("SJF", "FCFS", "Priority", "Round Robin")
)

# For Priority Scheduling: Ask for Priority Values
if algorithm == "Priority" and st.session_state["processes"]:
    st.sidebar.write("### Set Priorities")
    priority_values = [
        st.sidebar.number_input(f"Priority for {process[2]}:", min_value=1, max_value=10, value=5, key=f"priority_{i}")
        for i, process in enumerate(st.session_state["processes"])
    ]
    st.session_state["processes"] = [
        [priority_values[i], process[2], process[0], process[1]]
        for i, process in enumerate(st.session_state["processes"])
    ]

# Display process table
if st.session_state["processes"]:
    st.write("### Process List")
    process_table = {
        "Process ID": [p[2] if algorithm != "Priority" else p[1] for p in st.session_state["processes"]],
        "Burst Time": [p[0] if algorithm != "Priority" else p[2] for p in st.session_state["processes"]],
        "Arrival Time": [p[1] if algorithm != "Priority" else p[3] for p in st.session_state["processes"]]
    }
    if algorithm == "Priority":
        process_table["Priority"] = [p[0] for p in st.session_state["processes"]]
    st.table(process_table)

# Round Robin: Get time quantum
if algorithm == "Round Robin" and st.session_state["processes"]:
    time_quanta = st.sidebar.slider("Select Time Quanta", 1, 10, 2)

# Run the algorithm and display results
if st.session_state["processes"] and st.button("Run Algorithm"):
    with st.spinner("Running the algorithm..."):
        time.sleep(2)  # Simulate delay for processing

    if algorithm == "SJF":
        gantt, completed = sjf([p.copy() for p in st.session_state["processes"]])
    elif algorithm == "FCFS":
        gantt, completed = fcfs([p.copy() for p in st.session_state["processes"]])
    elif algorithm == "Priority":
        gantt, completed = priority([p.copy() for p in st.session_state["processes"]])
    elif algorithm == "Round Robin":
        gantt, completed = round_robin([p.copy() for p in st.session_state["processes"]], time_quanta)

    # Display Results
    st.write("### Gantt Chart")
    gantt_chart = " -> ".join(gantt)
    st.markdown(f"<h3 style='text-align: center; color: #0073e6;'>{gantt_chart}</h3>", unsafe_allow_html=True)

    st.write("### Process Completion Details")
    result_table = {
        "Process ID": list(completed.keys()),
        "Completion Time": [v[0] for v in completed.values()],
        "Turnaround Time": [v[1] for v in completed.values()],
        "Waiting Time": [v[2] for v in completed.values()]
    }
    st.table(result_table)
