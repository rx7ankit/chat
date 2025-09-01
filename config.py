# Configuration for parallel ChatGPT scraping

# Maximum number of concurrent browser instances
# Adjust based on your system's capabilities (RAM, CPU)
MAX_WORKERS = 10

# Timeout settings (in seconds)
PAGE_LOAD_TIMEOUT = 20
RESPONSE_WAIT_TIMEOUT = 60

# Browser optimization settings
DISABLE_IMAGES = True
DISABLE_CSS = False
HEADLESS_MODE = False  # Set to True for production

# Rate limiting (to avoid overwhelming ChatGPT)
MIN_DELAY_BETWEEN_REQUESTS = 1  # seconds
MAX_DELAY_BETWEEN_REQUESTS = 5  # seconds

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Logging level
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# System resource monitoring
MONITOR_RESOURCES = True
MAX_MEMORY_USAGE_GB = 8  # Maximum memory usage threshold
MAX_CPU_USAGE_PERCENT = 80  # Maximum CPU usage threshold
