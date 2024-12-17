
import os
from dotenv import load_dotenv
import streamlit as st
import speech_recognition as sr
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from gtts import gTTS
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import random
import time
import requests
import numpy as np
from scipy.io import wavfile
import io
from pathlib import Path
import sounddevice as sd
import google.generativeai as genai
import pyttsx3
import wave
import plotly.graph_objects as go
import pandas as pd
from threading import Thread

def configure():
    load_dotenv()


# Constants for Clarifai API
PAT = os.getenv('PAT')
USER_ID = 'anthropic'
APP_ID = 'completion'
MODEL_ID = 'claude-3-opus'
MODEL_VERSION_ID = '0b59b93d35864b9b88699a557629babf'


class VoiceAssistant:
    def __init__(self):
        # Configure Google Generative AI (Gemini)
        try:
            api_key = os.getenv("GOOGLE_AI_API_KEY") or st.secrets.get("GOOGLE_AI_API_KEY")

            if not api_key:
                st.error("Google AI API Key is missing. Please configure it.")
                st.stop()

            genai.configure(api_key=api_key)

            # Initialize speech recognition and TTS engine
            self.model = genai.GenerativeModel(model_name='gemini-1.5-flash')
            self.recognizer = sr.Recognizer()
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty("rate", 150)  # Adjust speaking rate
            self.tts_engine.setProperty("volume", 0.8)  # Set volume

        except Exception as e:
            st.error(f"Initialization Error: {e}")
            st.stop()

    @st.cache_resource
    def generate_response(_self, user_message):
        """Generate a response using Google Generative AI."""
        if not user_message:
            return "Sorry, I didn't hear anything."

        try:
            # Create a prompt that limits the scope to self-help and personal questions
            prompt = f"""Answer as a mental health therapist in English language only. Reply within 100 words. 
            Answer only mental health related questions, if not reply 'I cannot answer that question'.
            User message: {user_message}"""
        
            response = _self.model.generate_content(prompt)
            return response.text.strip()  # Return the full response without character limit
        except Exception as e:
            st.error(f"AI response generation error: {e}")
            return "Sorry, I encountered an error processing your request."
        
    def record_audio(self, duration=5):
        """Record audio from the microphone and save as WAV file."""
        try:
            st.info(f"Recording for {duration} seconds...")
            recording = sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()  # Wait until recording is finished

            # Save recording as WAV file
            wav_filename = "recorded_audio.wav"
            with wave.open(wav_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 2 bytes per sample for 16-bit audio
                wf.setframerate(16000)
                wf.writeframes((recording * 32767).astype(np.int16).tobytes())

            return wav_filename
        except Exception as e:
            st.error(f"Audio recording error: {e}")
            return None

    @st.cache_data
    def transcribe_audio(_self, wav_filename):
        """Transcribe recorded audio file to text using Google Speech Recognition."""
        if not wav_filename:
            return ""

        try:
            with sr.AudioFile(wav_filename) as source:
                audio = _self.recognizer.record(source)
                return _self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            st.error(f"Could not request results from speech recognition service: {e}")
            return ""
        except Exception as e:
            st.error(f"Transcription error: {e}")
            return ""

    def text_to_speech(self, text):
        """Convert text to speech using pyttsx3 in a separate thread."""
        try:
            def speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()

            # Run the TTS engine in a separate thread to avoid UI blocking
            tts_thread = Thread(target=speak, daemon=True)
            tts_thread.start()
        except Exception as e:
            st.error(f"Speech synthesis error: {e}")
            
    def run_voice_assistant(self):
        """Streamlit interface for the voice assistant."""
        st.title("🎤 Real-Time Voice Assistant")
        st.markdown("### 💬 Speak to receive immediate responses")

        # Text input fallback
        user_message = st.text_input("Or type your message:")

        if st.button("Talk Tuah Therapist") or user_message:
            if user_message:
                # Use text input if provided
                st.markdown(f"You: {user_message}")
                response = self.generate_response(user_message)
                st.markdown(f"Assistant: {response}")
                self.text_to_speech(response)
            else:
                # Record audio
                audio_file = self.record_audio(duration=10)

                if audio_file:
                    # Transcribe the recorded audio
                    user_message = self.transcribe_audio(audio_file)

                    if user_message:
                        st.markdown(f"You: {user_message}")

                        # Generate and play response
                        response = self.generate_response(user_message)
                        st.markdown(f"Assistant: {response}")

                        # Attempt text-to-speech
                        self.text_to_speech(response)
                    else:
                        st.warning("No speech detected. Please try again.")


def init_styles():
    st.set_page_config(page_title="Talk Tuah Therapist", page_icon="🧠", layout="centered", initial_sidebar_state="collapsed")
    page_bg_style = """<style> .stButton button { background-color: #236860; color: white; padding: 15px 30px; border-radius: 25px; width: 100%; } .stTab { background-color: #f0f2f6; padding: 20px; border-radius: 10px; } .css-1d391kg { padding: 1rem; } </style>"""
    st.markdown(page_bg_style, unsafe_allow_html=True)

def main():
    configure()
    init_styles()


    # Create columns to put image and title on the same line
    col1, col2 = st.columns([1.5, 10])  # Adjust column proportions as needed

    with col1:
        st.image('logo-no-bg.png', width=100)  # Smaller width to fit inline

    with col2:
        st.title("Talk Tuah Therapist")
        st.markdown("Your Safe Space for Healing: Chat, Journal, Grow.")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "Chatbot", "Breathing Center", "Therapeutic Activities",
        "Sleep Tracker", "Mood Tracker", "Journal Center", 
        "BrainRot Memes", "Stress Buster", "Game Center"
    ])

    with tab1:
        assistant = VoiceAssistant()
        assistant.run_voice_assistant()
    with tab2:
        breathing_center_page()
    with tab3:
        therapeutic_activities_page()
    with tab4:
        sleep_tracker_page()
    with tab5:  
        mood_tracker_page()
    with tab6:
        journal_page()
    with tab7:
        brainrot_corner_page()
    with tab8:
        stress_burster()
    with tab9:
        game_center_page()


    # Add Resources section in sidebar
    with st.sidebar:
        st.title("Additional Resources")
        if st.button("View Mental Health Resources"):
            resources_page()

    st.markdown("""
Created with ❤ for mental health awareness
By:Akriti Kh,Bhoomika K S,Chidananda S,Rohith BN

For support, email: talktuahtherapist03@gmail.com  
For Queries, dm on <a href="https://www.instagram.com/talktuahtherapist">TalkTuahTherapist</a>
""", unsafe_allow_html=True)

        






def process_message(message_text):
    response = generate_response(message_text)
    
    if response:
        st.session_state.messages.append({"role": "user", "content": message_text})
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        audio_file = speak(response)
        if audio_file:
            st.audio(audio_file)





def game_center_page():
    tab1, tab2 = st.tabs(["Memory Matcher", "Rock Paper Scissors"])

    with tab1:
        st.title("🧠 Memory Matcher")
        
        # Game setup
        if 'game_state' not in st.session_state:
            # Generate 12 unique emoji pairs
            emojis = ['🍎', '🍌', '🍇', '🍊', '🍉', '🍓', 
                      '🚗', '🚀', '🎈', '🏀', '🐶', '🐱']
            board = emojis * 2  # Create pairs
            random.shuffle(board)  # Shuffle the board
            
            st.session_state.game_state = {
                'board': board,
                'flipped': [],
                'matched': [],
                'attempts': 0,
                'game_over': False
            }
        
        game = st.session_state.game_state
        
        # Game grid with 12 buttons
        cols = st.columns(4)  # Create 4 columns for layout
        for i in range(12):  # Loop through all 12 cards
            with cols[i % 4]:  # Distribute cards across columns
                if i not in game['matched']:
                    if i in game['flipped']:
                        # Show the emoji if the card is flipped
                        st.button(game['board'][i], disabled=True, key=f"flipped_{i}")
                    else:
                        # Show a button to flip the card
                        if st.button(f"Card {i+1}", key=f"card_{i}"):
                            game['flipped'].append(i)
                            
                            # Match logic
                            if len(game['flipped']) == 2:
                                game['attempts'] += 1
                                first, second = game['flipped']
                                if game['board'][first] == game['board'][second]:
                                    game['matched'].extend(game['flipped'])
                                else:
                                    # Reset flipped after a short delay if no match
                                    time.sleep(1)
                                
                                # Clear flipped cards after processing
                                game['flipped'] = []
                else:
                    # Show the matched emoji
                    st.button(game['board'][i], disabled=True, key=f"matched_{i}")
        
        # Game status
        st.write(f"Attempts: {game['attempts']}")
        
        # Win condition
        if len(game['matched']) == 12:  # All pairs found (12 emojis)
            st.balloons()
            st.success("Congratulations! You found all pairs! 🎉")
            game['game_over'] = True
        
        # Reset game button (only visible if the game is over)
        if game.get('game_over'):
            if st.button("New Game", key="new_game"):
                del st.session_state.game_state

    with tab2:
        st.title("✊ Rock Paper Scissors Showdown!")

        # Custom styling for hand animations (optional)
        st.markdown("""
        <style>
        .hand-container {
            display: flex;
            justify-content: space-between;
            font-size: 100px;
            margin: 20px 0;
            transition: transform 0.3s ease;
        }
        .hand-move {
            animation: shake 0.5s;
        }
        @keyframes shake {
            0% { transform: rotate(0deg); }
            25% { transform: rotate(15deg); }
            50% { transform: rotate(-15deg); }
            75% { transform: rotate(15deg); }
            100% { transform: rotate(0deg); }
        }
        </style>
        """, unsafe_allow_html=True)

        # Game choices with emojis
        choices = ['Rock ✊', 'Paper ✋', 'Scissors ✌️']

        # Player's choice
        player_choice = st.radio("Make your choice", choices)

        if st.button("Play"):
            # Computer's random choice
            computer_choice = random.choice(choices)

            # Animated loading
            with st.spinner('Battling it out...'):
                time.sleep(1)  # Dramatic pause

            # Create two columns for choice reveal
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Your Choice")
                st.markdown(f"## {player_choice}")

            with col2:
                st.write("### Computer's Choice")
                st.markdown(f"## {computer_choice}")

            # Determine winner and show result with animations
            if player_choice == computer_choice:
                st.balloons()
                st.info("### It's a tie! 🤝")
            elif (
                (player_choice == 'Rock ✊' and computer_choice == 'Scissors ✌️') or
                (player_choice == 'Paper ✋' and computer_choice == 'Rock ✊') or
                (player_choice == 'Scissors ✌️' and computer_choice == 'Paper ✋')
            ):
                st.snow()
                st.success("### You win! 🎉🏆")
            else:
                st.error("### Computer wins! That's always OK, TRY AGAIN! 😢🤖")

def breathing_center_page():
    st.header("🫁 Breathing Center")
    
    # Enhanced Custom CSS for better UI
    st.markdown("""
        <style>
        @keyframes breathe {
            0% { transform: scale(1); opacity: 0.3; }
            50% { transform: scale(1.5); opacity: 0.8; }
            100% { transform: scale(1); opacity: 0.3; }
        }
        .breathing-circle {
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, #236860, #2E7D32);
            border-radius: 50%;
            margin: 40px auto;
            animation: breathe 8s infinite ease-in-out;
            box-shadow: 0 0 30px rgba(46, 125, 50, 0.3);
        }
        .exercise-card {
            background: linear-gradient(to right bottom, #ffffff, #f8f9fa);
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            color: #1a1a1a;
            border: 1px solid rgba(46, 125, 50, 0.1);
        }
        .timer-text {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            color: #2E7D32;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        div[data-testid="stSelectbox"] {
            width: 100%;
        }
        .stButton > button {
            width: 100%;
            padding: 0.5rem 1rem;
            font-size: 1.1rem;
            font-weight: 500;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Container for better spacing
    container = st.container()
    
    with container:
        # Display breathing animation
        st.markdown('<div class="breathing-circle"></div>', unsafe_allow_html=True)
        
        # Create a wider layout
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            breathing_exercise = st.selectbox(
                "Select a breathing exercise:",
                ["Box Breathing", "4-7-8 Breathing", "Deep Breathing"],
                key="breathing_select"
            )
            
            # Enhanced exercise descriptions
            descriptions = {
                "Box Breathing": """🔲 Box breathing is a powerful stress-relief technique used by Navy SEALs. 
                Perfect for maintaining calm and focus under pressure.""",
                "4-7-8 Breathing": """🌙 The 4-7-8 breathing technique helps reduce anxiety and aids better sleep. 
                Practiced twice daily, it becomes more effective over time.""",
                "Deep Breathing": """🌊 Deep breathing is a simple yet effective way to reduce stress and increase mindfulness. 
                It helps activate your body's natural relaxation response."""
            }
            
            st.markdown(
                f'<div class="exercise-card">{descriptions[breathing_exercise]}</div>', 
                unsafe_allow_html=True
            )
            
            # Controls section
            controls_col1, controls_col2 = st.columns([2, 2])
            with controls_col1:
                start_button = st.button("Start Exercise 🎯", key="start_breathing", use_container_width=True)
            with controls_col2:
                play_music = st.checkbox("🎵 Play Meditation Music", key="play_music")
                
            if play_music:
                audio_file = open('assets/audio/meditation.mp3', 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
            
            if start_button:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                if breathing_exercise == "Box Breathing":
                    for cycle in range(4):
                        for phase, duration in [("Inhale", 4), ("Hold", 4), ("Exhale", 4), ("Hold", 4)]:
                            status_text.markdown(
                                f'<p class="timer-text">{phase}</p>', unsafe_allow_html=True)
                            for i in range(duration):
                                progress_bar.progress((i + 1) / duration)
                                time.sleep(1)
                            progress_bar.progress(0)
                            
                elif breathing_exercise == "4-7-8 Breathing":
                    for cycle in range(4):
                        for phase, duration in [("Inhale", 4), ("Hold", 7), ("Exhale", 8)]:
                            status_text.markdown(
                                f'<p class="timer-text">{phase}</p>', unsafe_allow_html=True)
                            for i in range(duration):
                                progress_bar.progress((i + 1) / duration)
                                time.sleep(1)
                            progress_bar.progress(0)
                            
                elif breathing_exercise == "Deep Breathing":
                    for cycle in range(4):
                        for phase, duration in [("Inhale Deeply", 4), ("Hold", 2), ("Exhale Slowly", 4), ("Rest", 2)]:
                            status_text.markdown(
                                f'<p class="timer-text">{phase}</p>', unsafe_allow_html=True)
                            for i in range(duration):
                                progress_bar.progress((i + 1) / duration)
                                time.sleep(1)
                            progress_bar.progress(0)
                            
                st.success("✨ Exercise completed! Take a moment to notice how you feel.")



def journal_page():
    st.title("📝 Personal Journal")
    
    # Initialize the journal entries list in session state if not already done
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    
    # Create a main container for better layout
    with st.container():
        # Create columns for better spacing
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Input for the journal entry with placeholder
            journal_entry = st.text_area(
                "Write your journal entry here:", 
                height=200, 
                placeholder="What's on your mind today?"
            )
            
            # Dynamic character count with color coding
            char_count = len(journal_entry)
            if char_count > 0:
                color = "green" if char_count <= 500 else "red"
                st.markdown(f"<p style='color:{color}'>Character Count: {char_count}</p>", 
                            unsafe_allow_html=True)
        
        with col2:
            # Entry submission and management
            st.write("### Journal Actions")
            
            # Submit entry button
            if st.button("💾 Save Entry", use_container_width=True):
                if journal_entry.strip():
                    # Get the current time and format it
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # Append the entry and timestamp to the session state
                    st.session_state.journal_entries.append((current_time, journal_entry))
                    st.success("Entry saved successfully!")
                     # Use st.rerun() instead of st.experimental_rerun()
                else:
                    st.error("Please write something before submitting!")
            
            # Clear entries with enhanced confirmation
            if st.button("🗑️ Clear All Entries", use_container_width=True):
                 if st.session_state.journal_entries:
                     if st.checkbox("Are you sure you want to clear all entries?"):
            # Directly clear the list of journal entries
                            st.session_state.journal_entries = []
                            st.success("All entries have been cleared!")
                            st.rerun()
                 else:
                     st.warning("No entries to clear.")

           
    
    # Search functionality with container
    with st.container():
        st.write("### Search Entries")
        search_term = st.text_input("Search your journal entries:")
        
        # Display journal entries with search filtering
        if st.session_state.journal_entries:
            filtered_entries = [
                entry for entry in st.session_state.journal_entries 
                if search_term.lower() in entry[1].lower()
            ]
            
            if filtered_entries:
                st.write("### Your Journal Entries")
                for time_sent, message in reversed(filtered_entries):
                    with st.expander(f"Entry from {time_sent}"):
                        st.write(message)
            else:
                st.info("No entries match your search term.")
        else:
            st.info("No journal entries yet. Start writing your first entry!")

def stress_burster():
    st.title("🧘 Stress Burster")
    
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    
    .spline-container {
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        overflow: hidden;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Introduction text
    st.markdown("""
    ### Take a Moment to Unwind 
    Interact with our BlueBall and let your stress melt away.
    """)
    
    # Spline Design Container
    st.markdown("""
    <div class="spline-container">
    <iframe 
        src='https://my.spline.design/aitherapist-e7816283ccca0cc7f2e74c543a304ec1/' 
        frameborder='0' 
        width='100%' 
        height='500px'>
    </iframe>
    </div>
    """, unsafe_allow_html=True)
    
    # Stress Relief Tips
    st.subheader("Quick Stress Relief Tips")
    tips = [
        "Take deep, slow breaths",
        "Practice mindfulness",
        "Stretch or do light exercise",
        "Listen to calming music"
    ]
    
    for tip in tips:
        st.markdown(f"• {tip}")



def mood_tracker_page():
    st.title("📊 Mood Tracker")
    
    # Initialize mood history in session state
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []
    
    # Mood input section
    st.subheader("How are you feeling today?")
    
    # Create two columns for mood input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mood_scale = st.slider("Rate your mood (1-10):", 1, 10, 5)
        mood_notes = st.text_area("Any notes about your mood?", placeholder="What's affecting your mood today?")
    
    with col2:
        mood_emojis = {
            1: "😢", 2: "😔", 3: "😕", 4: "😐",
            5: "😊", 6: "😄", 7: "😃", 8: "😁",
            9: "🤗", 10: "🥳"
        }
        st.markdown(f"### {mood_emojis[mood_scale]}")
        if st.button("Save Mood"):
            current_time = datetime.now()
            st.session_state.mood_history.append({
                'date': current_time,
                'mood': mood_scale,
                'notes': mood_notes
            })
            st.success("Mood recorded!")
    
    # Display mood history graph
    if st.session_state.mood_history:
        st.subheader("Your Mood History")
        
        # Convert mood history to DataFrame
        df = pd.DataFrame(st.session_state.mood_history)
        
        # Create line chart using plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['mood'],
            mode='lines+markers',
            name='Mood',
            line=dict(color='#236860'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Mood Over Time',
            xaxis_title='Date',
            yaxis_title='Mood Level',
            yaxis_range=[0, 11],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display mood entries
        st.subheader("Recent Entries")
        for entry in reversed(st.session_state.mood_history[-5:]):
            with st.expander(f"Entry from {entry['date'].strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"Mood: {entry['mood']}/10 {mood_emojis[entry['mood']]}")
                st.write(f"Notes: {entry['notes']}")

def gratitude_journal_page():
    st.title("🙏 Gratitude Journal")
    
    # Initialize gratitude entries in session state
    if 'gratitude_entries' not in st.session_state:
        st.session_state.gratitude_entries = []
    
    st.markdown("""
    ### Daily Gratitude Practice
    Taking time to appreciate the good things in life can improve mental well-being.
    """)
    
    # Create gratitude entry
    gratitude_text = st.text_area(
        "What are you grateful for today?",
        placeholder="List 3 things you're thankful for..."
    )
    
    if st.button("Save Gratitude Entry"):
        if gratitude_text.strip():
            current_time = datetime.now()
            st.session_state.gratitude_entries.append({
                'date': current_time,
                'entry': gratitude_text
            })
            st.success("Gratitude entry saved! 🌟")
    
    # Display gratitude history
    if st.session_state.gratitude_entries:
        st.subheader("Your Gratitude Journey")
        for entry in reversed(st.session_state.gratitude_entries):
            with st.expander(f"Entry from {entry['date'].strftime('%Y-%m-%d %H:%M')}"):
                st.write(entry['entry'])

def sleep_tracker_page():
    st.title("😴 Sleep Tracker")
    
    # Initialize sleep data in session state
    if 'sleep_data' not in st.session_state:
        st.session_state.sleep_data = []
    
    # Sleep entry form
    st.subheader("Log Your Sleep")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sleep_date = st.date_input("Date:")
        sleep_duration = st.number_input("Hours of sleep:", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
    
    with col2:
        sleep_quality = st.select_slider(
            "Sleep quality:",
            options=["Poor", "Fair", "Good", "Very Good", "Excellent"],
            value="Good"
        )
        
        factors = st.multiselect(
            "Factors affecting sleep:",
            ["Stress", "Exercise", "Caffeine", "Screen Time", "Noise", "Temperature"]
        )
    
    if st.button("Save Sleep Log"):
        st.session_state.sleep_data.append({
            'date': sleep_date,
            'duration': sleep_duration,
            'quality': sleep_quality,
            'factors': factors
        })
        st.success("Sleep log saved!")
    
    # Display sleep statistics and graphs
    if st.session_state.sleep_data:
        st.subheader("Sleep Statistics")
        
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.sleep_data)
        
        # Create sleep duration chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['duration'],
            name='Sleep Duration',
            marker_color='#236860'
        ))
        
        fig.update_layout(
            title='Sleep Duration Over Time',
            xaxis_title='Date',
            yaxis_title='Hours of Sleep',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display average sleep statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Sleep Duration", f"{df['duration'].mean():.1f} hours")
        with col2:
            st.metric("Most Common Quality", df['quality'].mode()[0])

def resources_page():
    st.title("🆘 Mental Health Resources")
    
    # Emergency Contacts
    st.header("Emergency Contacts")
    
    emergency_contacts = {
        "National Crisis Hotline": "1-800-273-8255",
        "Crisis Text Line": "Text HOME to 741741",
        "Emergency Services": "911"
    }
    
    for service, contact in emergency_contacts.items():
        st.markdown(f"*{service}*: {contact}")
    
    # Mental Health Resources
    st.header("Self-Help Resources")
    
    with st.expander("Meditation Apps"):
        st.markdown("""
        - Headspace
        - Calm
        - Insight Timer
        - Simple Habit
        """)
    
    with st.expander("Educational Resources"):
        st.markdown("""
        - National Institute of Mental Health
        - Mental Health America
        - Psychology Today
        - Mind.org
        """)
    
    with st.expander("Support Groups"):
        st.markdown("""
        - NAMI Support Groups
        - Depression and Bipolar Support Alliance
        - Anxiety and Depression Association of America
        """)
    
    # Mental Health Tips
    st.header("Quick Mental Health Tips")
    
    tips = [
        "Practice deep breathing exercises",
        "Maintain a regular sleep schedule",
        "Exercise regularly",
        "Stay connected with loved ones",
        "Practice mindfulness",
        "Set realistic goals",
        "Take breaks when needed"
    ]
    
    for tip in tips:
        st.markdown(f"• {tip}")

def brainrot_corner_page():
    st.header("🎮 Brainrot Corner")

    if 'meme_counter' not in st.session_state:
        st.session_state.meme_counter = 0

    def fetch_random_meme():
        try:
            # Fetch meme from a working API
            response = requests.get("https://meme-api.com/gimme", timeout=10)  # Use a valid API
            response.raise_for_status()
            meme_data = response.json()
            # Check the API response structure
            image_url = meme_data.get('url', "https://via.placeholder.com/800x600")
            meme_text = meme_data.get('title', "No caption available.")
            return image_url, meme_text
        except requests.exceptions.RequestException as e:
            # Handle API errors gracefully
            st.error(f"Error fetching meme: {e}")
            return "https://via.placeholder.com/800x600", "Error fetching meme! Try again."

    if st.button("Generate New Meme"):
        st.session_state.meme_counter += 1
        image_url, meme_text = fetch_random_meme()

        # Display the fetched meme
        st.markdown(f"""
            <div style="text-align: center; background-color: #1a1a1a; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h2 style="color: white; font-size: 24px; margin-bottom: 20px;">{meme_text}</h2>
                <img src="{image_url}" style="max-width: 100%; border-radius: 8px;" alt="Random Meme">
                <p style="color: #888; margin-top: 15px;">Meme #{st.session_state.meme_counter}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.meme_counter % 5 == 0:
            st.balloons()
            st.markdown("""
                <div style="text-align: center; color: #236860; font-size: 20px; margin: 20px 0;">
                    🎉 Milestone reached! Keep the memes flowing! 🎉
                </div>
            """, unsafe_allow_html=True)

    # Footer with meme counter
    st.markdown(f"""
        <div style="text-align: center; margin-top: 20px; color: #888;">
            Memes Generated: {st.session_state.meme_counter} 🎭
            <br>Keep clicking for infinite entertainment!
        </div>
    """, unsafe_allow_html=True)


def therapeutic_activities_page():


    # Get the absolute path to the assets directory
    assets_dir = Path(__file__).parent / "assets"
    audio_dir = assets_dir / "audio"

    st.title("🎨 Therapeutic Activities")
    
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .activity-card {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .activity-card:hover {
        transform: translateY(-5px);
    }
    .canvas-container {
        background: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
    }
    .visualization-text {
        font-size: 1.2em;
        line-height: 1.6;
        padding: 20px;
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Activities Selection
    activity = st.selectbox(
        "Choose an Activity:",
        ["Art Therapy", "Sound Therapy",]
    )

    if activity == "Art Therapy":
        st.subheader("🎨 Express Yourself Through Art")
        
        # Initialize session state for art therapy
        if 'drawing_mode' not in st.session_state:
            st.session_state.drawing_mode = "freedraw"
        if 'stroke_width' not in st.session_state:
            st.session_state.stroke_width = 2
        if 'stroke_color' not in st.session_state:
            st.session_state.stroke_color = "#000000"
        
        # Art tools
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.session_state.drawing_mode = st.selectbox(
                "Drawing Tool:",
                ("freedraw", "line", "rect", "circle")
            )
        with col2:
            st.session_state.stroke_width = st.slider("Brush Size:", 1, 25, 2)
        with col3:
            st.session_state.stroke_color = st.color_picker("Color:", "#000000")
        
        # Canvas for drawing
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=st.session_state.stroke_width,
            stroke_color=st.session_state.stroke_color,
            background_color="#FFFFFF",
            background_image=None,
            update_streamlit=True,
            height=400,
            drawing_mode=st.session_state.drawing_mode,
            key="canvas",
        )

    
    elif activity == "Sound Therapy":
        st.subheader("🎵 Therapeutic Sounds")
        
        # Sound options with file paths
        sounds = {
            "Ocean Waves": audio_dir / "ocean.mp3",
            "Forest Birds": audio_dir / "forest.mp3",
            "Rainfall": audio_dir / "rain.mp3"
        }
        
        col1, col2 = st.columns(2)
        with col1:
            selected_sound = st.selectbox("Choose a sound:", list(sounds.keys()))
            
        with col2:
            st.markdown("### Sound Settings")
            volume = st.slider("Volume:", 0.0, 1.0, 0.5)
            
        if st.button("Play Sound"):
            try:
                with open(sounds[selected_sound], "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3")
            except FileNotFoundError:
                st.error(f"Audio file for {selected_sound} not found. Please ensure it exists in the assets directory.")

    









if __name__=="__main__":
    main()
