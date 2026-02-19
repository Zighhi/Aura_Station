import random

class PromptAgent:
    """A base class for prompt generation agents."""
    def __init__(self):
        # Core descriptive keywords
        self.base_keywords = [
            "lofi chill beat", "ambient music", "atmospheric soundscape", "deep focus drone", 
            "relaxing meditation music", "soothing generative audio", "instrumental study music",
            "minimalist background texture", "unobtrusive environmental drone"
        ]
        self.mood_keywords = ["calm", "serene", "powerful", "gentle", "deep", "warm", "cool", "mysterious", "ethereal", "grounding", "steady", "minimal", "non-intrusive"]
        self.purpose_keywords = ["studying", "sleeping", "meditating", "concentrating", "relaxing", "deep work"]

        # Scientifically-informed keywords from research
        self.binaural_options = [
            " with a subtle 10Hz alpha wave binaural beat for relaxed focus",
            " with a faint 20Hz beta wave binaural beat for active concentration",
            ""  # Chance for no binaural beat
        ]
        self.noise_options = [
            " layered with a gentle pink noise for masking distractions",
            " underpinned by a soft brown noise for a deep, rumbling foundation",
            ""  # Chance for no noise
        ]
        
        # More complex structures
        self.structures = [
            "A {keyword} featuring {element_keyword} and a {mood_keyword} feeling{binaural_beat}{noise_color}.",
            "An atmospheric soundscape perfect for {purpose}, with prominent {element_keyword} sounds{noise_color}.",
            "Generative music with hints of {element_keyword}, a {mood_keyword} mood, 90 bpm, 4/4 time signature{binaural_beat}.",
            "{element_keyword} mixed with {keyword}{noise_color}. The track should be {mood_keyword} and suitable for {purpose}.",
            "Deep focus track for {purpose}. A foundation of {element_keyword}{noise_color}, with {mood_keyword} melodic elements{binaural_beat}."
        ]

    def generate_prompt(self):
        """Generates a sophisticated prompt by combining structures and keywords."""
        structure = random.choice(self.structures)
        
        # This base implementation uses generic placeholders.
        # Subclasses should provide more specific element keywords.
        element_keyword = "natural elements" 
        
        prompt = structure.format(
            keyword=random.choice(self.base_keywords),
            element_keyword=element_keyword,
            mood_keyword=random.choice(self.mood_keywords),
            purpose=random.choice(self.purpose_keywords),
            binaural_beat=random.choice(self.binaural_options),
            noise_color=random.choice(self.noise_options)
        )
        return prompt.replace("  ", " ").strip() # Clean up any extra spaces

class FirePromptAgent(PromptAgent):
    """Generates prompts for the 'Fire' theme."""
    def __init__(self):
        super().__init__()
        self.element_keywords = [
            "the warm crackle of a fireplace", "a steady, roaring bonfire", "the gentle flicker of a candle flame", 
            "hot embers glowing in the dark", "a distant, welcoming campfire under stars", 
            "the rhythmic sounds of a blacksmith's forge", "a warm, radiant glow"
        ]

    def generate_prompt(self):
        structure = random.choice(self.structures)
        prompt = structure.format(
            keyword=random.choice(self.base_keywords),
            element_keyword=random.choice(self.element_keywords),
            mood_keyword=random.choice(self.mood_keywords + ["fiery", "smoldering", "cozy"]),
            purpose=random.choice(self.purpose_keywords),
            binaural_beat=random.choice(self.binaural_options),
            noise_color=random.choice(self.noise_options)
        )
        return prompt.replace("  ", " ").strip()

class WaterPromptAgent(PromptAgent):
    """Generates prompts for the 'Water' theme."""
    def __init__(self):
        super().__init__()
        self.element_keywords = [
            "gentle rain tapping on a window pane", "powerful ocean waves crashing on a shore", "a calm, clear stream flowing over stones",
            "the deep, mysterious ambience of being underwater", "the serene surface of a quiet lake at dawn", 
            "a soft, bubbling spring in a forest", "the roar of a distant waterfall"
        ]

    def generate_prompt(self):
        structure = random.choice(self.structures)
        prompt = structure.format(
            keyword=random.choice(self.base_keywords),
            element_keyword=random.choice(self.element_keywords),
            mood_keyword=random.choice(self.mood_keywords + ["fluid", "flowing", "drip-drop", "refreshing"]),
            purpose=random.choice(self.purpose_keywords),
            binaural_beat=random.choice(self.binaural_options),
            noise_color=random.choice(self.noise_options)
        )
        return prompt.replace("  ", " ").strip()

class EarthPromptAgent(PromptAgent):
    """Generates prompts for the 'Earth' theme."""
    def __init__(self):
        super().__init__()
        self.element_keywords = [
            "a gentle wind blowing through a dense, ancient forest", "the resonant silence of a deep cave", "a low, rumbling earthquake",
            "the subtle sounds of the deep woods at night", "crisp footsteps on dry autumn leaves", 
            "deep, grounding earth tones and sub-bass frequencies"
        ]

    def generate_prompt(self):
        structure = random.choice(self.structures)
        prompt = structure.format(
            keyword=random.choice(self.base_keywords),
            element_keyword=random.choice(self.element_keywords),
            mood_keyword=random.choice(self.mood_keywords + ["grounded", "stable", "ancient", "rooted"]),
            purpose=random.choice(self.purpose_keywords),
            binaural_beat=random.choice(self.binaural_options),
            noise_color=random.choice(self.noise_options)
        )
        return prompt.replace("  ", " ").strip()

if __name__ == '__main__':
    # Example usage:
    fire_agent = FirePromptAgent()
    water_agent = WaterPromptAgent()
    earth_agent = EarthPromptAgent()

    print("--- Fire Prompts ---")
    for _ in range(2):
        print(f"- {fire_agent.generate_prompt()}\n")
        
    print("\n--- Water Prompts ---")
    for _ in range(2):
        print(f"- {water_agent.generate_prompt()}\n")

    print("\n--- Earth Prompts ---")
    for _ in range(2):
        print(f"- {earth_agent.generate_prompt()}\n")
