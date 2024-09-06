import streamlit as st
import random
import base64
import time
from loadSecret import loadconfig
from streamlit_google_auth import Authenticate
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import requests
import logging
import json



# Lists of feedback messages
correct_messages = [
    "Great job! 🎉",
    "Excellent work! 👏",
    "You're on fire! 🔥",
    "Fantastic! Keep it up! 💪",
    "You're a math wizard! 🧙‍♂️",
    "Brilliant! You've got this! ✨",
    "Amazing work! You're crushing it! 💯",
    "Superb! You're making great progress! 🚀",
    "Wow! You're really good at this! 🌟",
    "Incredible! You're a math superstar! 🏆"
]

incorrect_messages = [
    "Nice try! Keep practicing! 💪",
    "Don't give up! You're learning! 📚",
    "Almost there! Give it another shot! 🎯",
    "Practice makes perfect! You've got this! 🌟",
    "Keep going! Every attempt makes you stronger! 💪",
    "You're making progress! Keep it up! 🚀",
    "Good effort! Let's try again! 🔄",
    "Stay positive! You're getting better with each try! 😊",
    "Mistakes help us learn! Keep pushing forward! 🌈",
    "You're doing great! Learning takes time! ⏳"
]

def display_home_button():
    return st.button("🏠 Home ", key="home_button")


def show_operation_selection():
    # Settings section
    st.sidebar.header("Settings") 
     # Problem Type Selection
    st.session_state.problem_type = st.sidebar.radio(
        "Select Problem Type:",
        options=["Number Problem", "Word Problem"],
        index=0,  # Default to "Number Problem"
        key="problem_type_radio"
    )   
    max_digits = st.sidebar.slider("Select maximum number of digits:", min_value=1, max_value=5, value=1)
    
    min_limit, max_limit = get_number_range_limits(max_digits)
    
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_num = st.number_input("Minimum number:", min_value=min_limit, max_value=max_limit, value=min_limit)
    with col2:
        max_num = st.number_input("Maximum number:", min_value=min_limit, max_value=max_limit, value=max_limit)
    # Add GIF display time setting
    
    
      # Add GIF display time setting
    #gif_display_time = st.sidebar.number_input("GIF display time (seconds):", min_value=1, max_value=15, value=5)
    
     # Add GIF display time setting
    st.session_state.gif_display_time = st.sidebar.number_input(
        "GIF display time (seconds):", 
        min_value=1, 
        max_value=15, 
        value=st.session_state.gif_display_time
    )
    
    
    if min_num > max_num:
        st.sidebar.error("Minimum number cannot be greater than maximum number.")
        st.stop()

    number_range = (min_num, max_num)

    st.markdown("<h2 style='text-align: center;'>Choose an operation:</h2>", unsafe_allow_html=True)

    operations = [
        ("➕ Addition", "Addition"),
        ("➖ Subtraction", "Subtraction"),
        ("✖️ Multiplication", "Multiplication"),
        ("➗ Division", "Division"),
        ("🔀 Mixed", "Mixed")
    ]

    # Create columns for operation buttons
    cols = st.columns(len(operations))

    for i, (op_label, op_value) in enumerate(operations):
        with cols[i]:
            if st.button(op_label, key=f"op_{op_value}", help=f"Click to start {op_value} practice"):
                st.session_state.test_started = True
                st.session_state.selected_operation = op_value
                st.session_state.number_range = number_range
                st.rerun()

    # Custom CSS to style the buttons
    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        padding: 10px 15px;
        background-color: #4CAF50;
        border: none;
        color: white;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        transition-duration: 0.4s;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)   
        
def display_rightside_gif(gif_path, width=300):
    duration = st.session_state.gif_display_time 
    with open(gif_path, "rb") as file:
        contents = file.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    
    st.markdown(
        f"""
        <style>
        .rightside-gif {{
            position: fixed;
            top: 50%;
            right: 20px;
            transform: translateY(-50%);
            width: {width}px;
            z-index: 9999;
        }}
        </style>
        <img src="data:image/gif;base64,{data_url}" class="rightside-gif">
        """,
        unsafe_allow_html=True
    )
    
    # Create a placeholder to remove the GIF later
    placeholder = st.empty()
    
    # Wait for the specified duration
    time.sleep(duration)
    
    # Remove the GIF and its style
    placeholder.markdown(
        """
        <style>
        .rightside-gif {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
def display_fullscreen_gif(gif_path, duration=10):
    with open(gif_path, "rb") as file:
        contents = file.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    
    st.markdown(
        f"""
        <style>
        .fullscreen-gif {{
            position: fixed;
            top: 0;
            left: 0;
            width: 50vw;
            height: 50vh;
            object-fit: cover;
            z-index: 9999;
        }}
        </style>
        <img src="data:image/gif;base64,{data_url}" class="fullscreen-gif">
        """,
        unsafe_allow_html=True
    )
    time.sleep(duration)
    st.empty()  # Clear the GIF

def get_number_range_limits(max_digits):
    if max_digits == 1:
        return 1, 9
    elif max_digits == 2:
        return 1, 99
    elif max_digits == 3:
        return 1, 999
    else:  # max_digits == 4
        return 1, 9999
    
def get_number_range_options(max_digits):
    if max_digits == 1:
        return [(1, 9)]
    elif max_digits == 2:
        return [(1, 9), (10, 99)]
    elif max_digits == 3:
        return [(1, 9), (10, 99), (100, 999)]
    else:  # max_digits == 4
        return [(1, 9), (10, 99), (100, 999), (1000, 9999)]


def generate_question(operation, number_range):
    min_num, max_num = number_range

    a = random.randint(min_num, max_num)
    b = random.randint(min_num, max_num)

    if operation == "Addition":
        question = f"Perform addition of the following numbers and select the correct answer:\n\n<div style='font-size: 24px; text-align: center;'>{a} + {b} = ?</div>"
        correct_answer = a + b
    elif operation == "Subtraction":
        if a < b:
            a, b = b, a
        question = f"Perform subtraction of the following numbers and select the correct answer:\n\n<div style='font-size: 24px; text-align: center;'>{a} - {b} = ?</div>"
        correct_answer = a - b
    elif operation == "Multiplication":
        question = f"Perform multiplication of the following numbers and select the correct answer:\n\n<div style='font-size: 24px; text-align: center;'>{a} × {b} = ?</div>"
        correct_answer = a * b
    elif operation == "Division":
        b = max(1, b)  # Ensure b is not zero
        a = b * random.randint(1, 10)  # Ensure clean division
        question = f"Perform division of the following numbers and select the correct answer:\n\n<div style='font-size: 24px; text-align: center;'>{a} ÷ {b} = ?</div>"
        correct_answer = a // b
    else:  # Mixed
        return generate_question(random.choice(["Addition", "Subtraction", "Multiplication", "Division"]), number_range)

    options = [correct_answer]
    while len(options) < 4:
        wrong_answer = correct_answer + random.randint(-10, 10)
        if wrong_answer not in options and wrong_answer >= 0:
            options.append(wrong_answer)
    random.shuffle(options)

    return question, correct_answer, options

def display_reward_points():
    reward_points = st.session_state.score+0 if 'score' in st.session_state else 0   
    st.markdown(
        f"""
        <div class="reward-points">
            🏆 Reward Points: {reward_points}
        </div>
        <style>
        .reward-points {{
            position: fixed;
            top: 80;
            left: 100;
            padding: 10px;
            background-color: #f0f2f6;
            border-radius: 0 0 10px 0;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            z-index: 9999;
            font-weight: bold;
            font-size: 16px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
def display_second_title(operation):
    reward_points = st.session_state.score+0 if 'score' in st.session_state else 0   
    st.markdown(
        f"""
        <div class="reward-points">
            🏆 Reward Points: {reward_points} 🏆 :     {operation} Practice
        </div>
        <style>
        .reward-points {{
            position: fixed;
            top: 80;
            left: 100;
            padding: 10px;
            background-color: #f0f2f6;
            border-radius: 0 0 10px 0;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            z-index: 9999;
            font-weight: bold;
            font-size: 16px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def practice_math(operation, number_range):
    # Add custom CSS for button styling and animations
    st.markdown("""
    <style>
    @keyframes blink {
        0% { box-shadow: 0 0 15px #ffff00; }
        50% { box-shadow: none; }
        100% { box-shadow: 0 0 15px #ffff00; }
    }
    .blink-button {
        animation: blink 1s linear infinite;
    }
    .disabled-button {
        opacity: 0.6;
        cursor: not-allowed;
    }
    .stButton button {
        width: 100%;
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    if 'current_question' not in st.session_state:
        st.session_state.current_question = generate_question(operation, number_range)
        st.session_state.question_count += 1
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
        
    display_second_title(operation)
   
    st.markdown(f"<p style='text-align: center;'></p>", unsafe_allow_html=True)
    question, correct_answer, options = st.session_state.current_question

    st.write(f"Question {st.session_state.question_count}/15:")
    st.markdown(question, unsafe_allow_html=True)
    
    # Add gap between answer options
    st.markdown(
        """
        <style>
        div.row-widget.stRadio > div{
            flex-direction: column;
            gap: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    user_answer = st.radio("Select your answer:", options, key=f"user_answer_{operation}")

    # Display feedback if available
    if st.session_state.feedback:
        if st.session_state.feedback[0] == "success":
            st.success(st.session_state.feedback[1])
        else:
            st.error(st.session_state.feedback[1])
        st.session_state.feedback = None  # Clear feedback after displaying

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        submit_disabled = st.session_state.get('submit_disabled', False)
        submit_button = st.button("Submit", key=f"submit_{operation}", disabled=submit_disabled)
        if submit_button and not submit_disabled:
            st.session_state.submitted = True
            st.session_state.attempted += 1
            if user_answer == correct_answer:
                feedback_message = random.choice(correct_messages)
                st.session_state.feedback = ("success", f"✅ {feedback_message} You earned 1 reward point.")
                st.session_state.score += 1
                st.session_state.correct += 1
                # Trigger right-side GIF display
                display_rightside_gif("./img/pass/thumbs-up-2584_256.gif", width=300)
                
            else:
                feedback_message = random.choice(incorrect_messages)
                st.session_state.feedback = ("error", f"❌ {feedback_message}")
                display_rightside_gif("./img/fail/farded-emoticon-emoticon.gif", width=300)
            st.session_state.submit_disabled = True
            st.rerun()

    with col2:
        next_button_class = "blink-button" if st.session_state.get('submit_disabled', False) else ""
        if st.button("Next Question", key=f"next_{operation}", help="Click to move to the next question"):
            st.session_state.current_question = generate_question(operation, number_range)
            st.session_state.question_count += 1
            st.session_state.submitted = False
            st.session_state.feedback = None
            st.session_state.submit_disabled = False
            st.rerun()
        
        # Add blinking effect using JavaScript
        if next_button_class:
            st.markdown(f"""
            <script>
                var nextButton = document.querySelector('button[kind="secondary"]:nth-of-type(2)');
                nextButton.classList.add('{next_button_class}');
            </script>
            """, unsafe_allow_html=True)

    with col3:
        show_answer_class = "blink-button" if st.session_state.get('submit_disabled', False) else ""
        if st.button("Show Answer", key=f"show_answer_{operation}", help="Click to see the correct answer"):
            st.session_state.feedback = ("success", f"The correct answer is: {correct_answer}")
            st.rerun()
        
        # Add blinking effect using JavaScript
        if show_answer_class:
            st.markdown(f"""
            <script>
                var showAnswerButton = document.querySelector('button[kind="secondary"]:nth-of-type(3)');
                showAnswerButton.classList.add('{show_answer_class}');
            </script>
            """, unsafe_allow_html=True)

    with col4:
        if st.button("Finish Test", key=f"finish_{operation}") or st.session_state.question_count >= 15:
            st.session_state.test_finished = True
            st.rerun()

    # Add the footer
    create_footer()
 

def practice_math_old(operation, number_range):
    
     # Add this at the beginning of the function
    st.markdown("""
    <style>
    @keyframes blink {
        0% { box-shadow: 0 0 15px #ffff00; }
        50% { box-shadow: none; }
        100% { box-shadow: 0 0 15px #ffff00; }
    }
    .blink-button {
        animation: blink 1s linear infinite;
    }
    .disabled-button {
        opacity: 0.6;
        cursor: not-allowed;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    if 'attempted' not in st.session_state:
        st.session_state.attempted = 0
    if 'correct' not in st.session_state:
        st.session_state.correct = 0
    if 'current_question' not in st.session_state:
        st.session_state.current_question = generate_question(operation, number_range)
        st.session_state.question_count += 1
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None

    display_reward_points()   

    #st.title(f"{operation} Practice")
    # Section title for the current operation
    st.markdown(f"<h2 style='text-align: center; margin: 0;'> {operation} Practice </h2>", unsafe_allow_html=True)
    question, correct_answer, options = st.session_state.current_question

    st.write(f"Question {st.session_state.question_count}/15:")
    st.markdown(question, unsafe_allow_html=True)
    
    # Add gap between answer options
    st.markdown(
        """
        <style>
        div.row-widget.stRadio > div{
            flex-direction: column;
            gap: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    user_answer = st.radio("Select your answer:", options, key=f"user_answer_{operation}")

    # Display feedback if available
    if st.session_state.feedback:
        if st.session_state.feedback[0] == "success":
            st.success(st.session_state.feedback[1])
            # Trigger right-side GIF display
            display_rightside_gif("./img/pass/thumbs-up-2584_256.gif", width=300)
            
        else:
            st.error(st.session_state.feedback[1])
            # Trigger right-side GIF display                
            display_rightside_gif("./img/fail/farded-emoticon-emoticon.gif", width=300)
        st.session_state.feedback = None  # Clear feedback after displaying

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        submit_disabled = st.session_state.get('submit_disabled', False)
        submit_button = st.button("Submit", key=f"submit_{operation}", disabled=submit_disabled)
        if submit_button and not submit_disabled:
            st.session_state.submitted = True
            st.session_state.attempted += 1
            if user_answer == correct_answer:
                feedback_message = random.choice(correct_messages)
                st.session_state.feedback = ("success", f"✅ {feedback_message} You earned 1 reward point.")
                st.session_state.score += 1
                st.session_state.correct += 1
                display_rightside_gif("./img/pass/thumbs-up-2584_256.gif", width=300)
                
            else:
                feedback_message = random.choice(incorrect_messages)
                st.session_state.feedback = ("error", f"❌ {feedback_message}")
            st.session_state.submit_disabled = True
            st.rerun()

    with col2:
        next_button_class = "blink-button" if st.session_state.get('submit_disabled', False) else ""
        st.markdown(f"""
        <button class="stButton {next_button_class}" onclick="document.getElementById('next_{operation}').click();">
            Next Question
        </button>
        """, unsafe_allow_html=True)
        if st.button("Next Question", key=f"next_{operation}", help="Click to move to the next question"):
            st.session_state.current_question = generate_question(operation, number_range)
            st.session_state.question_count += 1
            st.session_state.submitted = False
            st.session_state.feedback = None
            st.session_state.submit_disabled = False
            st.rerun()

    with col3:
        show_answer_class = "blink-button" if st.session_state.get('submit_disabled', False) else ""
        st.markdown(f"""
        <button class="stButton {show_answer_class}" onclick="document.getElementById('show_answer_{operation}').click();">
            Show Answer
        </button>
        """, unsafe_allow_html=True)
        if st.button("Show Answer", key=f"show_answer_{operation}", help="Click to see the correct answer"):
            st.session_state.feedback = ("success", f"The correct answer is: {correct_answer}")
            st.rerun()

    with col4:
        if st.button("Finish Test", key=f"finish_{operation}") or st.session_state.question_count >= 15:
            st.session_state.test_finished = True
            st.rerun()

    if st.button("Back to Operation Selection"):
        if st.warning("Are you sure you want to terminate this test? Your session will be cleared."):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Add the footer
    create_footer()

def show_summary():
    display_reward_points()
    st.title("Test Summary")
    total_questions = st.session_state.question_count
    attempted = st.session_state.attempted
    correct = st.session_state.correct
    incorrect = attempted - correct
    score_percentage = (correct / attempted) * 100 if attempted > 0 else 0

    st.write(f"Total Questions Seen: {total_questions}")
    st.write(f"Questions Attempted: {attempted}")
    
    st.markdown(f"""
    <div style="font-size: 2em; color: green; font-weight: bold;">
        Correct Answers: {correct}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="font-size: 2em; color: red; font-weight: bold;">
        Incorrect Answers: {incorrect}
    </div>
    """, unsafe_allow_html=True)
    
    st.write(f"Score Percentage: {score_percentage:.2f}%")

    if st.button("Start New Test"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
def create_footer():
    footer = st.container()
    with footer:
        st.markdown("""
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            color: black;
            text-align: center;
            padding: 10px 0;
            font-size: 14px;
            z-index: 999;
        }
        </style>
        """, unsafe_allow_html=True)

        total_questions = st.session_state.question_count
        attempted = st.session_state.attempted
        correct = st.session_state.correct
        score = st.session_state.score

        st.markdown(f"""
        <div class="footer">
            Total Questions: {total_questions} | 
            Attempted: {attempted} | 
            Correct: {correct} | 
            Score: {score}
        </div>
        """, unsafe_allow_html=True)
        
def create_operation_card(operation, color):
    return f"""
    <div class="operation-card" 
         style="
            background-color: {color};
            padding: 20px;
            border-radius: 10px;
            margin: 0 10px;
            text-align: center;
            cursor: pointer;
            width: 120px;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
         "
         onclick="selectOperation('{operation}')"
    >
        <h3 style="color: white; margin: 0;">{operation}</h3>
    </div>
    """
def practice_mathwordproblem(operation, number_range):
    # This function will be similar to practice_math, but tailored for word problems
    
    # Add custom CSS for button styling and animations (same as in practice_math)
    st.markdown("""
    <style>
    @keyframes blink {
        0% { box-shadow: 0 0 15px #ffff00; }
        50% { box-shadow: none; }
        100% { box-shadow: 0 0 15px #ffff00; }
    }
    .blink-button {
        animation: blink 1s linear infinite;
    }
    .disabled-button {
        opacity: 0.6;
        cursor: not-allowed;
    }
    .stButton button {
        width: 100%;
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    if 'current_question' not in st.session_state:
        st.session_state.current_question = generate_word_question(operation, number_range)
        st.session_state.question_count += 1
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None

    display_reward_points()

    st.markdown(f"<h2 style='text-align: center;'>{operation} Word Problem Practice</h2>", unsafe_allow_html=True)

    question, correct_answer, options = st.session_state.current_question

    st.write(f"Question {st.session_state.question_count}/15:")
    st.markdown(question, unsafe_allow_html=True)
    
    # Add gap between answer options
    st.markdown(
        """
        <style>
        div.row-widget.stRadio > div{
            flex-direction: column;
            gap: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    user_answer = st.radio("Select your answer:", options, key=f"user_answer_{operation}")

    # Display feedback if available
    if st.session_state.feedback:
        if st.session_state.feedback[0] == "success":
            st.success(st.session_state.feedback[1])
        else:
            st.error(st.session_state.feedback[1])
        st.session_state.feedback = None  # Clear feedback after displaying

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        submit_disabled = st.session_state.get('submit_disabled', False)
        submit_button = st.button("Submit", key=f"submit_{operation}", disabled=submit_disabled)
        if submit_button and not submit_disabled:
            st.session_state.submitted = True
            st.session_state.attempted += 1
            if user_answer == correct_answer:
                feedback_message = random.choice(correct_messages)
                st.session_state.feedback = ("success", f"✅ {feedback_message} You earned 1 reward point.")
                st.session_state.score += 1
                st.session_state.correct += 1
                # Trigger right-side GIF display
                display_rightside_gif("./img/pass/thumbs-up-2584_256.gif", width=300)
            else:
                feedback_message = random.choice(incorrect_messages)
                st.session_state.feedback = ("error", f"❌ {feedback_message}")
                display_rightside_gif("./img/fail/farded-emoticon-emoticon.gif", width=300)                        
            st.session_state.submit_disabled = True
            st.rerun()

    with col2:
        next_button_class = "blink-button" if st.session_state.get('submit_disabled', False) else ""
        if st.button("Next Question", key=f"next_{operation}", help="Click to move to the next question"):
            st.session_state.current_question = generate_word_question(operation, number_range)
            st.session_state.question_count += 1
            st.session_state.submitted = False
            st.session_state.feedback = None
            st.session_state.submit_disabled = False
            st.rerun()
        
        # Add blinking effect using JavaScript
        if next_button_class:
            st.markdown(f"""
            <script>
                var nextButton = document.querySelector('button[kind="secondary"]:nth-of-type(2)');
                nextButton.classList.add('{next_button_class}');
            </script>
            """, unsafe_allow_html=True)

    with col3:
        show_answer_class = "blink-button" if st.session_state.get('submit_disabled', False) else ""
        if st.button("Show Answer", key=f"show_answer_{operation}", help="Click to see the correct answer"):
            st.session_state.feedback = ("success", f"The correct answer is: {correct_answer}")
            st.rerun()
        
        # Add blinking effect using JavaScript
        if show_answer_class:
            st.markdown(f"""
            <script>
                var showAnswerButton = document.querySelector('button[kind="secondary"]:nth-of-type(3)');
                showAnswerButton.classList.add('{show_answer_class}');
            </script>
            """, unsafe_allow_html=True)

    with col4:
        if st.button("Finish Test", key=f"finish_{operation}") or st.session_state.question_count >= 15:
            st.session_state.test_finished = True
            st.rerun()

    # Add the footer
    create_footer()

def generate_word_question(operation, number_range):
    min_num, max_num = number_range
    num1 = random.randint(min_num, max_num)
    num2 = random.randint(min_num, max_num)
    
    if operation == "Addition":
        question = f"If you have {num1} apples and your friend gives you {num2} more, how many apples do you have in total?"
        answer = num1 + num2
    elif operation == "Subtraction":
        question = f"You have {num1} candies and give {num2} to your friend. How many candies do you have left?"
        answer = num1 - num2
    elif operation == "Multiplication":
        question = f"If you have {num1} bags of marbles, and each bag contains {num2} marbles, how many marbles do you have in total?"
        answer = num1 * num2
    elif operation == "Division":
        num1, num2 = max(num1, num2), min(num1, num2)
        if num2 == 0:
            num2 = 1
        product = num1 * num2
        question = f"If you have {product} stickers and want to divide them equally among {num2} friends, how many stickers will each friend get?"
        answer = num1
    else:  # Mixed
        return generate_word_question(random.choice(["Addition", "Subtraction", "Multiplication", "Division"]), number_range)

    options = [answer, answer + 1, answer - 1, answer + 2]
    random.shuffle(options)
    
    return question, str(answer), [str(opt) for opt in options]

def main():
    st.set_page_config(layout="wide")  # Set the page to wide mode for better layout
    #api_key = st.secrets["API_KEY"]
    # Set up logging

    
    
    loadconfig()
    logging.basicConfig(level=logging.DEBUG)
    # Load client configuration from the JSON file
    with open('google_credentials.json', 'r') as f:
        client_config = json.load(f)
    
    # Extract client_id and client_secret
    client_id = client_config['web']['client_id']
    client_secret = client_config['web']['client_secret']
    #st.write("Here's the main content of your app")
    #st.write('client_id:',client_id)
    #st.write('client_secret:',client_secret)
    
    scopes = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
    ]
    # Set up OAuth 2.0 flow
    flow = Flow.from_client_secrets_file(
        'google_credentials.json',
        scopes=scopes,
        redirect_uri='https://yogi-math-practice.streamlit.app/'  # Update this for production
    )
    

    # Check if we're handling the OAuth callback
    if 'code' in st.query_params:
        try:
            code = st.query_params.get('code')
            flow.fetch_token(
                code=code,
                client_id=client_id,
                client_secret=client_secret,
            )
            credentials = flow.credentials

            # Use the credentials to get user info
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()

            st.success("Authentication successful!")
            st.write(f"Welcome, {user_info['name']}!")
            st.session_state.user_info = user_info
            st.session_state.credentials = credentials.to_json()
        except Exception as e:
            st.error(f"An error occurred during authentication: {str(e)}")
            logging.exception("Detailed error information:")
    elif 'credentials' in st.session_state:
        # User is already authenticated
        credentials = Credentials.from_authorized_user_info(eval(st.session_state.credentials))
        st.write(f"Welcome back, {st.session_state.user_info['name']}!")
    else:
        # If we're not handling a callback and user is not authenticated, show the login button
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f'[Login with Google]({auth_url})')

    # Rest of your Streamlit app code goes here
    if 'credentials' in st.session_state:
        # User is authenticated, show the main app content
        st.write("Here's the main content of your app")
        # ... (your existing app logic)

    # Add a logout button
    if 'credentials' in st.session_state and st.button('Logout'):
        del st.session_state.credentials
        del st.session_state.user_info
        st.rerun()
        
        

    
    # Initialize session state variables
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    if 'test_finished' not in st.session_state:
        st.session_state.test_finished = False
    if 'selected_operation' not in st.session_state:
        st.session_state.selected_operation = None
    if 'gif_display_time' not in st.session_state:
        st.session_state.gif_display_time = 1  # Default to 5 seconds
    if 'problem_type' not in st.session_state:
        st.session_state.problem_type = "Number Problem"  # Default to Number Problem
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'attempted' not in st.session_state:
        st.session_state.attempted = 0
    if 'correct' not in st.session_state:
        st.session_state.correct = 0
    
        
    # Add custom CSS for layout and buttons
    st.markdown("""
    <style>
    .home-button {
        margin-top: 20px;
    }
    .main-title {
        margin-top: 0;
        padding-top: 0;
    }
    .stButton > button {
        padding: 10px 15px;
        background-color: #4CAF50;
        border: none;
        color: white;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        transition-duration: 0.4s;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display reward points at the very beginning
    #display_reward_points()
    
    # Create a layout for the home button and title
    col1, col2 = st.columns([1, 5])
    
    with col1:
        home_clicked = st.button("🏠 Home", key="home_button", help="Return to operation selection")
    
    with col2:
        st.markdown("<h1 class='main-title'>Math Practice for Kids (Grades 1-3)</h1>", unsafe_allow_html=True)
    
    # Handle home button click
    if home_clicked:
        # Reset all session state variables
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    if 'submit_disabled' not in st.session_state:
        st.session_state.submit_disabled = False
        
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False

    if 'test_finished' not in st.session_state:
        st.session_state.test_finished = False

    if 'selected_operation' not in st.session_state:
        st.session_state.selected_operation = None

    if st.session_state.test_finished:
        show_summary()
    elif not st.session_state.test_started:
        show_operation_selection()
    else:
        if st.session_state.problem_type == "Number Problem":
            practice_math(st.session_state.selected_operation, st.session_state.number_range)
        else:
            practice_mathwordproblem(st.session_state.selected_operation, st.session_state.number_range)

    # Add the footer
    create_footer()

if __name__ == "__main__":
    main()