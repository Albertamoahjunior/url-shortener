from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging
import json
from datetime import datetime
# Configure the logger to print to the console
logging.basicConfig(
    level=logging.INFO,  # Set the minimum logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format of the log messages
    handlers=[
        #logging.StreamHandler(), # Output logs to the console (stdout)
        # log to a file 
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(int(time.time() * 1000))  # Simple timestamp-based ID
        start_time = time.time()
        
        # Extract request details
        request_details = {
            "id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": request.client.host,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log incoming request
        logger.info(f"Incoming request: {json.dumps(request_details)}")
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response details
            response_details = {
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time,
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"Request completed: {json.dumps(response_details)}")
            
            return response
            
        except Exception as e:
            error_details = {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "path": request.url.path,
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Request failed: {json.dumps(error_details)}")
            raise
