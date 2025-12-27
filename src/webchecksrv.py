import asyncio
import inspect
import logging
from contextlib import asynccontextmanager, AsyncExitStack

from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from scanhistory import get_last_scans_by_type
from webcheck.conf import WEBCHECK_DATA_DIR
from webcheckcli import scan_domain_sync

@asynccontextmanager
async def lifespan(main_app: FastAPI):
    print("Setting up resources for main app lifespan...")
    async with AsyncExitStack() as stack:
        # init resources for the main app
        try:
            yield
        finally:
            # teardown in reverse order is handled by ExitStack
            pass


logging.basicConfig(level=logging.INFO)


### FastAPI routes

router = APIRouter()


# async def perform_scan_async(domain_name: str) -> dict:
#     """
#     Perform a domain scan asynchronously.
#     """
#     loop = asyncio.get_running_loop()
#     result = await loop.run_in_executor(None, scan_domain_sync, domain_name)
#     return result

@router.get("/webcheck/scans")
async def get_recent_scans() -> dict:
    """
    Retrieve a list of recently scanned domains.
    """
    last_scanned_domains = get_last_scans_by_type("domain", limit=25)
    return {"domains": list(last_scanned_domains)}


@router.get("/webcheck/d/{domain_name}")
async def get_domain_results(domain_name: str) -> dict:
    """
    Retrieve scan results by domain name.
    """
    # load scan result from file
    filename = f"{WEBCHECK_DATA_DIR}/webcheck/{domain_name}/scan_result.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            import json

            data = json.load(f)
            return data
    except FileNotFoundError:
        return {"error": "Scan result not found for domain: " + domain_name}
    except Exception as e:
        return {"error": str(e)}


@router.post("/webcheck/d/{domain_name}")
async def create_domain_scan(domain_name: str) -> dict:
    """
    Create a new scan for the given domain name.
    """
    #loop = asyncio.get_running_loop()
    #result = await loop.run_in_executor(None, scan_domain_sync, domain_name, True, False)
    result = await asyncio.to_thread(scan_domain_sync, domain_name, force=False)
    #print(result)
    return result


@router.post("/webcheck/c/{check_name}")
async def get_webcheck_results(check_name: str, domain: str=None) -> dict:
    """
    Retrieve scan results by scan ID.
    """
    # get url parameter from query string
    # e.g. /xscan/webcheck/{check_name}?url=http://example.com
    if not domain:
        return {"error": "domain parameter is required."}

    if check_name in ["cookies", "threats", "screenshot", "tls"]:
        return {"error": "Check is currently disabled globally."}

    ckeck_module = check_name #.replace("-", "_")
    module_name = "webcheck." + ckeck_module
    # load the "handler" function from the module
    # and invoke with url as parameter
    try:
        module = __import__(module_name, fromlist=["handler"])
        h = getattr(module, "handler")

        # handler can be async or sync
        if inspect.iscoroutinefunction(h):
            out = await asyncio.wait_for(
                h(domain), timeout=30
            )
        else:
            # run blocking handler in a thread so it can't block the loop
            out = await asyncio.wait_for(
                asyncio.to_thread(h, domain),
                timeout=30,
            )

        #return {"check_name": check_name, "result": out}
        return out
    except (ImportError, AttributeError) as e:
        return {"error": "Check not found: " + str(e)}
    except Exception as e:
        return {"error": str(e)}


### FastAPI app with lifespan context

app = FastAPI(title="Webcheck API", version="1.0.0", lifespan=lifespan)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)