import asyncio
import sys

from tetherto.qvac_sdk import Client, completion, load_model, unload_model
from tetherto.qvac_sdk.models import LLAMA_3_2_1B_INST_Q4_0


async def main():
    async with Client() as client:
        t = client.transport

        print("Loading local QVAC model...")

        model_id = await load_model(
            t,
            model_src=LLAMA_3_2_1B_INST_Q4_0
        )

        print("\nModel loaded.\n")

        run = completion(
            t,
            model_id=model_id,
            history=[
                {
                    "role": "user",
                    "content": (
    "You are a student budgeting assistant. "
    "Do not perform any calculations yourself. "
    "Use only the numbers provided. "
    "Current balance: €534. "
    "Upcoming mandatory expenses: €345. "
    "Safe-to-spend amount: €189. "
    "Proposed purchase: €100. "
    "Flexible money after the purchase: €89. "
    "The purchase is affordable, but it would reduce the student's flexible budget. "
    "Give a short recommendation in 2 sentences."),
        
                }
            ],
        )

        async for event in run.events:
            if event.type == "contentDelta":
                sys.stdout.write(event.text)
                sys.stdout.flush()

        print()

        await unload_model(t, model_id)


asyncio.run(main())