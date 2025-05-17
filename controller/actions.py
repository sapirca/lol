from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import logging
from animation.animation_manager import AnimationManager
from configs.config_kivsee import config as basic_config
from memory.memory_manager import MemoryManager


class Action(ABC):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_params_dict(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert params to dictionary if it's a Pydantic model"""
        if hasattr(params, 'model_dump'):
            return params.model_dump()
        return params

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action with given parameters"""
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate the parameters required for this action"""
        pass


class UpdateAnimationAction(Action):

    def __init__(self, animation_manager: AnimationManager):
        super().__init__()
        self.animation_manager = animation_manager
        self.temp_animation_path = None

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
                # self.logger.warning("No animation JSON provided for preview.")
                return "Error: No animation JSON provided for preview."

            self.animation_manager.render(animation_json)
            # self.logger.info("Animation preview rendered successfully.")
            return "Animation preview rendered successfully."
        except Exception as e:
            # self.logger.error(f"Error rendering animation preview: {e}")
            return f"Error rendering animation preview: {e}"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params_dict = self._get_params_dict(params)
        animation_str = json.dumps(params_dict["animation_sequence"], indent=4)

        # Save the animation sequence to a temporary file
        self.temp_animation_path = self.animation_manager.save_tmp_animation(
            animation_str)

        output = {
            "status": "success",
            "message":
            f"Animation sequence generated and saved to:\n{self.temp_animation_path}\n",
            "requires_confirmation": True,
            "temp_path": self.temp_animation_path,
        }

        # Auto-render if configured
        if basic_config.get("auto_render", False):
            output["message"] += "Rendering animation preview..."
            render_result = self.render_preview(
                params_dict["animation_sequence"])
            output["message"] += f"\n{render_result}"

        return output


class GetAnimationAction(Action):

    def __init__(self, animation_manager):
        super().__init__()
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
                return {
                    "status": "success",
                    "message": f"Retrieved animation for step {step_number}",
                    "requires_confirmation": False,
                    "data": {
                        "step_number": step_number,
                        "animation": animation
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": f"No animation found for step {step_number}",
                    "requires_confirmation": False
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving animation: {str(e)}",
                "requires_confirmation": False
            }


class AddToMemoryAction(Action):

    def __init__(self, memory_manager: MemoryManager):
        super().__init__()
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
            # Don't write to memory yet, wait for user confirmation
            return {
                "status": "success",
                "message":
                f"Ready to add memory with key: {key} and value: {value}. Do you want to save this to memory? (y/n)",
                "requires_confirmation": True,
                "data": {
                    "key": key,
                    "value": value,
                    "action": "add_to_memory"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error preparing memory addition: {str(e)}",
                "requires_confirmation": False
            }


class InformUserAction(Action):

    def __init__(self):
        super().__init__()

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("message" in params_dict
                and isinstance(params_dict["message"], str)
                and "message_type" in params_dict
                and params_dict["message_type"]
                in ["information", "answer", "error"])

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            return {
                "status": "success",
                "message": params_dict["message"],
                "requires_confirmation": False,
                "data": {
                    "message": params_dict["message"],
                    "message_type": params_dict["message_type"]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing inform user action: {str(e)}",
                "requires_confirmation": False
            }


class AskUserAction(Action):

    def __init__(self):
        super().__init__()

    def validate_params(self, params: Dict[str, Any]) -> bool:
        params_dict = self._get_params_dict(params)
        return ("message" in params_dict
                and isinstance(params_dict["message"], str)
                and "message_type" in params_dict
                and params_dict["message_type"]
                in ["clarification", "question", "memory_suggestion"])

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            params_dict = self._get_params_dict(params)
            return {
                "status": "success",
                "message": params_dict["message"],
                "requires_confirmation": True,  # Always requires user response
                "data": {
                    "message": params_dict["message"],
                    "message_type": params_dict["message_type"]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing ask user action: {str(e)}",
                "requires_confirmation": False
            }


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
        if result.get("requires_confirmation", False):
            self._pending_confirmation = (action, result.get("temp_path"))

        return result
