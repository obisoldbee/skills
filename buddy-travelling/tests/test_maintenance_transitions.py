"""Include the portable service-health regressions in the package's standard suite."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from test_service_health import HealthTests  # noqa: E402,F401
