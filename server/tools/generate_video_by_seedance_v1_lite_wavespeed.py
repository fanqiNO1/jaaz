from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId  # type: ignore
from langchain_core.runnables import RunnableConfig
from .video_generation import generate_video_with_provider
from .utils.image_utils import process_input_image


class GenerateVideoBySeedanceV1LiteInputT2VSchema(BaseModel):
    prompt: str = Field(
        description="Required. The prompt for video generation. Describe what you want to see in the video."
    )
    duration: int = Field(
        default=5,
        description="Optional. The duration of the video in seconds. Use 5 by default. Allowed values: 5, 10."
    )
    aspect_ratio: str = Field(
        default="16:9",
        description="Optional. The aspect ratio of the video. Allowed values: 1:1, 16:9, 4:3, 21:9"
    )
    camera_fixed: bool = Field(
        default=True,
        description="Optional. Whether to keep the camera fixed (no camera movement)."
    )
    tool_call_id: Annotated[str, InjectedToolCallId]


@tool("generate_video_by_seedance_v1_lite_t2v",
      description="Generate high-quality videos using Seedance V1 Lite model. Supports text-to-video generation.",
      args_schema=GenerateVideoBySeedanceV1LiteInputT2VSchema)
async def generate_video_by_seedance_v1_lite_t2v_wavespeed(
    prompt: str,
    config: RunnableConfig,
    tool_call_id: Annotated[str, InjectedToolCallId],
    duration: int = 5,
    aspect_ratio: str = "16:9",
    camera_fixed: bool = True,
) -> str:
    """
    Generate a video using Seedance V1 model via configured provider
    """

    return await generate_video_with_provider(
        prompt=prompt,
        resolution="720p",
        duration=duration,
        aspect_ratio=aspect_ratio,
        model="bytedance/seedance-v1-lite-t2v-720p",
        tool_call_id=tool_call_id,
        config=config,
        camera_fixed=camera_fixed,
    )
    # return "video generated successfully ![video_id: vi_8dJwtYYg.mp4](http://localhost:5174/api/file/vi_8dJwtYYg.mp4)"


# Export the tool for easy import
__all__ = ["generate_video_by_seedance_v1_lite_t2v_wavespeed"]
