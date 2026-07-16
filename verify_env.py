import sys

print(f"Python Version: {sys.version}")
print("Verifying library imports...")

try:
    import can
    print(f"  [SUCCESS] python-can (version {can.__version__})")
except ImportError as e:
    print(f"  [FAILED] python-can: {e}")

try:
    import cantools
    print(f"  [SUCCESS] cantools (version {cantools.__version__})")
except ImportError as e:
    print(f"  [FAILED] cantools: {e}")

try:
    import udsoncan
    print(f"  [SUCCESS] udsoncan")
except ImportError as e:
    print(f"  [FAILED] udsoncan: {e}")

try:
    import isotp
    print(f"  [SUCCESS] can-isotp (version {isotp.__version__})")
except ImportError as e:
    print(f"  [FAILED] can-isotp: {e}")

try:
    import serial
    print(f"  [SUCCESS] pyserial (version {serial.__version__})")
except ImportError as e:
    print(f"  [FAILED] pyserial: {e}")
