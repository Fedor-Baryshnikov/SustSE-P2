import httpx
import asyncio
import sys

OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "gemma3:27b"

PROMPT = """Write a complete Python script that uses FastAPI to create a REST API for a simple task management system. It should include:
1. A SQLite database using SQLAlchemy. 
2. Endpoints to Create, Read, Update, and Delete tasks. 
3. Task model should have fields: id, title, description, completed, and created_at. 
4. Use Pydantic for request and response validation. 
5. Include basic error handling for 404 cases.
Please provide the full, working code."""

async def main():
    if len(sys.argv) < 2:
        print("Missing output prefix")
        return

    output_prefix = sys.argv[1]

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": False
    }

    print(f"STRATEGY 1:Calling {MODEL}...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_API_URL, json=payload, timeout=300.0)
            response.raise_for_status()
            result = response.json()

            content = result.get("message", {}).get("content", "")
            tokens = result.get("eval_count", 0)

            print(f"STRATEGY 1: Tokens ({MODEL}): {tokens}")

            output_file = f"{output_prefix}_output.txt"
            with open(output_file, "w") as f:
                f.write(content)

            tokens_file = f"{output_prefix}_tokens.txt"
            with open(tokens_file, "w") as f:
                f.write(f"{MODEL}:{tokens}\n")

            print(f"STRATEGY 1: Output saved to {output_file}")

    except Exception as e:
        print(f"STRATEGY 1: Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())