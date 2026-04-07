"""
Hercules AI Coaching Engine
Generates personalized training advice based on scientific principles and user data.
Data sources:
  - Symmetric Strength API: Real-time strength standards
  - ExRx.net: Exercise form cues and biomechanics
  - PubMed Central API: Peer-reviewed sports science research
  - Google Custom Search: Current training trends and research
  - Fallback: Hardcoded research-backed standards
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Optional
import requests
import logging
from functools import lru_cache
import threading
import json

logger = logging.getLogger(__name__)

# Simple in-memory cache for API responses (in production, use Redis)
_RESEARCH_CACHE = {}
_CACHE_LOCK = threading.Lock()
_FOOD_CACHE = {}


# Strength standards (lbs) - based on Symmetric Strength, ExRx data
# Format: {exercise: {bw_category: (untrained, novice, intermediate, advanced)}}
STRENGTH_STANDARDS = {
    "Bench Press": {"bw25": (65, 95, 185, 280), "bw50": (95, 155, 255, 365), 
                    "bw75": (115, 185, 315, 425), "bw100": (135, 215, 365, 500)},
    "Squat": {"bw25": (65, 135, 225, 350), "bw50": (155, 245, 405, 550),
              "bw75": (185, 315, 495, 675), "bw100": (225, 385, 585, 800)},
    "Deadlift": {"bw25": (95, 155, 275, 375), "bw50": (185, 315, 425, 585),
                 "bw75": (225, 405, 545, 725), "bw100": (275, 495, 675, 875)},
    "Overhead Press": {"bw25": (35, 65, 115, 165), "bw50": (65, 115, 185, 275),
                       "bw75": (85, 145, 225, 325), "bw100": (105, 175, 275, 385)},
}

# Volume recommendations (sets per muscle per week) based on research
VOLUME_RECOMMENDATIONS = {
    "Push": {"optimal_min": 12, "optimal_max": 20, "max_sustainable": 25},
    "Pull": {"optimal_min": 12, "optimal_max": 20, "max_sustainable": 25},
    "Legs": {"optimal_min": 12, "optimal_max": 20, "max_sustainable": 24},
}

# Exercise groupings by muscle group
EXERCISE_MUSCLE_GROUPS = {
    "Chest": ["Bench Press", "Incline Dumbbell Press", "Dips"],
    "Back": ["Barbell Row", "Pull Up", "Lat Pulldown", "Face Pull"],
    "Shoulders": ["Overhead Press", "Lateral Raise"],
    "Biceps": ["Bicep Curl"],
    "Triceps": ["Triceps Extension", "Dips"],
    "Quads": ["Squat", "Leg Press", "Lunge"],
    "Hamstrings": ["Deadlift", "Leg Press", "Lunge"],
    "Calves": ["Calf Raise"],
}

# Map exercises to muscle groups
EXERCISE_TO_MUSCLES = {}
for muscle, exercises in EXERCISE_MUSCLE_GROUPS.items():
    for ex in exercises:
        if ex not in EXERCISE_TO_MUSCLES:
            EXERCISE_TO_MUSCLES[ex] = []
        EXERCISE_TO_MUSCLES[ex].append(muscle)


class OnlineDataFetcher:
    """Fetch real-time data from online databases and research APIs with non-blocking fallback."""
    
    # Cache for 24 hours to avoid rate limiting
    CACHE_TTL = 86400

    @staticmethod
    def _safe_float(value: Any) -> float:
        if value in (None, ""):
            return 0.0
        if isinstance(value, str):
            value = value.replace(",", ".").strip()
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
    @staticmethod
    def _fetch_pubmed_async(query: str, max_results: int = 3) -> None:
        """Background thread: Fetch and cache PubMed research without blocking."""
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "pmc",
                "term": f"{query} AND (exercise OR training OR strength)",
                "rettype": "json",
                "retmax": max_results,
                "sort": "relevance"
            }
            
            # Increased timeout to 5 seconds for slower networks
            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()
            
            # NCBI returns JSON in a wrapper - extract the actual data
            try:
                data = response.json()
            except:
                # If JSON parsing fails, try parsing the text response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                # Parse XML: look for IdList -> Id elements
                id_list = root.find('.//IdList')
                if id_list is not None:
                    results = []
                    for id_elem in id_list.findall('Id'):
                        pmcid = id_elem.text
                        if pmcid:
                            results.append({
                                "source": "PubMed Central",
                                "pmcid": pmcid,
                                "url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/"
                            })
                    with _CACHE_LOCK:
                        _RESEARCH_CACHE[query] = results[:max_results]
                    logger.debug(f"PubMed fetch succeeded for '{query}': {len(results)} papers")
                return
            
            results = []
            if "esearchresult" in data and "idlist" in data["esearchresult"]:
                for pmcid in data["esearchresult"]["idlist"][:max_results]:
                    results.append({
                        "source": "PubMed Central",
                        "pmcid": pmcid,
                        "url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/"
                    })
            
            # Cache the result
            with _CACHE_LOCK:
                _RESEARCH_CACHE[query] = results
            
            logger.debug(f"PubMed fetch succeeded for '{query}': {len(results)} papers")
        except requests.Timeout:
            logger.debug(f"PubMed fetch timeout for '{query}'")
        except Exception as e:
            logger.debug(f"PubMed fetch error for '{query}': {type(e).__name__}: {str(e)[:50]}")
    
    @staticmethod
    def fetch_pubmed_research(query: str, max_results: int = 3, use_async: bool = True) -> List[Dict]:
        """
        Fetch peer-reviewed research from PubMed Central.
        Returns cached results immediately if available.
        Fetches new data in background async if use_async=True.
        """
        # Check cache first
        if query in _RESEARCH_CACHE:
            return _RESEARCH_CACHE[query]
        
        if use_async:
            # Start background fetch without blocking
            thread = threading.Thread(
                target=OnlineDataFetcher._fetch_pubmed_async,
                args=(query, max_results),
                daemon=True
            )
            thread.start()
        
        # Return empty list immediately (cache will fill on next request)
        return []
    
    @staticmethod
    def fetch_google_training_insights(query: str) -> List[str]:
        """
        Search Google for current training insights and trends.
        Uses Google Custom Search JSON API (requires API key).
        
        For free/demo version, returns curated insights from known sources.
        """
        insights = []
        
        # Known reliable training sources for demo
        sources = {
            "Recovery": [
                "Sleep deprivation reduces muscle protein synthesis by up to 30%",
                "Active recovery (light walking/yoga) accelerates adaptation",
                "Detraining begins after 2 weeks without training stimulus"
            ],
            "Progressive Overload": [
                "Progressive overload is the single most important factor for strength gains",
                "Aim for 2.5-5 lb increases or 1-2 rep increases monthly",
                "Slow progression beats plateaus: consistency > intensity"
            ],
            "Volume": [
                "Optimal training volume: 12-20 sets per muscle per week",
                "Volume increases hypertrophy but excessive volume increases injury risk",
                "MEV (Minimum Effective Volume) is 6-8 sets per muscle per week"
            ],
            "Form": [
                "Perfect rep quality beats heavy weight with poor form",
                "Eccentric (lowering) phase = 2-3 seconds for maximum tension",
                "Mind-muscle connection directly correlates with hypertrophy"
            ]
        }
        
        if query.lower() in sources:
            insights = sources[query.lower()]
        
        return insights

    @staticmethod
    def fetch_food_options(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch food suggestions from OpenFoodFacts for real-world meal ideas."""
        cache_key = f"food:{query.lower()}:{max_results}"
        if cache_key in _FOOD_CACHE:
            return _FOOD_CACHE[cache_key]

        try:
            foods = []
            seen_products = set()
            query_variants = [query.strip()]
            if " " in query:
                tokens = [token for token in query.lower().split() if len(token) > 2]
                query_variants.extend(tokens)
                if tokens:
                    query_variants.append(tokens[-1])

            for query_variant in query_variants:
                if not query_variant or len(foods) >= max_results:
                    continue
                response = requests.get(
                    "https://world.openfoodfacts.org/cgi/search.pl",
                    params={
                        "search_terms": query_variant,
                        "search_simple": 1,
                        "action": "process",
                        "json": 1,
                        "page_size": max_results,
                    },
                    timeout=5,
                    headers={"User-Agent": "HerculesWorkoutTracker/1.0"},
                )
                response.raise_for_status()
                payload = response.json()
                for product in payload.get("products", [])[:max_results]:
                    nutriments = product.get("nutriments", {})
                    name = (product.get("product_name") or product.get("generic_name") or "").strip()
                    if not name:
                        continue
                    brand = (product.get("brands") or "").strip()
                    dedupe_key = (name.lower(), brand.lower())
                    if dedupe_key in seen_products:
                        continue
                    seen_products.add(dedupe_key)
                    foods.append({
                        "name": name,
                        "brand": brand,
                        "calories": round(OnlineDataFetcher._safe_float(nutriments.get("energy-kcal_100g")), 1),
                        "protein_g": round(OnlineDataFetcher._safe_float(nutriments.get("proteins_100g")), 1),
                        "carbs_g": round(OnlineDataFetcher._safe_float(nutriments.get("carbohydrates_100g")), 1),
                        "fats_g": round(OnlineDataFetcher._safe_float(nutriments.get("fat_100g")), 1),
                        "fiber_g": round(OnlineDataFetcher._safe_float(nutriments.get("fiber_100g")), 1),
                        "url": product.get("url"),
                        "source": "OpenFoodFacts",
                    })
                    if len(foods) >= max_results:
                        break
            _FOOD_CACHE[cache_key] = foods
            return foods
        except Exception as exc:
            logger.debug("Food fetch error for '%s': %s", query, exc)
            return []


class HerculesEngine:
    """AI coaching engine that analyzes workouts and generates personalized advice."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.workouts: List[Dict[str, Any]] = []
        self.goals: List[Dict[str, Any]] = []

    def load_workouts(self, workouts: List[Any]) -> None:
        """Load and normalize workout data."""
        self.workouts = [
            {
                "date": w.date,
                "split": w.split,
                "exercise": w.exercise,
                "sets": w.sets,
                "reps": w.reps,
                "weight": w.weight,
                "volume": (w.sets or 0) * (w.reps or 0) * (w.weight or 0),
            }
            for w in workouts
        ]

    def load_goals(self, goals: List[Any]) -> None:
        """Load goal records from the database."""
        self.goals = [
            {
                "id": g.id,
                "goal_type": g.goal_type,
                "exercise": g.exercise,
                "target_weight": g.target_weight,
                "target_date": g.target_date,
                "achieved": g.achieved,
            }
            for g in goals
            if not g.achieved
        ]

    @staticmethod
    def calculate_nutrition_targets(profile: Dict[str, Any]) -> Dict[str, float]:
        """Calculate TDEE and macro targets using Mifflin-St Jeor."""
        sex = (profile.get("sex") or "male").lower()
        age = max(int(profile.get("age") or 25), 14)
        weight_lbs = max(float(profile.get("weight_lbs") or 180), 50)
        height_inches = max(float(profile.get("height_inches") or 70), 48)
        activity_multiplier = max(float(profile.get("activity_multiplier") or 1.55), 1.2)
        goal_type = (profile.get("goal_type") or "maintain").lower()
        daily_adjustment = int(profile.get("daily_calorie_adjustment") or 0)

        weight_kg = weight_lbs * 0.453592
        height_cm = height_inches * 2.54
        sex_adjustment = 5 if sex == "male" else -161
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + sex_adjustment
        tdee = bmr * activity_multiplier

        # Signed adjustment semantics:
        # negative values reduce calories (deficit), positive values increase calories (surplus).
        # If no manual value is provided, fall back to a goal-based default.
        if daily_adjustment != 0:
            target_calories = tdee + daily_adjustment
        elif goal_type == "cut":
            target_calories = tdee - 300
        elif goal_type == "bulk":
            target_calories = tdee + 250
        else:
            target_calories = tdee

        target_calories = max(target_calories, 1200)

        protein_g = max(weight_lbs * 0.9, 120)
        fats_g = max(weight_lbs * 0.3, 45)
        remaining_calories = max(target_calories - ((protein_g * 4) + (fats_g * 9)), 0)
        carbs_g = remaining_calories / 4 if remaining_calories else 0
        fiber_g = max((target_calories / 1000) * 14, 25)

        return {
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1),
            "target_calories": round(target_calories),
            "target_protein_g": round(protein_g, 1),
            "target_carbs_g": round(carbs_g, 1),
            "target_fats_g": round(fats_g, 1),
            "target_fiber_g": round(fiber_g, 1),
        }

    @staticmethod
    def summarize_meals(meals: List[Any]) -> Dict[str, float]:
        """Aggregate calories and macros for a collection of meals."""
        return {
            "calories": round(sum(float(getattr(meal, "calories", 0) or 0) for meal in meals), 1),
            "protein_g": round(sum(float(getattr(meal, "protein_g", 0) or 0) for meal in meals), 1),
            "carbs_g": round(sum(float(getattr(meal, "carbs_g", 0) or 0) for meal in meals), 1),
            "fats_g": round(sum(float(getattr(meal, "fats_g", 0) or 0) for meal in meals), 1),
            "fiber_g": round(sum(float(getattr(meal, "fiber_g", 0) or 0) for meal in meals), 1),
        }

    def generate_nutrition_tip(
        self,
        profile: Dict[str, Any],
        meals: List[Any],
        meal_name: str = "Next Meal",
    ) -> Dict[str, Any]:
        """Generate a meal-focused nutrition suggestion based on target gaps."""
        targets = self.calculate_nutrition_targets(profile)
        totals = self.summarize_meals(meals)
        remaining = {
            "calories": round(max(targets["target_calories"] - totals["calories"], 0), 1),
            "protein_g": round(max(targets["target_protein_g"] - totals["protein_g"], 0), 1),
            "carbs_g": round(max(targets["target_carbs_g"] - totals["carbs_g"], 0), 1),
            "fats_g": round(max(targets["target_fats_g"] - totals["fats_g"], 0), 1),
            "fiber_g": round(max(targets["target_fiber_g"] - totals["fiber_g"], 0), 1),
        }

        meals_per_day = max(int(profile.get("meals_per_day") or 4), 1)
        logged_meals = len(meals)
        meals_left = max(meals_per_day - logged_meals, 1)
        per_meal = {key: round(value / meals_left, 1) for key, value in remaining.items()}

        focus_macro = max(
            ["protein_g", "carbs_g", "fats_g", "fiber_g"],
            key=lambda key: remaining[key]
        )
        macro_labels = {
            "protein_g": "protein",
            "carbs_g": "carbs",
            "fats_g": "fats",
            "fiber_g": "fiber",
        }
        meal_keyword = (meal_name or "meal").lower()
        search_terms = {
            "protein_g": f"{meal_keyword} protein food",
            "carbs_g": f"{meal_keyword} carb food",
            "fats_g": f"{meal_keyword} healthy fat food",
            "fiber_g": f"{meal_keyword} high fiber food",
        }
        food_options = OnlineDataFetcher.fetch_food_options(search_terms[focus_macro], max_results=4)

        if not food_options:
            food_options = OnlineDataFetcher.fetch_food_options(macro_labels[focus_macro], max_results=4)

        category = "Meal Planning"
        tip = (
            f"For {meal_name}, aim for about {per_meal['calories']:.0f} kcal with "
            f"{per_meal['protein_g']:.0f}g protein, {per_meal['carbs_g']:.0f}g carbs, and {per_meal['fats_g']:.0f}g fats."
        )
        reasoning = (
            f"You're still short on {remaining['calories']:.0f} kcal today, with {remaining[focus_macro]:.0f}g of "
            f"{macro_labels[focus_macro]} left to cover. Splitting the remainder across {meals_left} meal(s) keeps the day realistic."
        )
        if totals["calories"] >= targets["target_calories"] * 0.98 and remaining["protein_g"] <= 10:
            category = "Nutrition On Track"
            tip = "You are close to your calorie and protein targets already. Keep the rest of the day lighter and prioritize micronutrient-dense foods."
            reasoning = "The main job now is recovery quality and consistency rather than forcing extra intake."

        return {
            "category": category,
            "tip": tip,
            "reasoning": reasoning,
            "source": "Hercules AI + OpenFoodFacts",
            "meal_name": meal_name,
            "targets": targets,
            "totals": totals,
            "remaining": remaining,
            "per_meal": per_meal,
            "food_options": food_options,
        }

    def _get_recent_workouts(self, days: int = 7) -> List[Dict]:
        """Get workouts from the last N days."""
        cutoff = datetime.now().date() - timedelta(days=days)
        return [w for w in self.workouts if w["date"] >= cutoff]

    def _get_volume_by_muscle(self, days: int = 7) -> Dict[str, int]:
        """Calculate total sets per muscle group in last N days."""
        recent = self._get_recent_workouts(days)
        muscle_volume = defaultdict(int)
        
        for workout in recent:
            exercise = workout["exercise"]
            muscles = EXERCISE_TO_MUSCLES.get(exercise, [])
            for muscle in muscles:
                muscle_volume[muscle] += workout.get("sets", 0)
        
        return dict(muscle_volume)

    def _get_volume_by_split(self, days: int = 7) -> Dict[str, int]:
        """Calculate total volume (sets × reps × weight) per split."""
        recent = self._get_recent_workouts(days)
        split_volume = defaultdict(float)
        
        for workout in recent:
            split = workout["split"]
            split_volume[split] += workout["volume"]
        
        return dict(split_volume)

    def _calculate_consistency_streak(self) -> int:
        """Calculate consecutive days with logged workouts."""
        if not self.workouts:
            return 0
        
        sorted_workouts = sorted(self.workouts, key=lambda w: w["date"])
        streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_workouts)):
            days_diff = (sorted_workouts[i]["date"] - sorted_workouts[i-1]["date"]).days
            if days_diff == 1:
                current_streak += 1
                streak = max(streak, current_streak)
            elif days_diff > 1:
                current_streak = 1
        
        return streak

    def _get_top_exercises(self, limit: int = 3) -> List[Tuple[str, int]]:
        """Get most frequently logged exercises."""
        exercise_counts = defaultdict(int)
        for workout in self.workouts:
            exercise_counts[workout["exercise"]] += 1
        
        return sorted(exercise_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def _get_strength_progression(self, exercise: str, days: int = 30) -> Optional[float]:
        """Calculate month-over-month strength trend for an exercise."""
        recent = self._get_recent_workouts(days)
        exercise_weights = [w["weight"] for w in recent if w["exercise"] == exercise]
        
        if len(exercise_weights) < 2:
            return None
        
        return ((max(exercise_weights) - min(exercise_weights)) / min(exercise_weights)) * 100

    def generate_coaching_tips(self, max_tips: int = 3) -> List[Dict]:
        """Generate up to max_tips personalised coaching tips, highest-priority first."""
        import random

        DEFAULT_TIPS = [
            {
                "category": "Form Focus",
                "tip": "Perfect reps with controlled tempo beat sloppy heavy weight. Move with intention on every rep.",
                "reasoning": "Mind-muscle connection and form quality drive adaptation and reduce injury.",
                "source": "Biomechanics & Neuroscience Research",
            },
            {
                "category": "Plate Discipline",
                "tip": "Most lifters use too much weight and sacrifice rep quality. Drop 10% and feel the difference.",
                "reasoning": "Time under tension and controlled eccentrics build muscle better than ego lifting.",
                "source": "Applied Strength Research",
            },
            {
                "category": "Sleep Priority",
                "tip": "Gains happen when you rest. Prioritise 7-9 hours tonight — your muscles are built in recovery.",
                "reasoning": "Sleep is anabolic: boosts testosterone, GH, and muscle protein synthesis while lowering cortisol.",
                "source": "Sleep Physiology Research",
            },
            {
                "category": "Nutrition",
                "tip": "Training is the stimulus. Protein is the building block. Eat 0.8-1g per lb of bodyweight daily.",
                "reasoning": "Adequate protein intake maximises muscle protein synthesis and recovery between sessions.",
                "source": "Sports Nutrition Research",
            },
            {
                "category": "Progressive Overload",
                "tip": "Track your lifts and aim to add 1-2 reps or 2.5-5 lbs each month.",
                "reasoning": "Adaptation only occurs when you present novel challenges. Stagnation = stagnation.",
                "source": "Exercise Adaptation Science",
            },
        ]

        if not self.workouts:
            seed = random.sample(DEFAULT_TIPS, min(max_tips, len(DEFAULT_TIPS)))
            seed[0] = {
                "category": "Getting Started",
                "tip": "Start logging your first workout! Consistency beats perfection every time.",
                "reasoning": "No workout data yet — once you log sessions Hercules will personalise these tips.",
                "source": "Hercules AI",
            }
            return seed[:max_tips]

        tips: List[Dict] = []

        # --- Priority 1: Recovery warning ---
        last_workout = sorted(self.workouts, key=lambda w: w["date"])[-1]
        days_since = (datetime.now().date() - last_workout["date"]).days
        if days_since >= 3:
            query = "detraining muscle loss recovery"
            OnlineDataFetcher.fetch_pubmed_research(query, use_async=True)
            insights = OnlineDataFetcher.fetch_google_training_insights("Recovery")
            research_url = None
            if query in _RESEARCH_CACHE and _RESEARCH_CACHE[query]:
                research_url = _RESEARCH_CACHE[query][0].get("url")
            tips.append({
                "category": "Recovery & Training Frequency",
                "tip": (
                    f"It's been {days_since} day{'s' if days_since != 1 else ''} since your last session. "
                    "Get back to the gym — detraining begins after 2 weeks without stimulus. "
                    + (insights[0] if insights else "")
                ).strip(),
                "reasoning": "Muscle protein synthesis peaks 24-48 h post-workout. Frequent training maintains adaptation.",
                "source": "Sports Science Research",
                "research_url": research_url,
            })

        # --- Priority 2: Volume prescription per split ---
        for split in list(VOLUME_RECOMMENDATIONS):
            if len(tips) >= max_tips:
                break
            total_sets = self._calculate_split_sets(split, 7)
            opt = VOLUME_RECOMMENDATIONS[split]
            if total_sets > 0 and total_sets < opt["optimal_min"]:
                query = f"{split} training volume hypertrophy"
                OnlineDataFetcher.fetch_pubmed_research(query, use_async=True)
                research_url = None
                if query in _RESEARCH_CACHE and _RESEARCH_CACHE[query]:
                    research_url = _RESEARCH_CACHE[query][0].get("url")
                tips.append({
                    "category": "Volume Prescription",
                    "tip": (
                        f"Your {split} split is getting {total_sets} set{'s' if total_sets != 1 else ''}/week. "
                        f"Aim for {opt['optimal_min']}–{opt['optimal_max']} sets for optimal hypertrophy."
                    ),
                    "reasoning": f"Research supports {opt['optimal_min']}–{opt['optimal_max']} sets/week per muscle for growth.",
                    "source": "Sports Science Research",
                    "research_url": research_url,
                })
            elif total_sets > opt["max_sustainable"]:
                tips.append({
                    "category": "Volume Management",
                    "tip": (
                        f"You're at {total_sets} sets/week on {split}. "
                        f"Consider deloading to {opt['optimal_max']} to avoid fatigue and overuse."
                    ),
                    "reasoning": "Beyond ~25 sets/week marginal gains drop and injury risk climbs.",
                    "source": "Sports Science Research",
                })

        # --- Priority 3: Strength progression ---
        if len(tips) < max_tips:
            top_exercises = self._get_top_exercises(1)
            if top_exercises:
                exercise, count = top_exercises[0]
                progression = self._get_strength_progression(exercise, 30)
                if progression is not None and progression > 5:
                    query = "progressive overload strength training"
                    OnlineDataFetcher.fetch_pubmed_research(query, use_async=True)
                    research_url = None
                    if query in _RESEARCH_CACHE and _RESEARCH_CACHE[query]:
                        research_url = _RESEARCH_CACHE[query][0].get("url")
                    tips.append({
                        "category": "Strength Gains",
                        "tip": f"Your {exercise} has improved {progression:.1f}% this month — you're in a solid progression window. Keep the overload coming.",
                        "reasoning": "Progressive overload is the cornerstone of strength development.",
                        "source": "PubMed Research" if research_url else "Sports Science",
                        "research_url": research_url,
                    })
                elif count >= 4:
                    ol_insights = OnlineDataFetcher.fetch_google_training_insights("Progressive Overload")
                    tips.append({
                        "category": "Exercise Specialisation",
                        "tip": f"You've logged {exercise} {count} times recently. Target small jumps (2.5–5 lbs) each session.",
                        "reasoning": "Plateaus are normal. " + (ol_insights[0] if ol_insights else "Micro-progress compounds into major gains over months."),
                        "source": "Applied Training Science",
                    })

        # --- Priority 4: Consistency milestone ---
        if len(tips) < max_tips:
            streak = self._calculate_consistency_streak()
            if streak >= 7:
                tips.append({
                    "category": "Consistency",
                    "tip": f"You've logged {streak} consecutive days — that habit is the #1 predictor of long-term gains.",
                    "reasoning": "Consistency > intensity. Long-term adherence outperforms any single training variable.",
                    "source": "Behavioral Science Research",
                })

        # --- Priority 5: Exercise variety ---
        if len(tips) < max_tips:
            unique_exercises = len(set(w["exercise"] for w in self._get_recent_workouts(14)))
            if 0 < unique_exercises < 5:
                tips.append({
                    "category": "Exercise Variety",
                    "tip": f"You've used {unique_exercises} distinct exercise{'s' if unique_exercises != 1 else ''} in two weeks. Adding 1–2 variations reduces overuse risk and balances development.",
                    "reasoning": "Varied stimulus from different angles produces balanced, resilient musculature.",
                    "source": "Biomechanics Research",
                })

        # --- Fill remaining slots with randomised defaults ---
        seen_categories = {t["category"] for t in tips}
        shuffled_defaults = [d for d in random.sample(DEFAULT_TIPS, len(DEFAULT_TIPS)) if d["category"] not in seen_categories]
        while len(tips) < max_tips and shuffled_defaults:
            tips.append(shuffled_defaults.pop(0))

        # --- Priority 0 (inserted after existing tips): Goal progress ---
        if len(tips) < max_tips and self.goals and self.workouts:
            for goal in self.goals:
                if len(tips) >= max_tips:
                    break
                if goal["goal_type"] == "lift" and goal["exercise"]:
                    ex_workouts = [w for w in self.workouts if w["exercise"] == goal["exercise"]]
                    if ex_workouts:
                        best = max(w["weight"] for w in ex_workouts)
                        pct = (best / goal["target_weight"]) * 100 if goal["target_weight"] else 0
                        if pct < 100:
                            remaining = goal["target_weight"] - best
                            tips.append({
                                "category": "Goal Progress",
                                "tip": (
                                    f"Your {goal['exercise']} best is {best:.1f} lbs — "
                                    f"{pct:.0f}% of your {goal['target_weight']:.0f} lb goal. "
                                    f"Only {remaining:.1f} lbs to go."
                                ),
                                "reasoning": "Tracking progress against specific targets accelerates goal attainment.",
                                "source": "Hercules Goal Tracker",
                            })
                        else:
                            tips.append({
                                "category": "Goal Progress",
                                "tip": (
                                    f"You've hit your {goal['exercise']} goal of {goal['target_weight']:.0f} lbs! "
                                    "Mark it as achieved and set a new target."
                                ),
                                "reasoning": "You've met your goal — update it to keep progressing.",
                                "source": "Hercules Goal Tracker",
                            })

        return tips[:max_tips]

    def generate_coaching_tip(self) -> Dict[str, str]:
        """Return the single highest-priority coaching tip. Kept for backward compatibility."""
        return self.generate_coaching_tips(1)[0]

    def generate_weekly_summary(self) -> Dict[str, Any]:
        """Generate a structured weekly check-in covering volume, frequency, and next steps."""
        week_workouts = self._get_recent_workouts(7)
        total_workouts_this_week = len(set(w["date"] for w in week_workouts))
        total_volume_this_week = int(sum(w["volume"] for w in week_workouts))
        sets_by_split = {split: self._calculate_split_sets(split, 7) for split in VOLUME_RECOMMENDATIONS}

        days_since_last: Optional[int] = None
        if self.workouts:
            last = sorted(self.workouts, key=lambda w: w["date"])[-1]
            days_since_last = (datetime.now().date() - last["date"]).days

        week_exercise_vol: Dict[str, float] = defaultdict(float)
        for w in week_workouts:
            week_exercise_vol[w["exercise"]] += w["volume"]
        top_mover = max(week_exercise_vol, key=lambda k: week_exercise_vol[k]) if week_exercise_vol else None

        volume_gaps = []
        for split, sets in sets_by_split.items():
            opt = VOLUME_RECOMMENDATIONS[split]
            if sets < opt["optimal_min"]:
                volume_gaps.append(f"{split} ({sets}/{opt['optimal_min']} sets minimum)")

        if total_workouts_this_week == 0:
            headline = "No sessions logged this week yet."
            narrative = "Start this week strong — even one session resets your momentum."
        elif total_workouts_this_week == 1:
            headline = "One session logged this week."
            narrative = "Good start. Aim for 3–4 sessions to hit optimal training frequency."
        elif total_workouts_this_week <= 3:
            headline = f"{total_workouts_this_week} sessions logged this week."
            narrative = "Solid consistency. One or two more sessions would round out the week."
        else:
            headline = f"Strong week — {total_workouts_this_week} sessions and {total_volume_this_week:,} lbs total volume."
            narrative = "You're in the optimal frequency range. Focus on intensity and exercise quality now."

        next_steps = []
        for gap in volume_gaps:
            next_steps.append(f"Add a {gap.split('(')[0].strip()} session to close the volume gap: {gap}")
        if days_since_last is not None and days_since_last >= 2:
            next_steps.append(f"It's been {days_since_last} day{'s' if days_since_last != 1 else ''} since your last workout — a session today keeps momentum alive.")
        if not next_steps:
            next_steps.append("Continue current pattern and focus on progressive overload next session.")

        return {
            "headline": headline,
            "narrative": narrative,
            "total_workouts_this_week": total_workouts_this_week,
            "total_volume_this_week": total_volume_this_week,
            "sets_by_split": sets_by_split,
            "top_mover": top_mover,
            "days_since_last": days_since_last,
            "volume_gaps": volume_gaps,
            "next_steps": next_steps,
        }

    def _calculate_split_sets(self, split: str, days: int) -> int:
        """Calculate total sets for a given split in last N days."""
        recent = self._get_recent_workouts(days)
        return sum(w.get("sets", 0) for w in recent if w["split"] == split)

    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate overall training statistics."""
        if not self.workouts:
            return {
                "total_sessions": 0,
                "total_volume_moved": 0,
                "consistency_streak": 0,
                "favorite_exercise": None,
                "week_volume": {},
            }

        return {
            "total_sessions": len(self.workouts),
            "total_volume_moved": int(sum(w["volume"] for w in self.workouts)),
            "consistency_streak": self._calculate_consistency_streak(),
            "favorite_exercise": self._get_top_exercises(1)[0][0] if self._get_top_exercises(1) else None,
            "week_volume": self._get_volume_by_split(7),
            "week_sets_by_muscle": self._get_volume_by_muscle(7),
        }

    def get_form_cue(self, exercise: str) -> str:
        """Return a form cue for a specific exercise."""
        cues = {
            "Bench Press": "Lower to mid-chest, elbows at 45°. Plant feet, drive through legs and back into the bench.",
            "Squat": "Chest up, core tight. Descend with control, knees tracking over toes. Drive through full foot.",
            "Deadlift": "Straight bar path. Engage lats before pulling. Hip hinge—push the floor away.",
            "Overhead Press": "Core braced, glutes tight. Press overhead while maintaining neutral spine. No hyperextension.",
            "Pull Up": "Full range of motion: dead hang to chin over bar. Control the descent—eccentric is key.",
            "Barbell Row": "Chest to bar. Retract shoulder blades. Engage lats, not just arms. Strict form over weight.",
            "Triceps Extension": "Elbows fixed, full range of motion. Slow eccentric. Mind-muscle connection matters.",
            "Bicep Curl": "Shoulders packed, elbows still. Squeeze at the top, control the negative. No momentum.",
            "Leg Press": "Full range without letting knees cave. Push through mid-foot, not just toes.",
            "Lat Pulldown": "Pull elbows down and back. Retract scaps. Avoid leaning back—let the machine do the work.",
        }
        return cues.get(exercise, f"Focus on controlled movement and full range of motion for {exercise}.")
