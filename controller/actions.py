from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List
import json
import logging
from animation.animation_manager import AnimationManager
from configs.config_kivsee import config as basic_config
from memory.memory_manager import MemoryManager
from controller.message_streamer import TAG_SYSTEM_INTERNAL
from schemes.main_schema import MainSchema
from animation.frameworks.kivsee.compound_effects import beat_based_effects as bb_effects


class Action(ABC):
    """Base class for all actions in the system."""

    def __init__(self, message_streamer):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.message_streamer = message_streamer
        self._purpose = "No purpose specified"
        self._requires_confirmation = False
        self._returns = {}

    @property
    def purpose(self) -> str:
        """Get the purpose of this action."""
        return self._purpose

    @property
    def requires_confirmation(self) -> bool:
        """Get whether this action requires confirmation."""
        return self._requires_confirmation

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

    def __init__(self, animation_manager: AnimationManager, message_streamer):
        super().__init__(message_streamer)
        self.animation_manager = animation_manager
        self._purpose = "Create or update an animation sequence. This action will add the animation to the sequence manager."
        self._requires_confirmation = True
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

            self.animation_manager.render(animation_json)
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
                "requires_confirmation": False,
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
                "requires_confirmation": False
            }
            self._log_action_result("update_animation", error_result)
            return error_result


class GetAnimationAction(Action):

    def __init__(self, animation_manager: AnimationManager, message_streamer):
        super().__init__(message_streamer)
        self.animation_manager = animation_manager
        self._purpose = "Retrieve an existing animation sequence by step number"
        self._requires_confirmation = False
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
                    "requires_confirmation": False,
                    "data": {
                        "step_number": step_number,
                        "animation": animation
                    }
                }
            else:
                result = {
                    "status": "error",
                    "message": f"No animation found for step {step_number}",
                    "requires_confirmation": False
                }
            self._log_action_result("get_animation", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error retrieving animation: {str(e)}",
                "requires_confirmation": False
            }
            self._log_action_result("get_animation", error_result)
            return error_result


class AddToMemoryAction(Action):

    def __init__(self, memory_manager: MemoryManager, message_streamer):
        super().__init__(message_streamer)
        self.memory_manager = memory_manager
        self._purpose = "Add information to the system's memory"
        self._requires_confirmation = False
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
                "requires_confirmation": False,
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
                "requires_confirmation": False
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
                "requires_confirmation": True,  # Always requires user response
                "message_type": "clarification"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing clarification action: {str(e)}",
                "requires_confirmation": False
            }


class QuestionAction(Action):

    def __init__(self, message_streamer):
        super().__init__(message_streamer)
        self._purpose = "Ask a question to the user"
        self._requires_confirmation = True
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
                "requires_confirmation": True,  # Always requires user response
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
                "requires_confirmation": False
            }
            self._log_action_result("question", error_result)
            return error_result


class MemorySuggestionAction(Action):

    def __init__(self, message_streamer):
        super().__init__(message_streamer)
        self._purpose = "Suggest information to be stored in memory"
        self._requires_confirmation = True
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
                "requires_confirmation": True,  # Always requires user response
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
                "requires_confirmation": False
            }
            self._log_action_result("memory_suggestion", error_result)
            return error_result


class AnswerUserAction(Action):
    """Action for directly answering user questions without requiring further actions."""

    def __init__(self, message_streamer):
        super().__init__(message_streamer)
        self._purpose = "Answer a user's question directly without requiring further actions"
        self._requires_confirmation = False
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
                "requires_confirmation": False,
            }
            self._log_action_result("answer_user", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error processing answer action: {str(e)}",
                "requires_confirmation": False
            }
            self._log_action_result("answer_user", error_result)
            return error_result


class GenerateBeatBasedEffectAction(Action):
    """Action for retrieving beat-based effects for a song."""

    def __init__(self, message_streamer):
        super().__init__(message_streamer)
        self._purpose = "Get beat-based brightness effects for a given time range and BPM"
        self._requires_confirmation = False
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
                    "requires_confirmation": False
                }

            result = {
                "status": "success",
                "message":
                f"Generated a [{effect_type} effect] for time range {start_time_ms}-{end_time_ms}ms at {bpm} BPM",
                "requires_confirmation": False,
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
                "requires_confirmation": False
            }
            self._log_action_result("get_beat_based_effects", error_result)
            return error_result


class ActionRegistry:

    def __init__(self):
        self._actions = {}
        self._pending_confirmation = None

    def register_action(self, name: str, action: Action):
        self._actions[name] = action

    def get_action(self, name: str) -> Optional[Action]:
        return self._actions.get(name)

    def execute_action(self, name: str, params: Dict[str,
                                                     Any]) -> Dict[str, Any]:
        action = self.get_action(name)
        if not action:
            return {
                "status": "error",
                "message": f"Action {name} not found",
                "requires_confirmation": False
            }

        if not action.validate_params(params):
            return {
                "status": "error",
                "message": f"Invalid parameters for action {name}",
                "requires_confirmation": False
            }

        result = action.execute(params)
        result['name'] = name

        # Store pending confirmation if needed
        if result.get("requires_confirmation", False):
            self._pending_confirmation = (action, params)
        else:
            self._pending_confirmation = None

        return result

    def get_actions_documentation(self) -> str:
        """Generate documentation for all registered actions."""
        lines = ["Available Actions:", ""]

        for i, (name, action) in enumerate(self._actions.items(), 1):
            lines.append(f"{i}. {name}")
            lines.append(f"   - Purpose: {action.purpose}")

            # Get parameter schema from the action's class
            params_schema = None
            for base in action.__class__.__bases__:
                if hasattr(base, '__annotations__'):
                    params_schema = base.__annotations__.get('params', None)
                    if params_schema:
                        break

            if params_schema:
                lines.append("   - Parameters:")
                lines.append("     ```python")
                lines.append(f"     {params_schema.__name__}:")
                for field_name, field in params_schema.__fields__.items():
                    lines.append(
                        f"       {field_name}: {field.type_.__name__}  # {field.field_info.description}"
                    )
                lines.append("     ```")

            lines.append(
                f"   - Requires confirmation: {'Yes' if action.requires_confirmation else 'No'}"
            )

            if action.returns:
                lines.append("   - Returns:")
                for return_name, return_desc in action.returns.items():
                    lines.append(f"     - {return_name}: {return_desc}")

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
            "    \"requires_confirmation\": bool,  # Whether user confirmation is needed",
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
