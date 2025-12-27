import os
import socket
import asyncio
import re

DEFAULT_PORTS_TO_CHECK = [
    20, 21, 22, 23, 25, 53, 80, 67, 68, 69,
    110, 119, 123, 143, 156, 161, 162, 179, 194,
    389, 443, 587, 993, 995,
    3000, 3306, 3389, 5060, 5900, 8000, 8080, 8888
]

PORTS = os.environ.get('PORTS_TO_CHECK', '').split(',') if os.environ.get('PORTS_TO_CHECK') else DEFAULT_PORTS_TO_CHECK

async def check_port(host, port):
    try:
        port_int = int(port)
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port_int),
            timeout=1.5
        )
        writer.close()
        await writer.wait_closed()
        return port_int
    except Exception as e:
        raise Exception(f"Error at port: {port}")


async def check_host_ports(domain):
    
    open_ports = []
    failed_ports = []

    def error_response(message, status_code=444):
        return {'error': message}

    async def check_port_wrapper(port):
        try:
            result = await check_port(domain, port)
            open_ports.append(result)
            return {'status': 'fulfilled', 'port': result}
        except Exception as e:
            failed_ports.append(int(port))
            return {'status': 'rejected', 'port': int(port)}
    
    promises = [check_port_wrapper(port) for port in PORTS]
    
    try:
        await asyncio.wait_for(asyncio.gather(*promises, return_exceptions=True), timeout=9.0)
    except asyncio.TimeoutError:
        checked_ports = open_ports + failed_ports
        ports_not_checked = [int(port) for port in PORTS if int(port) not in checked_ports]
        failed_ports.extend(ports_not_checked)
        return error_response('The function timed out before completing.')
    
    open_ports.sort()
    failed_ports.sort()
    
    return {'openPorts': open_ports, 'failedPorts': failed_ports}


handler = check_host_ports