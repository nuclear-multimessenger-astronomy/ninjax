"""Command-line entry points for ninjax."""

# Keep this module free of jim imports. `jimgw.core.single_event.time_utils`
# raises at import time when float64 is off, and this package initialises before
# any submodule, so a jim import here would run before the entry point can
# enable x64.
