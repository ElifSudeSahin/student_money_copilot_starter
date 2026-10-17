import asyncio

from tetherto.qvac_sdk import Client, completion, load_model, unload_model
from tetherto.qvac_sdk.models import LLAMA_3_2_1B_INST_Q4_0


async def _ask_qvac(prompt: str) -> str:
    async with Client() as client:
        t = client.transport

        model_id = await load_model(
            t,
            model_src=LLAMA_3_2_1B_INST_Q4_0
        )

        answer = ""

        run = completion(
            t,
            model_id=model_id,
            history=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        async for event in run.events:
            if event.type == "contentDelta":
                answer += event.text

        await unload_model(t, model_id)

        return answer.strip()


def get_qvac_recommendation(prompt: str) -> str:
    return asyncio.run(_ask_qvac(prompt))
