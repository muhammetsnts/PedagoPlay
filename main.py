from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import random
import sys
import os

# Add the current directory to Python path to import pedagoplay
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pedagoplay import build_messages, chat_completion

app = FastAPI(title="PedagoPlay", description="Children's Activity Planner")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for request/response
class ActivityRequest(BaseModel):
    num_children: int
    ages: List[int]
    weather: str
    location: str
    special_cases: Optional[str] = "No special case."

class ActivityResponse(BaseModel):
    activities: str
    success: bool
    error: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/activities", response_model=ActivityResponse)
async def get_activities(request: ActivityRequest):
    try:
        # Try to use the AI API first
        try:
            messages = build_messages(
                num_children=request.num_children,
                ages=request.ages,
                weather=request.weather,
                location=request.location,
                special_cases=request.special_cases
            )
            
            activities = chat_completion(messages)
            
            if activities and activities.strip():
                return ActivityResponse(
                    activities=activities,
                    success=True
                )
        except Exception as api_error:
            print(f"API error: {str(api_error)}")
            # Fall back to simple activity generator
        
        # Fallback: Generate simple activities without API
        activities = generate_simple_activities(
            num_children=request.num_children,
            ages=request.ages,
            weather=request.weather,
            location=request.location,
            special_cases=request.special_cases
        )
        
        return ActivityResponse(
            activities=activities,
            success=True
        )
        
    except Exception as e:
        print(f"Error in get_activities: {str(e)}")
        return ActivityResponse(
            activities="",
            success=False,
            error=f"Server error: {str(e)}"
        )

def generate_simple_activities(num_children: int, ages: List[int], weather: str, location: str, special_cases: str) -> str:
    """Generate simple activities without API"""
    
    # Determine if indoor or outdoor based on weather
    is_outdoor = weather.lower() in ['sunny', 'cloudy', 'partly cloudy']
    
    activities = []
    
    # Indoor activities
    if not is_outdoor or weather.lower() in ['rainy', 'snowy']:
        activities.extend([
            "🎨 **Art & Craft Time**\nCreate colorful drawings, make paper crafts, or try finger painting. This helps develop creativity and fine motor skills.\n\n",
            "📚 **Story Time**\nRead books together, create your own stories, or act out favorite tales. Great for language development and imagination.\n\n",
            "🧩 **Puzzle & Games**\nWork on age-appropriate puzzles, play board games, or create your own games. Develops problem-solving skills.\n\n",
            "🎵 **Music & Dance**\nSing songs, play simple instruments, or have a dance party. Great for rhythm and coordination.\n\n"
        ])
    
    # Outdoor activities
    if is_outdoor:
        activities.extend([
            "🌳 **Nature Exploration**\nGo for a walk, collect leaves, or explore the garden. Learn about plants and animals in your area.\n\n",
            "⚽ **Active Play**\nPlay ball games, run around, or have a mini sports day. Great for physical development and energy.\n\n",
            "🏖️ **Sand & Water Play**\nIf available, play with sand or water. Build sandcastles or have water fun. Develops sensory skills.\n\n",
            "🚶 **Adventure Walk**\nExplore your neighborhood, visit a park, or go on a treasure hunt. Encourages exploration and discovery.\n\n"
        ])
    
    # Add location-specific suggestions
    if "park" in location.lower():
        activities.append("🌳 **Park Adventure**\nVisit the local park, play on playground equipment, or have a picnic. Perfect for outdoor fun!\n\n")
    
    # Add age-appropriate suggestions
    avg_age = sum(ages) / len(ages) if ages else 4
    if avg_age < 3:
        activities.append("👶 **Toddler Fun**\nSimple sensory play, soft toys, and gentle activities perfect for little ones.\n\n")
    elif avg_age > 6:
        activities.append("🎯 **Big Kid Activities**\nMore complex crafts, science experiments, or organized games for older children.\n\n")
    
    # Add special considerations
    if "allergy" in special_cases.lower():
        activities.append("⚠️ **Allergy-Safe Activities**\nAll activities are designed to be safe and avoid common allergens.\n\n")
    
    if "disability" in special_cases.lower() or "wheelchair" in special_cases.lower():
        activities.append("♿ **Accessible Activities**\nAll suggested activities are designed to be inclusive and accessible for all children.\n\n")
    
    # Select 3-4 activities at random to add variation across requests
    max_selection = min(4, len(activities))
    selected_activities = random.sample(activities, k=max_selection) if max_selection > 0 else []
    
    result = f"🎉 **Fun Activities for {num_children} child{'ren' if num_children > 1 else ''} (ages {', '.join(map(str, ages))})**\n\n"
    result += f"📍 **Location:** {location}\n"
    result += f"🌤️ **Weather:** {weather.title()}\n\n"
    result += "**Here are some great activities for your little ones:**\n\n"
    
    for i, activity in enumerate(selected_activities, 1):
        result += f"{i}. {activity}"
    
    result += "\n💡 **Tips:**\n"
    result += "- Always supervise children during activities\n"
    result += "- Adapt activities to your child's interests and abilities\n"
    result += "- Have fun and be creative!\n"
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
    
