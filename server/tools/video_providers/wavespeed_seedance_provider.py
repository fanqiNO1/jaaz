import os
import asyncio
import traceback
from typing import Any, Optional
from unittest import result
from .video_base_provider import VideoProviderBase
from services.config_service import config_service
from utils.http_client import HttpClient


class WavespeedSeedDanceVideoProvider(VideoProviderBase, provider_name="wavespeed"):
    """WaveSpeed video generation (seedance) provider implementation"""

    def _build_headers(self) -> dict[str, str]:
        """Build request headers"""
        config = config_service.app_config.get('wavespeed', {})
        api_key = str(config.get("api_key", ""))
        api_url = str(config.get("url", ""))
        channel = os.environ.get('WAVESPEED_CHANNEL', 'jaaz_main')

        if not api_key:
            raise ValueError("WaveSpeed API key is not configured")
        if not api_url:
            raise ValueError("WaveSpeed API URL is not configured")
        return {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'channel': channel,
        }
    

    def _build_payload(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        camera_fixed: bool = True,
        input_images_data: Optional[str] = None,
    ) -> dict[str, Any]:
        payload = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "camera_fixed": camera_fixed,
        }
        if input_images_data is not None:
            payload["image"] = input_images_data
        return payload


    async def _poll_for_result(self, result_url: str, headers: dict[str, str]) -> str:
        """Poll for video generation result"""
        async with HttpClient.create_aiohttp() as session:
            for _ in range(120):  # 最多等120秒
                await asyncio.sleep(1)
                async with session.get(result_url, headers=headers) as result_resp:
                    result_data = await result_resp.json()
                    print("WaveSpeed polling result:", result_data)

                    data = result_data.get("data", {})
                    outputs = data.get("outputs", [])
                    status = data.get("status")

                    if status in ("succeeded", "completed") and outputs:
                        return outputs[0]

                    if status == "failed":
                        raise Exception(
                            f"WaveSpeed generation failed: {result_data}")

            raise Exception("WaveSpeed video generation timeout")
    
    async def generate(
        self,
        prompt: str,
        model: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        camera_fixed: bool = True,
        input_image_data: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate video using Seedance provided by WaveSpeed API service.
        
        Args:
            prompt: Video generation prompt
            duration: Video duration in seconds
            aspect_ratio: Video aspect ratio
            camera_fixed: Whether the camera is fixed
        
        Returns:
            str: Video URL for download
        """
        try:
            headers = self._build_headers()
            payload = self._build_payload(prompt, duration, aspect_ratio, camera_fixed, input_image_data)
        
            config = config_service.app_config.get('wavespeed', {})
            api_url = str(config.get("url", "")).rstrip("/")
            endpoint = f"{api_url}/{model}"

            async with HttpClient.create_aiohttp() as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    response_json = await response.json()

                    if response.status != 200 or response_json.get("code") != 200:
                        raise Exception(
                            f"WaveSpeed API error: {response_json}")

                    result_url = response_json["data"]["urls"]["get"]
                    print(result_url)

            # Poll for the result
            video_url = await self._poll_for_result(result_url, headers)
            print(
                f"🎥 WaveSpeed video generation completed, video URL: {video_url}")

            return video_url

        except Exception as e:
            print('Error generating video with WaveSpeed:', e)
            traceback.print_exc()
            raise e