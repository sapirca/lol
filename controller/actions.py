from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import logging
from animation.animation_manager import AnimationManager
from configs.config_kivsee import config as basic_config
from memory.memory_manager import MemoryManager
from controller.message_streamer import TAG_SYSTEM_INTERNAL


class Action(ABC):

    def __init__(self, message_streamer):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.message_streamer = message_streamer

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
            step_number = self.animation_manager.add_sequence(animation_str)

            result = {
                "status": "success",
                "message": f"Animation sequence added to step {step_number}.",
                "requires_confirmation": False,
                "data": {
                    "step_number": step_number,
                    "animation_sequence": params_dict["animation_sequence"]
                }
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
                "requires_confirmation": False,
                "data": {
                    "error": str(e)
                }
            }
            self._log_action_result("update_animation", error_result)
            return error_result


class GetAnimationAction(Action):

    def __init__(self, animation_manager, message_streamer):
        super().__init__(message_streamer)
        self.animation_manager = animation_manager

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return "step_number" in params_dict and isinstance(
            params_dict["step_number"], int)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params_dict = self._get_params_dict(params)
        step_number = params_dict["step_number"]
        try:
            animation = self.animation_manager.sequence_manager.steps.get(
                step_number, None)
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
                    "requires_confirmation": False,
                    "data": {
                        "error": f"No animation found for step {step_number}"
                    }
                }
            self._log_action_result("get_animation", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error retrieving animation: {str(e)}",
                "requires_confirmation": False,
                "data": {
                    "error": str(e)
                }
            }
            self._log_action_result("get_animation", error_result)
            return error_result


class AddToMemoryAction(Action):

    def __init__(self, memory_manager: MemoryManager, message_streamer):
        super().__init__(message_streamer)
        self.memory_manager = memory_manager

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
                "requires_confirmation": False,
                "data": {
                    "error": str(e)
                }
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

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("message" in params_dict
                and isinstance(params_dict["message"], str))

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            is_clarification = params_dict.get("is_clarification", False)

            result = {
                "status": "success",
                "message": params_dict["message"],
                "requires_confirmation": True,  # Always requires user response
                "message_type": "question",
                "data": {
                    "is_clarification": is_clarification,
                    "question": params_dict["message"]
                }
            }
            self._log_action_result("question", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Error processing question action: {str(e)}",
                "requires_confirmation": False,
                "data": {
                    "error": str(e)
                }
            }
            self._log_action_result("question", error_result)
            return error_result


class MemorySuggestionAction(Action):

    def __init__(self, message_streamer):
        super().__init__(message_streamer)

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
                "data": {
                    "suggestion": params_dict["message"]
                }
            }
            self._log_action_result("memory_suggestion", result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message":
                f"Error processing memory suggestion action: {str(e)}",
                "requires_confirmation": False,
                "data": {
                    "error": str(e)
                }
            }
            self._log_action_result("memory_suggestion", error_result)
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
