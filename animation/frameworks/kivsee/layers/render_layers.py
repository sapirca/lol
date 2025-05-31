from typing import List, Dict, Union, Optional
from animation.frameworks.kivsee.layers.coloring_layer import create_alternate_effect, create_alternate_between_multiple_elements, create_segmeneted_alternate_color_multiple_elements
from animation.frameworks.kivsee.layers.masking_layer import create_dot_masking, create_round_masking
from animation.frameworks.kivsee.layers.motion_layer import create_snow_sparkle_elements
from animation.frameworks.kivsee.layers.brightness_layer import (
    create_breath_effect_by_the_beat, create_blink_effect_by_the_beat,
    create_blink_and_fade_out_effect_by_the_beat,
    create_fade_in_and_disappear_effect_by_the_beat, create_soft_pulse_effect,
    create_strobe_effect, create_fade_in_out_effect)
from animation.frameworks.kivsee.renderer.render import Render


def create_color_effect(start_time_ms: int, end_time_ms: int,
                        color: str) -> Dict[str, Union[str, List[str], Dict]]:
    return {
        "effect_config": {
            "start_time": start_time_ms,
            "end_time": end_time_ms,
            "segments": "all",
        },
        "const_color": {
            "color": {
                "hue": float(color),
                "sat": 1.0,
                "val": 1.0,
            }
        },
    }


def create_layer_animation(layer_type: str, elements: List[str],
                           start_time_ms: int, end_time_ms: int, bpm: int,
                           **kwargs) -> Dict[str, Union[str, List[str], Dict]]:
    """
    Create a single layer animation with the specified parameters.
    
    Args:
        layer_type: Type of layer animation to create
        elements: List of elements to apply the animation to
        start_time_ms: Start time in milliseconds
        end_time_ms: End time in milliseconds
        bpm: Beats per minute for timing
        **kwargs: Additional parameters specific to each layer type
    
    Returns:
        Dictionary containing the effect configuration
    """
    # Get the base effect configuration
    if layer_type == "alternate_color":
        base_effect = create_alternate_effect(
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            color_1=kwargs.get("color_1", "0.0"),
            color_2=kwargs.get("color_2", "0.5"),
            elements=elements)
    elif layer_type == "snow_sparkle":
        base_effect = create_snow_sparkle_elements(elements=elements,
                                                   start_time_ms=start_time_ms,
                                                   end_time_ms=end_time_ms,
                                                   bpm=bpm)
    elif layer_type == "breath":
        base_effect = create_breath_effect_by_the_beat(
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            bpm=bpm,
            elements=elements)
    elif layer_type == "blink":
        base_effect = create_blink_effect_by_the_beat(
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            bpm=bpm,
            elements=elements)
    elif layer_type == "dot_mask":
        base_effect = create_dot_masking(start_time_ms=start_time_ms,
                                         end_time_ms=end_time_ms,
                                         sparsity=kwargs.get("sparsity", 0.5),
                                         elements=elements)
    elif layer_type == "round_mask":
        base_effect = create_round_masking(sparsity=kwargs.get(
            "sparsity", 0.5),
                                           elements=elements)
    else:
        raise ValueError(f"Unknown layer type: {layer_type}")

    # Add color effect to layers that don't have their own color
    if layer_type not in ["alternate_color", "snow_sparkle"
                          ]:  # Skip layers that already have color
        color_effect = create_color_effect(start_time_ms=start_time_ms,
                                           end_time_ms=end_time_ms,
                                           color=kwargs.get("color", "0.0"))

        # Create new dictionary with combined effects
        combined_effects = {}
        for element in base_effect.keys():
            # Create a new config that combines color and base effect
            combined_config = []
            combined_config.append(color_effect)
            elements_effects = base_effect[element]
            if isinstance(elements_effects, list):
                combined_config.extend(elements_effects)
            else:
                combined_config.append(elements_effects)
            combined_effects[element] = combined_config

        base_effect = combined_effects

    return base_effect


def render_layers(
        layers_config: List[Dict],
        elements: List[str],
        bpm: int,
        base_start_time: int = 0,
        time_increment: int = 1000) -> Dict[str, Union[str, List[str], Dict]]:
    """
    Render multiple layers of animations with sequential timing.
    
    Args:
        layers_config: List of layer configurations, each containing:
            - type: Type of layer animation
            - elements: List of elements to apply to (optional, defaults to all)
            - **kwargs: Additional parameters for the specific layer type
        elements: List of all available elements
        bpm: Beats per minute for timing
        base_start_time: Starting time for the first layer
        time_increment: Time increment between layers in milliseconds
    
    Returns:
        Dictionary containing all layer animations
    """
    all_effects = {}
    current_time = base_start_time

    for layer_config in layers_config:
        layer_type = layer_config.pop("type")
        layer_elements = layer_config.pop("elements", elements)

        # Calculate timing for this layer
        start_time = current_time
        end_time = start_time + time_increment

        # Create the layer animation
        layer_effects = create_layer_animation(layer_type=layer_type,
                                               elements=layer_elements,
                                               start_time_ms=start_time,
                                               end_time_ms=end_time,
                                               bpm=bpm,
                                               **layer_config)

        for element in layer_effects.keys():
            if element not in all_effects:
                all_effects[element] = layer_effects[element]
            else:
                all_effects[element].extend(layer_effects[element])

        # Increment time for next layer
        current_time = end_time

    return all_effects


def create_and_render_animation(layers_config: List[Dict],
                                elements: List[str],
                                bpm: int,
                                animation_name: str,
                                base_start_time: int = 0,
                                time_increment: int = 1000,
                                playback_offset: int = 0) -> None:
    """
    Create and render a layered animation using the renderer.
    
    Args:
        layers_config: List of layer configurations
        elements: List of elements to apply animations to
        bpm: Beats per minute for timing
        animation_name: Name of the animation
        base_start_time: Starting time for the first layer
        time_increment: Time increment between layers in milliseconds
        playback_offset: Offset in milliseconds for playback timing
    """
    # Create the layered animation
    layered_effects = render_layers(layers_config=layers_config,
                                    elements=elements,
                                    bpm=bpm,
                                    base_start_time=base_start_time,
                                    time_increment=time_increment)

    # Create animation data in the format expected by renderer
    animation_data = {
        "name": animation_name,
        "animation": {
            "duration_ms":
            base_start_time + (len(layers_config) * time_increment),
            "num_repeats": 1,
            "effects": []
        }
    }

    animations_per_element = {}

    for element in layered_effects.keys():
        animations_per_element[element] = {
            "duration_ms":
            base_start_time + (len(layers_config) * time_increment),
            "num_repeats": 1,
            "effects": layered_effects[element]
        }

    preprocessed_animation_data = {
        "name": animation_name,
        "animation_data_per_element": animations_per_element
    }

    renderer = Render()
    renderer.render_unpacked_animation(preprocessed_animation_data)


def main():
    # Define the elements we want to animate
    elements = ["ring7", "ring8", "ring9", "ring10", "ring11", "ring12"]

    # Create a layered animation configuration
    layers_config = [
        {
            "type": "alternate_color",
            "elements": elements,
            "color_1": "0.0",  # Red
            "color_2": "0.5"  # Blue
        },
        {
            "type": "alternate_color",
            "elements": elements[::2],  # Even rings
            "color_1": "0.0",  # Red
            "color_2": "0.33"  # Green
        },
        {
            "type": "breath",
            "elements": elements[::3],  # Every third ring
            "color": "0.1"
        },
        {
            "type": "dot_mask",
            "elements":
            elements[1::3],  # Every third ring starting from second
            "sparsity": 0.3,
            "color": "0.5"  # Yellow
        },
        {
            "type": "snow_sparkle",
            "elements": elements[1::2],  # Odd rings
            "color": "0.67"  # Purple
        },
    ]

    # Create and render the animation
    create_and_render_animation(
        layers_config=layers_config,
        elements=elements,
        bpm=120,  # 120 beats per minute
        animation_name="sparkle_animation",
        base_start_time=0,
        time_increment=2000,  # 1 second between layers
        playback_offset=0)


if __name__ == "__main__":
    main()
