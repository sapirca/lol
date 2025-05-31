from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List
import json
import logging
from animation.animation_manager import AnimationManager
from configs.config_kivsee import config as basic_config
from memory.memory_manager import MemoryManager
from controller.message_streamer import TAG_SYSTEM_INTERNAL
from music.song_provider import SongProvider
from schemes.main_schema import MainSchema, ConfirmationType
from animation.frameworks.kivsee.layers import brightness_layer as bb_effects


class Action(ABC):
    """Base class for all actions in the system."""

    def __init__(self, message_streamer):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.message_streamer = message_streamer
        self._purpose = "No purpose specified"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {}

    @property
    def purpose(self) -> str:
        """Get the purpose of this action."""
        return self._purpose

    @property
    def confirmation_type(self) -> ConfirmationType:
        """Get the confirmation type for this action."""
        return self._confirmation_type

    @property
    def returns(self) -> Dict[str, str]:
        """Get the return values of this action."""
        return self._returns

    def _get_params_dict(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert params to dictionary if it's a Pydantic model"""
        if hasattr(params, 'model_dump'):
            return params.model_dump()
        return params

    def _log_action_result(self, action_name: str, result: Dict[str, Any]):
        """Log action result to message streamer"""
        status = result.get("status", "unknown")
        message = result.get("message", "")
        log_message = f"Action '{action_name}' completed with status: {status}\nDetails: {message}"
        self.message_streamer.add_invisible(TAG_SYSTEM_INTERNAL,
                                            log_message,
                                            context=False)

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action with given parameters"""
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate the parameters required for this action"""
        pass


class UpdateAnimationAction(Action):

    def __init__(self, animation_manager: AnimationManager, message_streamer,
                 song_name: str):
        super().__init__(message_streamer)
        self.animation_manager = animation_manager
        self._purpose = "Create or update an animation sequence. This action will add the animation to the sequence manager."
        self._song_name = song_name
        self._returns = {
            # "step_number":
            # "The step number that will be assigned if confirmed",
        }

    def _get_params_dict(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert params to dictionary if it's a Pydantic model"""
        if hasattr(params, 'model_dump'):
            return params.model_dump(exclude_unset=True, exclude_none=True)
        return params

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return "animation_sequence" in params_dict

    def render_preview(self, animation_json):
        """Render a preview of the provided animation JSON."""
        try:
            if not animation_json:
                return "Error: No animation JSON provided for preview."

            self.animation_manager.render(animation_json,
                                          self.song_name,
                                          store_animation=True)
            return "Animation preview rendered successfully."
        except Exception as e:
            return f"Error rendering animation preview: {e}"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params_dict = self._get_params_dict(params)
        animation_str = json.dumps(params_dict["animation_sequence"], indent=4)

        try:
            # Directly add the animation to the sequence manager
            result_message = self.animation_manager.add_sequence(animation_str)
            # current_steps_count = len(
            #     self.animation_manager.sequence_manager.steps)

            result = {
                "status": "success",
                "message": result_message,
                "confirmation_type": params_dict["confirmation_type"],
                # "data": {
                #     "step_number": current_steps_count
                # }
            }

            # Auto-render if configured
            if basic_config.get("auto_render", False):
                render_result = self.render_preview(
                    params_dict["animation_sequence"])
                result[
                    "message"] += f"\nRendering animation preview...\n{render_result}"

            self._log_action_result("update_animation", result)
            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error adding animation sequence: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("update_animation", error_result)
            return error_result


class GetAnimationAction(Action):

    def __init__(self, animation_manager: AnimationManager, message_streamer):
        super().__init__(message_streamer)
        self.animation_manager = animation_manager
        self._purpose = "Retrieve an existing animation sequence by step number"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "step_number": "The requested step number",
            "animation": "The animation sequence data"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return "step_number" in params_dict and isinstance(
            params_dict["step_number"], int)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params_dict = self._get_params_dict(params)
        step_number = int(params_dict["step_number"])

        try:
            animation = self.animation_manager.get_sequence_by_step(
                step_number)
            if animation:
                result = {
                    "status": "success",
                    "message": f"Retrieved animation for step {step_number}",
                    "confirmation_type": params_dict["confirmation_type"],
                    "data": {
                        "step_number": step_number,
                        "animation": animation
                    }
                }
            else:
                result = {
                    "status": "error",
                    "message": f"No animation found for step {step_number}",
                    "confirmation_type": params_dict["confirmation_type"]
                }
            self._log_action_result("get_animation", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error retrieving animation: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("get_animation", error_result)
            return error_result


class AddToMemoryAction(Action):

    def __init__(self, memory_manager: MemoryManager, message_streamer):
        super().__init__(message_streamer)
        self.memory_manager = memory_manager
        self._purpose = "Add information to the system's memory"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "key": "The key under which the value was stored",
            "value": "The value that was stored"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("key" in params_dict and isinstance(params_dict["key"], str)
                and "value" in params_dict
                and isinstance(params_dict["value"], str))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params_dict = self._get_params_dict(params)
        try:
            key = params_dict["key"]
            value = params_dict["value"]

            self.memory_manager.write_to_memory(key, value)

            result = {
                "status": "success",
                "message": f"Memory saved:\n {{\"{key}\": \"{value}\"}}",
                "confirmation_type": params_dict["confirmation_type"],
                "data": {
                    "key": key,
                    "value": value
                }
            }
            self._log_action_result("add_to_memory", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error adding to memory: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("add_to_memory", error_result)
            return error_result


class ClarificationAction(Action):

    def __init__(self):
        super().__init__()

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("message" in params_dict
                and isinstance(params_dict["message"], str))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            return {
                "status": "success",
                "message": params_dict["message"],
                "confirmation_type": self.confirmation_type,
                "message_type": "clarification"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing clarification action: {str(e)}",
                "confirmation_type": self.confirmation_type
            }


class QuestionAction(Action):

    def __init__(self, message_streamer):
        super().__init__(message_streamer)
        self._purpose = "Ask a question to the user"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            # "question": "The question that was asked",
            # "is_clarification": "Whether this is a clarification question"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("message" in params_dict
                and isinstance(params_dict["message"], str))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            # is_clarification = params_dict.get("is_clarification", False)

            result = {
                "status": "success",
                "message": params_dict["message"],
                "confirmation_type": params_dict["confirmation_type"],
                # "message_type": "question",
                # "data": {
                #     "question": params_dict["message"],
                #     "is_clarification": is_clarification
                # }
            }
            self._log_action_result("question", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error processing question action: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("question", error_result)
            return error_result


class MemorySuggestionAction(Action):

    def __init__(self, message_streamer):
        super().__init__(message_streamer)
        self._purpose = "Suggest information to be stored in memory"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {"suggestion": "The suggested information to store"}

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("message" in params_dict
                and isinstance(params_dict["message"], str))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            result = {
                "status": "success",
                "message": params_dict["message"],
                "confirmation_type": params_dict["confirmation_type"],
                "message_type": "memory_suggestion",
                # "data": {
                #     "suggestion": params_dict["message"]
                # }
            }
            self._log_action_result("memory_suggestion", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message":
                f"Error processing memory suggestion action: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("memory_suggestion", error_result)
            return error_result


class AnswerUserAction(Action):
    """Action for directly answering user questions without requiring further actions."""

    def __init__(self, message_streamer):
        super().__init__(message_streamer)
        self._purpose = "Answer a user's question directly without requiring further actions"
        self._returns = {}

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("message" in params_dict
                and isinstance(params_dict["message"], str))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            result = {
                "status": "success",
                "message": params_dict["message"],
                "confirmation_type": params_dict["confirmation_type"],
            }
            self._log_action_result("answer_user", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error processing answer action: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("answer_user", error_result)
            return error_result


class GenerateBeatBasedEffectAction(Action):
    """Action for retrieving beat-based effects for a song."""

    def __init__(self, message_streamer):
        super().__init__(message_streamer)
        self._purpose = "Get beat-based brightness effects for a given time range and BPM"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "EffectConfig":
            "The time frame of the relevant effect config",
            "BrightnessEffectConfig":
            "This is the data for the BrightnessEffectConfig. This can be put into the animation for any element you want, make sure to put this alongside a coloring like const_color or rainbow",
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("start_time_ms" in params_dict
                and isinstance(params_dict["start_time_ms"], int)
                and params_dict["start_time_ms"] >= 0
                and "end_time_ms" in params_dict
                and isinstance(params_dict["end_time_ms"], int)
                and params_dict["end_time_ms"] > params_dict["start_time_ms"]
                and "bpm" in params_dict
                and isinstance(params_dict["bpm"], int)
                and params_dict["bpm"] > 0)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            start_time_ms = params_dict["start_time_ms"]
            end_time_ms = params_dict["end_time_ms"]
            bpm = params_dict["bpm"]
            effect_type = params_dict["beat_based_effect_type"]

            # Create effect based on the type
            effect_config = None
            if effect_type == "breath":
                effect_config = bb_effects.create_breath_effect_by_the_beat(
                    start_time_ms, end_time_ms, bpm)
            elif effect_type == "soft_pulse":
                effect_config = bb_effects.create_soft_pulse_effect(
                    start_time_ms, end_time_ms, 0.5,
                    bpm)  # Using 0.5 as default intensity
            elif effect_type == "strobe":
                effect_config = bb_effects.create_strobe_effect(
                    start_time_ms, end_time_ms, bpm)
            elif effect_type == "fade_in_out":
                effect_config = bb_effects.create_fade_in_out_effect(
                    start_time_ms, end_time_ms, bpm)
            elif effect_type == "blink":
                effect_config = bb_effects.create_blink_effect_by_the_beat(
                    start_time_ms, end_time_ms, bpm)
            elif effect_type == "blink_and_fade_out":
                effect_config = bb_effects.create_blink_and_fade_out_effect_by_the_beat(
                    start_time_ms, end_time_ms, bpm)
            elif effect_type == "fade_in_and_disappear":
                effect_config = bb_effects.create_fade_in_and_disappear_effect_by_the_beat(
                    start_time_ms, end_time_ms, bpm)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown effect type: {effect_type}",
                    "confirmation_type": params_dict["confirmation_type"]
                }

            result = {
                "status": "success",
                "message":
                f"Generated a [{effect_type} effect] for time range {start_time_ms}-{end_time_ms}ms at {bpm} BPM",
                "confirmation_type": params_dict["confirmation_type"],
                "data": {
                    "EffectConfig": {
                        "start_time": start_time_ms,
                        "end_time": end_time_ms
                    },
                    "BrightnessEffectConfig": effect_config
                }
            }
            self._log_action_result("get_beat_based_effects", result)
            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error getting beat-based effects: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("get_beat_based_effects", error_result)
            return error_result


class RemoveMemoryAction(Action):
    """Action for removing a memory entry by key."""

    def __init__(self, memory_manager: MemoryManager, message_streamer):
        super().__init__(message_streamer)
        self.memory_manager = memory_manager
        self._purpose = "Remove a memory entry by its key"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "key": "The key that was removed",
            "success": "Whether the removal was successful"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return "key" in params_dict and isinstance(params_dict["key"], str)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            key = params_dict["key"]

            success = self.memory_manager.remove_from_memory(key)

            if success:
                result = {
                    "status": "success",
                    "message":
                    f"Successfully removed memory entry with key: {key}",
                    "confirmation_type": params_dict["confirmation_type"],
                    "data": {
                        "key": key,
                        "success": True
                    }
                }
            else:
                result = {
                    "status": "error",
                    "message": f"No memory entry found with key: {key}",
                    "confirmation_type": params_dict["confirmation_type"],
                    "data": {
                        "key": key,
                        "success": False
                    }
                }

            self._log_action_result("remove_memory", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error removing memory: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("remove_memory", error_result)
            return error_result


class UpdateMemoryAction(Action):
    """Action for updating an existing memory entry or creating a new one."""

    def __init__(self, memory_manager: MemoryManager, message_streamer):
        super().__init__(message_streamer)
        self.memory_manager = memory_manager
        self._purpose = "Update an existing memory entry or create a new one"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "key": "The key that was updated",
            "value": "The new value after update",
            "was_created": "Whether a new entry was created"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("key" in params_dict and isinstance(params_dict["key"], str)
                and "value" in params_dict
                and isinstance(params_dict["value"], str))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            key = params_dict["key"]
            value = params_dict["value"]

            # Get existing value if it exists
            was_created = self.memory_manager.read_from_memory(key) is None

            self.memory_manager.write_to_memory(key, value)

            result = {
                "status": "success",
                "message":
                f"{'Created' if was_created else 'Updated'} memory entry with key: {key}",
                "confirmation_type": params_dict["confirmation_type"],
                "data": {
                    "key": key,
                    "value": value,
                    "was_created": was_created
                }
            }

            self._log_action_result("update_memory", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error updating memory: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("update_memory", error_result)
            return error_result


class GetMusicStructureAction(Action):
    """Action for retrieving specific aspects of music structure."""

    def __init__(self, song_provider: SongProvider, message_streamer):
        super().__init__(message_streamer)
        self.song_provider = song_provider
        self._purpose = "Get specific aspects of music structure (lyrics, key points, drum pattern, beats/bars)"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "structure_type": "The type of structure requested",
            "data": "The requested music structure data"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("structure_type" in params_dict
                and params_dict["structure_type"]
                in ["lyrics", "key_points", "drum_pattern", "beats"])

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            structure_type = params_dict["structure_type"]
            song_name = params_dict["song_name"]

            # Get the appropriate structure data based on type
            if structure_type == "lyrics":
                data = self.song_provider.get_lyrics(song_name)
            elif structure_type == "key_points":
                data = self.song_provider.get_key_points(song_name)
            elif structure_type == "drum_pattern":
                data = self.song_provider.get_drum_pattern(song_name)
            elif structure_type == "beats":
                data = self.song_provider.get_beats(song_name)
            else:
                raise ValueError(f"Unknown structure type: {structure_type}")

            result = {
                "status": "success",
                "message": f"Retrieved {structure_type} structure data",
                "confirmation_type": params_dict["confirmation_type"],
                "data": {
                    "structure_type": structure_type,
                    "data": data
                }
            }

            self._log_action_result("get_music_structure", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error getting music structure: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("get_music_structure", error_result)
            return error_result


class SaveCompoundEffectAction(Action):
    """Action for saving a compound effect."""

    def __init__(self, compound_effects_manager, message_streamer):
        super().__init__(message_streamer)
        self.compound_effects_manager = compound_effects_manager
        self._purpose = "Save a compound effect with a name and tags"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "name": "The name of the saved compound effect",
            "tags": "The tags associated with the compound effect",
            "success": "Whether the save operation was successful"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("name" in params_dict and isinstance(params_dict["name"], str)
                and "effects" in params_dict
                and isinstance(params_dict["effects"], list)
                and "tags" in params_dict
                and isinstance(params_dict["tags"], list))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            name = params_dict["name"]
            effects = params_dict["effects"]
            tags = params_dict["tags"]

            success = self.compound_effects_manager.save_compound_effect(
                name, effects, tags)

            result = {
                "status": "success" if success else "error",
                "message":
                f"{'Successfully saved' if success else 'Failed to save'} compound effect '{name}'",
                "confirmation_type": params_dict["confirmation_type"],
                "data": {
                    "name": name,
                    "tags": tags,
                    "success": success
                }
            }
            self._log_action_result("save_compound_effect", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error saving compound effect: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("save_compound_effect", error_result)
            return error_result


class GetCompoundEffectAction(Action):
    """Action for retrieving a compound effect by name."""

    def __init__(self, compound_effects_manager, message_streamer):
        super().__init__(message_streamer)
        self.compound_effects_manager = compound_effects_manager
        self._purpose = "Get a compound effect by its name"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "name": "The name of the compound effect",
            "effects": "The list of effects in the compound effect",
            "tags": "The tags associated with the compound effect"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return "name" in params_dict and isinstance(params_dict["name"], str)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            name = params_dict["name"]

            compound_effect = self.compound_effects_manager.get_compound_effect(
                name)

            if compound_effect:
                result = {
                    "status": "success",
                    "message": f"Retrieved compound effect '{name}'",
                    "confirmation_type": params_dict["confirmation_type"],
                    "data": {
                        "name": compound_effect.name,
                        "effects": compound_effect.effects,
                        "tags": compound_effect.tags
                    }
                }
            else:
                result = {
                    "status": "error",
                    "message": f"No compound effect found with name '{name}'",
                    "confirmation_type": params_dict["confirmation_type"]
                }

            self._log_action_result("get_compound_effect", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error retrieving compound effect: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("get_compound_effect", error_result)
            return error_result


class GetCompoundEffectsKeysAndTagsAction(Action):
    """Action for retrieving all compound effect names and their tags."""

    def __init__(self, compound_effects_manager, message_streamer):
        super().__init__(message_streamer)
        self.compound_effects_manager = compound_effects_manager
        self._purpose = "Get all compound effect names and their associated tags"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "effects": "Dictionary mapping effect names to their tags"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return True  # No parameters needed

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            effects = self.compound_effects_manager.get_all_effects_keys_and_tags(
            )

            result = {
                "status": "success",
                "message": f"Retrieved {len(effects)} compound effects",
                "confirmation_type": params_dict["confirmation_type"],
                "data": {
                    "effects": effects
                }
            }
            self._log_action_result("get_compound_effects_keys_and_tags",
                                    result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error retrieving compound effects: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("get_compound_effects_keys_and_tags",
                                    error_result)
            return error_result


class GetRandomEffectAction(Action):
    """Action for retrieving a random effect from the random bank."""

    def __init__(self, compound_effects_manager, message_streamer):
        super().__init__(message_streamer)
        self.compound_effects_manager = compound_effects_manager
        self._purpose = "Get a random effect from the random bank by its number"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "number": "The number of the random effect",
            "effect": "The random effect data"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return "number" in params_dict and isinstance(params_dict["number"],
                                                      int)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            number = params_dict["number"]

            effect = self.compound_effects_manager.get_random_effect(number)

            if effect:
                result = {
                    "status": "success",
                    "message": f"Retrieved random effect {number}",
                    "confirmation_type": params_dict["confirmation_type"],
                    "data": {
                        "number": number,
                        "effect": effect
                    }
                }
            else:
                result = {
                    "status": "error",
                    "message": f"No random effect found with number {number}",
                    "confirmation_type": params_dict["confirmation_type"]
                }

            self._log_action_result("get_random_effect", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error retrieving random effect: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("get_random_effect", error_result)
            return error_result


class DeleteRandomEffectAction(Action):
    """Action for deleting a random effect from the random bank."""

    def __init__(self, compound_effects_manager, message_streamer):
        super().__init__(message_streamer)
        self.compound_effects_manager = compound_effects_manager
        self._purpose = "Delete a random effect from the random bank by its number"
        self._confirmation_type = ConfirmationType.ASK_EVERY_TIME
        self._returns = {
            "number": "The number of the deleted random effect",
            "success": "Whether the deletion was successful"
        }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return "number" in params_dict and isinstance(params_dict["number"],
                                                      int)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            number = params_dict["number"]

            success = self.compound_effects_manager.delete_random_effect(
                number)

            result = {
                "status": "success" if success else "error",
                "message":
                f"{'Successfully deleted' if success else 'Failed to delete'} random effect {number}",
                "confirmation_type": params_dict["confirmation_type"],
                "data": {
                    "number": number,
                    "success": success
                }
            }
            self._log_action_result("delete_random_effect", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error deleting random effect: {str(e)}",
                "confirmation_type": params_dict["confirmation_type"]
            }
            self._log_action_result("delete_random_effect", error_result)
            return error_result


class ActionRegistry:
    """Registry for all available actions in the system."""

    def __init__(self):
        self._actions = {}
        self._pending_action = None
        self._pending_params = None
        self._last_action_result = None

    def register_action(self, name: str, action: Action):
        """Register a new action with the given name."""
        self._actions[name] = action

    def get_action(self, name: str) -> Optional[Action]:
        """Get an action by name."""
        return self._actions.get(name)

    def get_last_action_result(self) -> Optional[Dict[str, Any]]:
        """Get the result of the last executed action."""
        return self._last_action_result

    def has_pending_action(self) -> bool:
        """Check if there is a pending action waiting for confirmation."""
        return self._pending_action is not None

    def get_pending_action_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the pending action."""
        if not self.has_pending_action():
            return None

        action = self._actions.get(self._pending_action)
        # if not action:
        #     return None

        params_dict = action._get_params_dict(self._pending_params)
        return {
            "action_name": self._pending_action,
            "turn": params_dict.get("turn"),
            "confirmation_type": params_dict.get("confirmation_type")
        }

    def execute_pending_action(self):
        """Execute the pending action with its parameters."""
        if self._pending_action and self._pending_params:
            action = self._actions.get(self._pending_action)
            if action:
                # Now we actually execute the action
                result = action.execute(self._pending_params)
                self._last_action_result = result
                # Clear pending state after execution
                self._pending_action = None
                self._pending_params = None
                return result
        return None

    def cancel_pending_action(self):
        """Cancel the pending action."""
        self._pending_action = None
        self._pending_params = None
        self._last_action_result = {
            "status": "cancelled",
            "message": "Action cancelled by user",
            "confirmation_type": "no-action-required"
        }

    def execute_action(self, name: str, params: Dict[str,
                                                     Any]) -> Dict[str, Any]:
        """Store an action for later execution after confirmation."""
        action = self._actions.get(name)
        if not action:
            return {
                "status": "error",
                "message": f"Action {name} not found",
                "confirmation_type": ConfirmationType.ASK_EVERY_TIME
            }

        if not action.validate_params(params):
            return {
                "status": "error",
                "message": f"Invalid parameters for action {name}",
                "confirmation_type": ConfirmationType.ASK_EVERY_TIME
            }

        try:
            # Get the confirmation type from the params
            params_dict = action._get_params_dict(params)
            confirmation_type = params_dict.get(
                "confirmation_type", ConfirmationType.ASK_EVERY_TIME)

            # For actions that don't require confirmation, execute immediately
            if confirmation_type == ConfirmationType.NO_ACTION_REQUIRED:
                result = action.execute(params)
                self._last_action_result = result
                # Clear any pending action when executing a no-confirmation action
                self._pending_action = None
                self._pending_params = None
                return result

            # For actions that require confirmation, store them for later execution
            self._pending_action = name
            # Convert params to dict if it's a Pydantic model
            if hasattr(params, 'model_dump'):
                self._pending_params = params.model_dump()
            else:
                self._pending_params = params

            # Return a pending confirmation result
            return {
                "status": "pending_confirmation",
                "message":
                f"Action '{name}' requires confirmation before execution",
                "confirmation_type": confirmation_type,
            }

        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error preparing action {name}: {str(e)}",
                "confirmation_type": ConfirmationType.ASK_EVERY_TIME
            }
            self._last_action_result = error_result
            # Clear pending state on error
            self._pending_action = None
            self._pending_params = None
            return error_result

    def get_actions_documentation(self) -> str:
        """Get documentation for all registered actions."""
        lines = []
        for name, action in self._actions.items():
            lines.append(f"Action: {name}")
            lines.append(f"  - Purpose: {action.purpose}")
            lines.append(f"  - Confirmation type: {action.confirmation_type}")
            if action.returns:
                lines.append("  - Returns:")
                for key, desc in action.returns.items():
                    lines.append(f"    - {key}: {desc}")
            lines.append("")
        return "\n".join(lines)

    def get_result_format_documentation(self) -> str:
        """Generate documentation for the action result format."""
        lines = [
            "Action Results:",
            "- After each action is executed, its result will be included in your next context",
            "- Results include both success and error information",
            "- Results format:", "  ```python", "  {",
            "    \"action\": str,  # Name of the executed action",
            "    \"status\": Literal[\"success\", \"error\"],  # Result status",
            "    \"message\": str,  # Human-readable message",
            "    \"confirmation_type\": Literal[\"ask_every_time\", \"ask_once\", \"no_confirmation\"],  # Confirmation type",
            "    \"data\": Optional[Dict[str, Any]]  # Action-specific return data (only on success)",
            "  }", "  ```",
            "- Use these results to make informed decisions in your next response",
            "- For actions requiring confirmation, wait for user confirmation before proceeding",
            ""
        ]
        return "\n".join(lines)

    def get_response_format_documentation(self) -> str:
        """Generate documentation for the response format."""
        lines = [
            "Your responses must follow this exact structure:", "```python"
        ]

        # Get the schema fields and their descriptions
        schema_fields = MainSchema.__fields__  # Assuming MainSchema is a Pydantic BaseModel

        # Helper function to get a readable type name
        def get_type_name(
                field_annotation) -> str:  # Renamed parameter for clarity
            if hasattr(field_annotation, '__name__'):
                return field_annotation.__name__
            elif hasattr(field_annotation,
                         '__origin__'):  # Handles Union, List, Dict, etc.
                if field_annotation.__origin__ is typing.Union:
                    # For Union types (e.g., str | None), get names of all constituent types
                    args = field_annotation.__args__
                    # Filter out NoneType for cleaner representation if it's optional
                    type_names = [
                        get_type_name(arg) for arg in args
                        if arg is not type(None)
                    ]
                    if len(type_names) == 1 and type(
                            None) in args:  # Optional[Type]
                        return f"Optional[{type_names[0]}]"
                    return " | ".join(type_names)
                else:
                    # For generic types like List[str], Dict[str, int]
                    origin_name = get_type_name(field_annotation.__origin__)
                    args_names = [
                        get_type_name(arg) for arg in field_annotation.__args__
                    ]
                    return f"{origin_name}[{', '.join(args_names)}]"
            return str(field_annotation)  # Fallback for any other complex type

        # Build the schema documentation
        lines.append("{")
        for field_name, field in schema_fields.items():
            description = field.description or ""
            # Access the type annotation using .annotation
            field_type_str = get_type_name(field.annotation)
            lines.append(
                f'    "{field_name}": {field_type_str},  # {description}')
        lines.append("}")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)
