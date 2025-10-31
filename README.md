# 🎨 PedagoPlay Web Application

A children-friendly web application that suggests fun and educational activities for kids based on their age, weather, location, and special considerations.

## 🌟 Features

- **Children-friendly UI** with soft pastel colors and playful design
- **Smart Activity Suggestions** using AI to recommend age-appropriate activities
- **Weather-aware** recommendations for indoor and outdoor activities
- **Location-specific** suggestions based on your area
- **Special considerations** support for allergies, disabilities, and space limitations
- **Responsive design** that works on all devices

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Environment
Make sure you have a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

### 3. Run the Application
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

### 4. Open Your Browser
Visit `http://localhost:8000` to see your PedagoPlay application!

## 📁 Project Structure

```
PedagoPlay/
├── main.py              # FastAPI application
├── pedagoplay.py        # Core activity generation logic
├── requirements.txt     # Python dependencies
├── index.html           # Main web page template
├── static/
│   ├── style.css        # Beautiful pastel styling
│   └── script.js        # Interactive JavaScript
└── README.md            # This file
```

## 🎯 How to Use

1. **Enter the number of children** you're planning activities for
2. **Specify their ages** (separated by commas if multiple)
3. **Select the current weather** (sunny, rainy, snowy, etc.)
4. **Enter your location** for location-specific suggestions
5. **Add any special considerations** (allergies, disabilities, space limitations)
6. **Click "Find Activities!"** and get personalized recommendations!

## 🎨 Design Features

- **Soft pastel color palette** with gradients
- **Playful typography** using the Fredoka font
- **Smooth animations** and hover effects
- **Mobile-responsive** design
- **Accessibility-friendly** interface
- **Loading states** and error handling

## 🔧 API Endpoints

- `GET /` - Main web page
- `POST /api/activities` - Get activity suggestions

## 🛠️ Development

The application uses:
- **FastAPI** for the backend API
- **HTML/CSS/JavaScript** for the frontend
- **OpenRouter API** for AI-powered activity generation
- **Pydantic** for data validation

## 📝 Notes

- Make sure your OpenRouter API key is properly configured. You can get one from here: [OpenRouter API Key](https://openrouter.ai/docs/api-reference/authentication)
- The application is designed to be safe and appropriate for children
- All activity suggestions are filtered for child safety

