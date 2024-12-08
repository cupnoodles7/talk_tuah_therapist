# Talk Tuah Therapist 🧠💭

## 🌟 Overview

Talk Tuah Therapist is a comprehensive mental health support application that combines AI-powered chat therapy with interactive wellness tools. It provides a safe, accessible space for users to manage their mental health journey through various therapeutic features.

### Hosted on Render
-[Visit the Website](https://talk-tuah-therapist-1o0g.onrender.com/)
- The website is hosted on Render.  
- Environment variables are securely managed via Render's dashboard.  
- Dependencies are installed automatically using `requirements.txt`.  
- The live website is deployed and accessible at the provided URL..

## ✨ Features

- **AI Therapist Chat** 🤖
  - Engage in therapeutic conversations with an AI-powered chatbot
  - Voice input support for natural interaction
  - Text-to-speech capability for responses

- **Wellness Tools** 🎯
  - **Breathing Center** 🫁: Guided breathing exercises
  - **Therapeutic Activities** 🎨: Art therapy and sound therapy
  - **Sleep Tracker** 😴: Monitor sleep patterns and quality
  - **Mood Tracker** 📊: Track and visualize emotional states
  - **Journal Center** 📝: Private space for personal reflection
  - **Stress Buster** 🧘‍♀️: Interactive stress relief activities
  - **Game Center** 🎮: Mental wellness games

- **Additional Features** 🎁
  - **BrainRot Memes** 😄: Lighthearted entertainment
  - **Resources Hub** 🆘: Access to mental health resources

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/talk-tuah-therapist.git
cd talk-tuah-therapist
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# For Windows
venv\Scripts\activate
# For Unix/MacOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
CLARIFAI_PAT=your_clarifai_pat_here
```

## 🎮 Running the Application

1. **Start the Streamlit server**
```bash
streamlit run app.py
```

2. **Access the application**
Open your web browser and navigate to:
```
http://localhost:8501
```

## 📦 Dependencies

- streamlit
- speech_recognition
- clarifai-grpc
- gTTS
- streamlit-drawable-canvas
- plotly
- pandas
- numpy
- scipy
- requests

## 🔧 Configuration

The application uses several API keys and configurations:
- Clarifai API for AI chat functionality
- Gemini API for voice assistance
- Various audio files for sound therapy
- Custom UI components and styling

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Anthropic's Claude for AI capabilities
- Streamlit for the wonderful web framework
- All contributors and users of the application

## 📞 Support

For support, email: support@talktuah.com
For Queries, dm on TalkTuahTherapist

---

<p align="center">Made with ❤️ for mental health awareness</p>
