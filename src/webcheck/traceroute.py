import urllib.parse
import subprocess
import json
import asyncio

async def trace_route_handler(host):
    if not host:
        raise ValueError('No host provided')

    # Run traceroute command
    try:
        if subprocess.run(['which', 'traceroute'], capture_output=True).returncode == 0:
            cmd = ['traceroute', '-n', host]
        else:
            cmd = ['tracert', '-h', '30', host]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Traceroute failed: {stderr.decode()}")
        
        # Parse traceroute output into hops
        output_lines = stdout.decode().strip().split('\n')
        hops = []
        
        for line in output_lines[1:]:  # Skip header line
            line = line.strip()
            if line and not line.startswith('traceroute'):
                parts = line.split()
                if len(parts) > 1:
                    hop_data = {
                        'hop': parts[0],
                        'ip': parts[1] if len(parts) > 1 else '',
                        'rtt': []
                    }
                    
                    # Extract RTT values
                    for part in parts[2:]:
                        if part.replace('.', '').isdigit():
                            hop_data['rtt'].append(float(part))
                    
                    hops.append(hop_data)
        
        result = hops
        
    except Exception as e:
        raise Exception(f"Traceroute error: {str(e)}")

    return {
        "message": "Traceroute completed!",
        "result": result,
    }

handler = trace_route_handler