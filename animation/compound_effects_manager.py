from typing import Dict, List, Optional
import json
import os
from schemes.kivsee_scheme.effects_scheme import EffectProto
from pydantic import BaseModel


class CompoundEffect(BaseModel):
    """Represents a compound effect - a collection of EffectProtos that are rendered together"""
    name: str
    tags: List[str]
    effects: List[EffectProto]


AI_BANK_PATH = "./animation/compounds/ai_bank"
RAND_BANK_PATH = "./animation/compounds/rand_bank"


class CompoundEffectsManager:

    def __init__(self, storage_dir: str = AI_BANK_PATH, world: str = "rings"):
        """Initialize the compound effects manager with a storage directory and world"""
        self.storage_dir = storage_dir
        self.world = world
        # EffectProto.set_world(world)  # Set the world for validation
        self._ensure_storage_dir()
        self._effects: Dict[str, CompoundEffect] = {}
        self._load_effects()

    def _ensure_storage_dir(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_dir, exist_ok=True)

    def _load_effects(self):
        """Load all compound effects from storage"""
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.storage_dir, filename),
                              'r') as f:
                        effect_data = json.load(f)
                        # Set world before deserializing
                        # EffectProto.set_world(self.world)
                        compound_effect = CompoundEffect(**effect_data)
                        self._effects[compound_effect.name] = compound_effect
                except Exception as e:
                    print(f"Error loading compound effect {filename}: {e}")

    def get_random_effect(self, number: int) -> Optional[Dict]:
        """Get a random effect from the random bank by its number"""
        try:
            filepath = os.path.join(RAND_BANK_PATH, f"random_{number}.json")
            if not os.path.exists(filepath):
                return None

            with open(filepath, 'r') as f:
                effect_data = json.load(f)
                return effect_data
        except Exception as e:
            print(f"Error reading random effect {number}: {e}")
            return None

    def delete_random_effect(self, number: int) -> bool:
        """Delete a random effect from the random bank"""
        try:
            filepath = os.path.join(RAND_BANK_PATH, f"random_{number}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting random effect {number}: {e}")
            return False

    def save_compound_effect(self, name: str, effects: List[EffectProto],
                             tags: List[str]) -> bool:
        """Save a compound effect with the given name, effects, and tags"""
        try:
            compound_effect = CompoundEffect(name=name,
                                             effects=effects,
                                             tags=tags)
            self._effects[name] = compound_effect

            # Save to file
            filepath = os.path.join(self.storage_dir, f"{name}.json")
            with open(filepath, 'w') as f:
                json.dump(compound_effect.model_dump(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving compound effect {name}: {e}")
            return False

    def get_compound_effect(self, name: str) -> Optional[CompoundEffect]:
        """Retrieve a compound effect by name"""
        return self._effects.get(name)

    def get_all_effects_keys_and_tags(self) -> Dict[str, List[str]]:
        """Get all compound effect names and their associated tags"""
        return {name: effect.tags for name, effect in self._effects.items()}

    def delete_compound_effect(self, name: str) -> bool:
        """Delete a compound effect by name"""
        try:
            if name in self._effects:
                del self._effects[name]
                filepath = os.path.join(self.storage_dir, f"{name}.json")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting compound effect {name}: {e}")
            return False

    def update_compound_effect(self, name: str, effects: List[EffectProto],
                               tags: List[str]) -> bool:
        """Update an existing compound effect"""
        if name not in self._effects:
            return False
        return self.save_compound_effect(name, effects, tags)
