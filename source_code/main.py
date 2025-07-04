# Assignment: Assigment 2: Design Your Own AI Assistant (Prototype)
# Author: Cooper Nathan
# Date: July 3, 2025

from enum import Enum
from datetime import datetime
import re 


# Part 1: Data Type Design
# custom data type representing a user profile with validation

class UserProfile:    
    # Initialize with attributes and check for errors in the input data
    def __init__(self, name, age, preferences, isPremium):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non empty string")
        if not isinstance(age, int) or age <= 0:
            raise ValueError("Age must be a positive integer")
        if not isinstance(preferences, dict):
            raise TypeError("Preferences must be a dictionary")
        if not isinstance(isPremium, bool):
            raise TypeError("isPremium must be a boolean")
        
        self.name = name.strip()
        self.age = age
        self.preferences = preferences
        self.isPremium = isPremium
    
    # String representation for debugging and logging
    def __str__(self):
        return f"UserProfile(name='{self.name}', age={self.age}, premium={self.isPremium})"


class CommandType(Enum):
    # Enumeration for different types of assistant commands
    MUSIC = "MUSIC"
    FITNESS = "FITNESS"
    STUDY = "STUDY"
    GENERAL = "GENERAL"

# Request: input string, timestamp (datetime), command type (enumeration)
# Data type representing a user request with input validation.
class Request:
    def __init__(self, input_string, command_type, timestamp=None):
        # validate parameters
        if not isinstance(input_string, str) or not input_string.strip(): # cHECK if input string is not empty
            raise ValueError("Input string cannot be empty")
        if not isinstance(command_type, CommandType): 
            raise TypeError("command_type must be an instance of CommandType")
        
        self.input_string = input_string.strip()
        self.timestamp = timestamp if timestamp else datetime.now()
        self.command_type = command_type
    
    def __str__(self):
        return f"Request(input='{self.input_string}', type={self.command_type.value}, time={self.timestamp})"


# Response: message (string), confidence (float), actionPerformed (boolean)
class Response:
    def __init__(self, message, confidence, actionPerformed):
        # Validate parameters
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        if not isinstance(confidence, (int, float)):
            raise TypeError("Confidence must be a number")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if not isinstance(actionPerformed, bool):
            raise TypeError("actionPerformed must be a boolean")
        
        self.message = message
        self.confidence = float(confidence)
        self.actionPerformed = actionPerformed
    
    def __str__(self):
        return f"Response(message='{self.message}', confidence={self.confidence}, actionPerformed={self.actionPerformed})"


# Part 2: Core OOP Structure (35 pts)
# Base class AIAssistant with core behaviors: greetUser(), handleRequest(request), generateResponse()
class AIAssistant:
    def __init__(self, name):
        self.name = name
        self.interaction_count = 0
    
    def greetUser(self, user):
        # Greet a user with personalized message
        greeting = f"Hello {user.name}! I'm {self.name}, your trusty and faithful AI assistant."
        if user.isPremium: # Additional behavior for premium users
            greeting += " As a premium user, you have access to all features!"
        return Response(greeting, 1.0, False)
    
    def handleRequest(self, user, request):
        # Handle a user request. Base implementation provides default behavior
        # Default response is a clarification request, but subclasses should override this when keywords are detected
        self.interaction_count += 1
        return Response("I'm not sure how to help with that. Please be more specific.", 0.3, False)
    
    def generateResponse(self, message, confidence, actionPerformed):
        return Response(message, confidence, actionPerformed)
    

class MusicAssistant(AIAssistant):
    # Music focused assistant that recommends songs based on mood
    # Extends the base AIAssistant class, inheriting the greetUser and generateResponse methods and overriding the handleRequest method
    
    def __init__(self):
        super().__init__("MelodyBot")
        self.music_database = {
            "happy": ["Uptown Funk - Bruno Mars", "Can't Stop the Feeling - Justin Timberlake", "Feel Good Inc - Gorillaz"],
            "sad": ["Someone Like You - Adele", "Hurt - Johnny Cash", "Mad World - Gary Jules"],
            "energetic": ["Eye of the Tiger - Survivor", "Thunderstruck - AC/DC", "Pump It - Black Eyed Peas"],
            "relaxing": ["Weightless - Marconi Union", "Clair de Lune - Debussy", "Aqueous Transmission - Incubus"],
            "romantic": ["Perfect - Ed Sheeran", "All of Me - John Legend", "Make You Feel My Love - Bob Dylan"]
        }
    
    def handleRequest(self, user, request):
        # Override base method to handle music-specific requests
        self.interaction_count += 1
        
        if request.command_type == CommandType.MUSIC:
            return self.recommendPlaylist(user, request.input_string)
        else:
            return super().handleRequest(user, request)
    
    def recommendPlaylist(self, user, input_text):
        input_lower = input_text.lower()
        
        # Extract mood and preferences from the input text
        parser = CommandParser()
        extracted_prefs = parser.extractPreferences(input_text)
        
        # Use extracted mood or check for mood keywords directly
        mood = extracted_prefs.get("mood")
        if not mood:
            # Check for mood keywords in the input
            for mood_key in self.music_database.keys():
                if mood_key in input_lower:
                    mood = mood_key
                    break
        
        preferred_genre = extracted_prefs.get("genre") or user.preferences.get("genre", "all")
        
        if mood and mood in self.music_database:
            songs = self.music_database[mood]
            message = f"Based on your '{mood}' mood"
            if preferred_genre != "all":
                message += f" and preference for {preferred_genre}"
            message += f", here are some recommendations: {', '.join(songs[:2])}"
            if user.isPremium:
                message += f"\nPremium users get the full playlist: {', '.join(songs)}"
            return Response(message, 0.9, True)
        else:
            return Response(f"I can suggest music for these moods: happy, sad, energetic, relaxed, or romantic. What's your mood?", 0.6, False)

class FitnessAssistant(AIAssistant):
    # Suggests workouts based on goals.
    # Demonstrates inheritance from AIAssistant class with method overriding for handleRequest
   
    def __init__(self):
        super().__init__("FitBot")
        # Workout plans dictionary with structured data for different fitness levels and goals
        self.workout_plans = {
            "strength": {
                "beginner": "3 sets of: 10 push-ups, 15 squats, 30-second plank",
                "intermediate": "4 sets of: 15 push-ups, 20 squats, 1-minute plank, 10 lunges",
                "advanced": "5 sets of: 20 push-ups, 25 squats, 90-second plank, 15 lunges, 10 burpees"
            },
            "cardio": {
                "beginner": "20-minute brisk walk or 10-minute light jog",
                "intermediate": "30-minute jog or 20-minute cycling",
                "advanced": "45-minute run or 30-minute HIIT workout"
            },
            "flexibility": {
                "beginner": "15-minute basic stretching routine",
                "intermediate": "25-minute yoga flow",
                "advanced": "45-minute advanced yoga or pilates session"
            }
        }
    
    def handleRequest(self, user, request):
        # Override base method to handle fitness-specific requests
        self.interaction_count += 1
        
        if request.command_type == CommandType.FITNESS:
            return self.suggestWorkout(user, request.input_string)
        else:
            return super().handleRequest(user, request)
    
    def suggestWorkout(self, user, request_text):
        # Extract fitness level and goal from the request text
        parser = CommandParser()
        extracted_prefs = parser.extractPreferences(request_text)
        
        # Use extracted fitness level or fall back to user preferences
        fitness_level = extracted_prefs.get("fitness_level") or user.preferences.get("fitness_level", "beginner")
        
        request_lower = request_text.lower()
        
        # Check for workout type keywords
        for workout_type in self.workout_plans.keys():
            if workout_type in request_lower:
                workout = self.workout_plans[workout_type].get(fitness_level, self.workout_plans[workout_type]["beginner"])
                message = f"For your {workout_type} goal at {fitness_level} level: {workout}"
                if user.isPremium:
                    message += "\nPremium users get personalized meal plans too!"
                return Response(message, 0.95, True)
        
        return Response(f"I can help with: strength, cardio, or flexibility training. What would you like to focus on?", 0.7, False)


class StudyAssistant(AIAssistant):
    # Assistant that schedules study sessions and explains topics
    # Demonstrates inheritance from AIAssistant plus polymorphism by overriding handleRequest method
    def __init__(self):
        super().__init__("StudyMate")
        self.knowledge_base = {
            "oop": "Object-Oriented Programming (OOP) is a programming paradigm based on objects and classes. Key concepts include encapsulation, inheritance, and polymorphism.",
            "ai": "Artificial Intelligence (AI) is the simulation of human intelligence in machines. It includes machine learning, natural language processing, and computer vision.",
            "python": "Python is a high-level programming language known for its readability and versatility. It's widely used in AI, web development, and data science.",
            "data structures": "Data structures are ways of organizing and storing data efficiently. Common types include arrays, linked lists, stacks, queues, and trees.",
            "algorithms": "Algorithms are step-by-step procedures for solving problems. They're fundamental to computer science and programming."
        }
    
    def handleRequest(self, user, request):
        """Override base method to handle study-specific requests."""
        self.interaction_count += 1
        
        if request.command_type == CommandType.STUDY:
            return self.explainTopic(user, request.input_string)
        else:
            return super().handleRequest(user, request)
    
    def explainTopic(self, user, input_text):
        """Unique behavior: explain academic topics."""
        input_lower = input_text.lower()
        
        # Check if any topic keywords are in the input using regex because of spaces and certain topics being within words
        for topic in self.knowledge_base.keys():
            pattern = r'\b' + re.escape(topic) + r'\b'
            if re.search(pattern, input_lower):
                explanation = self.knowledge_base[topic]
                message = f"Here's an explanation of {topic}: {explanation}"
                if user.isPremium:
                    message += "\nPremium users get detailed examples and practice problems!"
                return Response(message, 0.9, True)
        
        # If no specific topic found, offer options
        available_topics = ", ".join(self.knowledge_base.keys())
        return Response(f"I can explain: {available_topics}. What would you like to learn about?", 0.6, False)

# Part 3: Dynamic Behavior & User Simulation (30 pts)
class AssistantManager:
    # Manages multiple assistants and routes requests based on command type

    def __init__(self):
        self.assistants = {
            CommandType.MUSIC: MusicAssistant(),
            CommandType.FITNESS: FitnessAssistant(),
            CommandType.STUDY: StudyAssistant(),
            CommandType.GENERAL: AIAssistant("GeneralBot")
        }
        self.user_greeted = {}  # Track which assistants have greeted which users
    
    # Calls the approproate assistant's handleRequest method based on identified command type
    def routeRequest(self, user, request):
        assistant = self.assistants.get(request.command_type, self.assistants[CommandType.GENERAL])
        
        # Check if this assistant has greeted this user before
        user_key = f"{user.name}_{request.command_type.value}"
        if user_key not in self.user_greeted:
            # First interaction with this assistant type - greet first
            greeting = assistant.greetUser(user)
            response = assistant.handleRequest(user, request)
            # Combine greeting and response
            combined_message = f"{greeting.message}\n\n{response.message}"
            self.user_greeted[user_key] = True
            return Response(combined_message, response.confidence, response.actionPerformed)
        else:
            # Normal interaction
            return assistant.handleRequest(user, request)
    
    # Greet the user with a specific assistant based on command type
    def greetUser(self, user, assistant_type):
        assistant = self.assistants.get(assistant_type, self.assistants[CommandType.GENERAL])
        return assistant.greetUser(user)

class CommandParser:
    def __init__(self):
        self.keywords = {
            CommandType.MUSIC: ["song", "music", "play", "playlist", "mood", "genre"],
            CommandType.FITNESS: ["workout", "exercise", "fitness", "gym", "strength", "cardio"],
            CommandType.STUDY: ["study", "learn", "explain", "topic", "homework", "schedule"]
        }
        
        # Add keyword-based preference detection
        self.preference_keywords = {
            "fitness_level": {
                "beginner": ["beginner", "new", "start", "easy", "basic"],
                "intermediate": ["intermediate", "moderate", "medium", "regular"],
                "advanced": ["advanced", "hard", "intense", "expert", "pro"]
            },
            "genre": {
                "rock": ["rock", "metal", "guitar"],
                "pop": ["pop", "mainstream", "chart"],
                "classical": ["classical", "orchestra", "symphony"],
                "jazz": ["jazz", "blues", "smooth"]
            },
            "mood": ["happy", "sad", "energetic", "relaxing", "romantic", "calm", "excited"]
        }
    
    def parseCommand(self, input_string):
        # Parse input string to determine command type
        input_lower = input_string.lower()
        
        for command_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in input_lower:
                    return command_type
        
        return CommandType.GENERAL
    
    def extractPreferences(self, input_string):
        # Extract preferences from user input based on keywords.
        preferences = {}
        input_lower = input_string.lower()
        
        # Extract fitness level by checking whether keywords from the fitness_level dictionary are present in the input.
        # If a keyword is found, the fitness level is set in the preferences dictionary 
        for level, keywords in self.preference_keywords["fitness_level"].items():
            for keyword in keywords:
                if keyword in input_lower:
                    preferences["fitness_level"] = level
                    break
        
        # Extract genre with the same method as fitness level
        for genre, keywords in self.preference_keywords["genre"].items():
            for keyword in keywords:
                if keyword in input_lower:
                    preferences["genre"] = genre
                    break
        
        # Extract mood
        for mood in self.preference_keywords["mood"]:
            if mood in input_lower:
                preferences["mood"] = mood
                break
        
        return preferences

def interactive_mode():
    # Interactive mode where user can enter their own requests
    print("=== Interactive AI Assistant ===")
    print("You can chat with our AI assistants!")
    print("Type 'quit' to exit, 'help' for commands\n")
    
    # Let user create their profile
    name = input("Enter your name: ")
    while True:
        try:
            age = int(input("Enter your age: "))
            break
        except ValueError:
            print("Please enter a valid age (number)")
    
    premium = input("Are you a premium user? (y/n): ").lower().startswith('y')
    
    # Create user profile
    user = UserProfile(name, age, {}, premium)
    
    # Create system components
    manager = AssistantManager()
    parser = CommandParser()
    
    # Greet user and show what they can ask
    print(f"\nWelcome {name}! {'Premium' if premium else 'Standard'} user account created.")
    print("You can ask for:")
    print("- Music recommendations (try: 'play happy music')")
    print("- Fitness workouts (try: 'I need a beginner strength workout')")
    print("- Study help (try: 'explain OOP concepts')")
    print("- General questions")
    print("Type 'help' for available commands or 'quit' to exit.")
    print()
    
    while True:
        user_input = input("You: ").strip() # To show that the user is typing
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'help':
            print("Available commands:")
            print("- Music: 'play [mood] music', 'recommend songs'")
            print("- Fitness: 'workout', 'exercise', '[level] [type] training'")
            print("- Study: 'explain [topic]', 'learn about [subject]'")
            print("- General: any other questions")
            print("- 'quit' to exit")
            continue
        elif not user_input:
            print("Please enter a command or 'quit' to exit")
            continue
        
        # Parse command and get response
        command_type = parser.parseCommand(user_input)
        request = Request(user_input, command_type)
        response = manager.routeRequest(user, request)
        
        # Display response
        print(f"Assistant: {response.message}")
        print(f"(Confidence: {response.confidence:.1f})")
        print()

def demo_mode():
    # Create users with minimal preferences
    user1 = UserProfile("Alice", 25, {}, True)
    user2 = UserProfile("Bob", 30, {"fitness_level": "advanced"}, False)
    
    # Create system components
    manager = AssistantManager()
    parser = CommandParser()
    
    test_commands = [
        "I want energetic music for my workout",
        "Play some relaxing music",
        "I need a beginner strength workout",
        "Give me an advanced cardio routine",
        "Explain OOP concepts",
        "What is python?",
        "Tell me about algorithms"
    ]
    
    print("=== AI Assistant System Demo ===\n")
    
    for command in test_commands:
        print(f"User command: '{command}'")
        
        # Parse command type
        command_type = parser.parseCommand(command)
        print(f"Detected type: {command_type.value}")
        
        # Create request
        request = Request(command, command_type)
        print(f"Request timestamp: {request.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # Route request and get response
        response = manager.routeRequest(user1, request)
        
        print(f"Response: {response.message}")
        print(f"Confidence: {response.confidence}")
        print(f"Action performed: {response.actionPerformed}")
        print("-" * 50)

def main():
    """Main function with mode selection."""
    print("AI Assistant Framework")
    print("======================")
    print("Choose an option:")
    print("1. Run demo with predefined commands")
    print("2. Interactive mode - enter your own requests")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            demo_mode()
            break
        elif choice == '2':
            interactive_mode()
            break
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()