import azure.functions as func
import logging
import random
import time
import concurrent.futures
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Function to estimate Pi using Monte Carlo method
def monte_carlo_pi(points: int) -> int:
    inside_circle = sum(1 for _ in range(points) if (random.random()**2 + random.random()**2) <= 1)
    return inside_circle

# Multi-threaded Monte Carlo estimation
def estimate_pi_parallel(points: int, num_threads: int = 4):
    start_time = time.time()  # Start execution timer

    # Split work into chunks for parallel execution
    points_per_thread = points // num_threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(monte_carlo_pi, [points_per_thread] * num_threads)

    total_inside_circle = sum(results)
    pi_estimate = (total_inside_circle / points) * 4

    # Calculate execution time
    execution_time = time.time() - start_time
    error_margin = abs(pi_estimate - 3.141592653589793)

    return pi_estimate, execution_time, error_margin

@app.route(route="montecarlo")
def estimate_pi(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Monte Carlo Pi Approximation Function Triggered.")

    try:
        req_body = req.get_json()
        if not req_body:
            raise ValueError("Empty JSON body")
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid or missing JSON input. Expected {'points': int, 'threads': int}"}),
            mimetype="application/json",
            status_code=400
        )

    points = int(req_body.get("points", 1000000))  # Default: 1M points
    num_threads = int(req_body.get("threads", 4))  # Default: 4 threads

    pi_estimate, exec_time, error = estimate_pi_parallel(points, num_threads)

    response_data = {
        "pi_estimate": pi_estimate,
        "execution_time_seconds": round(exec_time, 5),
        "error_margin": round(error, 10),
        "threads_used": num_threads
    }

    return func.HttpResponse(json.dumps(response_data), mimetype="application/json")

@app.route(route="montecarlo-ui")
def serve_html(req: func.HttpRequest) -> func.HttpResponse:
    try:
        with open("index.html", "r", encoding="utf-8") as f:  
            html_content = f.read()
        return func.HttpResponse(html_content, mimetype="text/html")
    except Exception as e:
        return func.HttpResponse(f"Error loading page: {str(e)}", status_code=500)
