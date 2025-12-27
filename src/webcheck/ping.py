import platform
import asyncio

async def ping_handler(host):

    command = ['ping', '-c', '2', host]

    try:
        # Run the ping command asynchronously
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Ping failed: {stderr.decode()}")

        # Parse ping output
        output_lines = stdout.decode().strip().split('\n')
        result = []

        for line in output_lines:
            line = line.strip()
            if line and ('time=' in line or 'time<' in line):
                result.append(line)

    except Exception as e:
        raise Exception(f"Ping error: {str(e)}")

    return {
        "message": "Ping completed!",
        "result": result,
    }

handler = ping_handler