FUEL_SYSTEM_STATUS = {
    1: "Open loop (insufficient temp)",
    2: "Closed loop",
    4: "Open loop (engine load/decel)",
    8: "Open loop (system failure)",
    16: "Closed loop (feedback fault)"
}

def decode_fuel_system_status(data):
    if len(data) >= 2:
        sys1 = FUEL_SYSTEM_STATUS.get(data[0], f"Unknown ({data[0]})")
        sys2 = FUEL_SYSTEM_STATUS.get(data[1], "N/A") if data[1] != 0 else "N/A"
        return f"Sys1: {sys1}, Sys2: {sys2}"
    elif len(data) == 1:
        return FUEL_SYSTEM_STATUS.get(data[0], f"Unknown ({data[0]})")
    return data.hex()

OBD_STANDARDS = {
    1: "OBD-II (CARB)", 2: "OBD (EPA)", 3: "OBD and OBD-II", 4: "OBD-I",
    5: "Not intended to meet any OBD standard", 6: "EOBD (Europe)",
    7: "EOBD and OBD-II", 8: "EOBD and OBD", 9: "EOBD, OBD and OBD II",
    10: "JOBD (Japan)", 11: "JOBD and OBD II", 12: "JOBD and EOBD",
    13: "JOBD, EOBD, and OBD II", 17: "EMD", 18: "EMD+",
    19: "HD OBD-C", 20: "HD OBD", 21: "WWH OBD",
    23: "HD EOBD-I", 24: "HD EOBD-I N", 25: "HD EOBD-II",
    26: "HD EOBD-II N", 28: "OBDBr-1", 29: "OBDBr-2",
    30: "KOBD", 31: "IOBD I", 32: "IOBD II", 33: "HD EOBD-IV",
}

FUEL_TYPES = {
    1: "Gasoline", 2: "Methanol", 3: "Ethanol", 4: "Diesel", 5: "LPG",
    6: "CNG", 7: "Propane", 8: "Electric", 9: "Bifuel Gas",
    10: "Bifuel Methanol", 11: "Bifuel Ethanol", 12: "Bifuel LPG",
    13: "Bifuel CNG", 14: "Bifuel Propane", 15: "Bifuel Electric",
    16: "Bifuel Mixed", 17: "Hybrid Gas", 18: "Hybrid Ethanol",
    19: "Hybrid Diesel", 20: "Hybrid Electric", 21: "Hybrid Mixed",
    22: "Hybrid Regen", 23: "Bifuel Diesel",
}

OBD2_PIDS = {
    0x00: {"name": "PIDs supported [01 - 20]", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x01: {"name": "Monitor status since DTCs cleared", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x02: {"name": "Freeze DTC", "unit": "", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x03: {"name": "Fuel system status", "unit": "", "cluster": "Fuel System", "dynamic": True, "decode": decode_fuel_system_status},
    0x04: {"name": "Calculated engine load", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Engine Load", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x05: {"name": "Engine coolant temperature", "unit": "°C", "cluster": "Engine Performance", "dynamic": True, "group": "Coolant & Oil Temperature", "min": 80, "max": 110, "decode": lambda data: data[0] - 40 if len(data) >= 1 else None},
    0x06: {"name": "Short term fuel trim Bank 1", "unit": "%", "cluster": "Fuel System", "dynamic": True, "group": "Fuel Trim Bank 1", "min": -10, "max": 10, "decode": lambda data: (data[0] / 1.28) - 100 if len(data) >= 1 else None},
    0x07: {"name": "Long term fuel trim Bank 1", "unit": "%", "cluster": "Fuel System", "dynamic": True, "group": "Fuel Trim Bank 1", "min": -10, "max": 10, "decode": lambda data: (data[0] / 1.28) - 100 if len(data) >= 1 else None},
    0x08: {"name": "Short term fuel trim Bank 2", "unit": "%", "cluster": "Fuel System", "dynamic": True, "group": "Fuel Trim Bank 2", "min": -10, "max": 10, "decode": lambda data: (data[0] / 1.28) - 100 if len(data) >= 1 else None},
    0x09: {"name": "Long term fuel trim Bank 2", "unit": "%", "cluster": "Fuel System", "dynamic": True, "group": "Fuel Trim Bank 2", "min": -10, "max": 10, "decode": lambda data: (data[0] / 1.28) - 100 if len(data) >= 1 else None},
    0x0A: {"name": "Fuel pressure", "unit": "kPa", "cluster": "Fuel System", "dynamic": True, "decode": lambda data: data[0] * 3 if len(data) >= 1 else None},
    0x0B: {"name": "Intake manifold absolute pressure", "unit": "kPa", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: data[0] if len(data) >= 1 else None},
    0x0C: {"name": "Engine RPM", "unit": "rpm", "cluster": "Engine Performance", "dynamic": True, "group": "Engine RPM", "min": 600, "max": 6000, "decode": lambda data: ((data[0] * 256) + data[1]) / 4 if len(data) >= 2 else None},
    0x0D: {"name": "Vehicle speed", "unit": "km/h", "cluster": "Engine Performance", "dynamic": True, "group": "Vehicle Speed", "min": 0, "max": 130, "decode": lambda data: data[0] if len(data) >= 1 else None},
    0x0E: {"name": "Timing advance", "unit": "°", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: (data[0] / 2) - 64 if len(data) >= 1 else None},
    0x0F: {"name": "Intake air temperature", "unit": "°C", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: data[0] - 40 if len(data) >= 1 else None},
    0x10: {"name": "MAF air flow rate", "unit": "g/s", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: ((data[0] * 256) + data[1]) / 100 if len(data) >= 2 else None},
    0x11: {"name": "Throttle position", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Throttle Position", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x12: {"name": "Commanded secondary air status", "unit": "bitmask", "cluster": "Emissions", "dynamic": False, "decode": lambda data: data.hex()},
    0x13: {"name": "Oxygen sensors present (in 2 banks)", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x14: {"name": "O2 Sensor 1", "unit": "V", "cluster": "O2 Sensors", "dynamic": True, "group": "O2 Sensor Bank 1", "decode": lambda data: data[0] / 200 if len(data) >= 2 else None},
    0x15: {"name": "O2 Sensor 2", "unit": "V", "cluster": "O2 Sensors", "dynamic": True, "group": "O2 Sensor Bank 1", "decode": lambda data: data[0] / 200 if len(data) >= 2 else None},
    0x16: {"name": "O2 Sensor 3", "unit": "V", "cluster": "O2 Sensors", "dynamic": True, "group": "O2 Sensor Bank 2", "decode": lambda data: data[0] / 200 if len(data) >= 2 else None},
    0x17: {"name": "O2 Sensor 4", "unit": "V", "cluster": "O2 Sensors", "dynamic": True, "group": "O2 Sensor Bank 2", "decode": lambda data: data[0] / 200 if len(data) >= 2 else None},
    0x18: {"name": "O2 Sensor 5", "unit": "V", "cluster": "O2 Sensors", "dynamic": True, "group": "O2 Sensor Bank 3", "decode": lambda data: data[0] / 200 if len(data) >= 2 else None},
    0x19: {"name": "O2 Sensor 6", "unit": "V", "cluster": "O2 Sensors", "dynamic": True, "group": "O2 Sensor Bank 3", "decode": lambda data: data[0] / 200 if len(data) >= 2 else None},
    0x1A: {"name": "O2 Sensor 7", "unit": "V", "cluster": "O2 Sensors", "dynamic": True, "group": "O2 Sensor Bank 4", "decode": lambda data: data[0] / 200 if len(data) >= 2 else None},
    0x1B: {"name": "O2 Sensor 8", "unit": "V", "cluster": "O2 Sensors", "dynamic": True, "group": "O2 Sensor Bank 4", "decode": lambda data: data[0] / 200 if len(data) >= 2 else None},
    0x1C: {"name": "OBD standards this vehicle conforms to", "unit": "", "cluster": "Vehicle Info", "dynamic": False, "decode": lambda data: OBD_STANDARDS.get(data[0], f"Unknown ({data[0]})") if len(data) >= 1 else None},
    0x1D: {"name": "Oxygen sensors present (in 4 banks)", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x1E: {"name": "Auxiliary input status", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data[0] & 1 if len(data) >= 1 else None},
    0x1F: {"name": "Run time since engine start", "unit": "seconds", "cluster": "Vehicle Info", "dynamic": False, "decode": lambda data: (data[0] * 256) + data[1] if len(data) >= 2 else None},
    0x20: {"name": "PIDs supported [21 - 40]", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x21: {"name": "Distance traveled with MIL on", "unit": "km", "cluster": "Vehicle Info", "dynamic": False, "group": "MIL Time & Distance", "decode": lambda data: (data[0] * 256) + data[1] if len(data) >= 2 else None},
    0x22: {"name": "Fuel Rail Pressure (relative to manifold vacuum)", "unit": "kPa", "cluster": "Fuel System", "dynamic": True, "decode": lambda data: ((data[0] * 256) + data[1]) * 0.079 if len(data) >= 2 else None},
    0x23: {"name": "Fuel Rail Gauge Pressure", "unit": "kPa", "cluster": "Fuel System", "dynamic": True, "decode": lambda data: ((data[0] * 256) + data[1]) * 10 if len(data) >= 2 else None},
    0x24: {"name": "O2 Sensor 1 (Wideband) Eq. Ratio & Voltage", "unit": "", "cluster": "O2 Sensors", "dynamic": True, "decode": lambda data: f"{((data[0] * 256) + data[1]) / 32768:.3f} ratio, {((data[2] * 256) + data[3]) / 8192:.3f} V" if len(data) >= 4 else None},
    0x2C: {"name": "Commanded EGR", "unit": "%", "cluster": "Emissions", "dynamic": True, "group": "EGR", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x2D: {"name": "EGR Error", "unit": "%", "cluster": "Emissions", "dynamic": True, "group": "EGR", "min": -10, "max": 10, "decode": lambda data: (data[0] / 1.28) - 100 if len(data) >= 1 else None},
    0x2E: {"name": "Commanded evaporative purge", "unit": "%", "cluster": "Emissions", "dynamic": True, "group": "EVAP System", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x2F: {"name": "Fuel Tank Level Input", "unit": "%", "cluster": "Fuel System", "dynamic": True, "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x30: {"name": "Warm-ups since codes cleared", "unit": "count", "cluster": "Vehicle Info", "dynamic": False, "decode": lambda data: data[0] if len(data) >= 1 else None},
    0x31: {"name": "Distance traveled since codes cleared", "unit": "km", "cluster": "Vehicle Info", "dynamic": False, "group": "Cleared Time & Distance", "decode": lambda data: (data[0] * 256) + data[1] if len(data) >= 2 else None},
    0x32: {"name": "Evap. System Vapor Pressure", "unit": "Pa", "cluster": "Emissions", "dynamic": True, "group": "EVAP System", "decode": lambda data: ((data[0] * 256) + data[1]) / 4 if len(data) >= 2 else None},
    0x33: {"name": "Absolute Barometric Pressure", "unit": "kPa", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: data[0] if len(data) >= 1 else None},
    0x34: {"name": "O2 Sensor 1 (Wideband) Eq. Ratio & Current", "unit": "", "cluster": "O2 Sensors", "dynamic": True, "decode": lambda data: f"{((data[0] * 256) + data[1]) / 32768:.3f} ratio, {(((data[2] * 256) + data[3]) / 256) - 128:.3f} mA" if len(data) >= 4 else None},
    0x3C: {"name": "Catalyst Temperature: Bank 1, Sensor 1", "unit": "°C", "cluster": "Emissions", "dynamic": True, "group": "Catalyst Bank 1", "decode": lambda data: (((data[0] * 256) + data[1]) / 10) - 40 if len(data) >= 2 else None},
    0x3D: {"name": "Catalyst Temperature: Bank 2, Sensor 1", "unit": "°C", "cluster": "Emissions", "dynamic": True, "group": "Catalyst Bank 2", "decode": lambda data: (((data[0] * 256) + data[1]) / 10) - 40 if len(data) >= 2 else None},
    0x3E: {"name": "Catalyst Temperature: Bank 1, Sensor 2", "unit": "°C", "cluster": "Emissions", "dynamic": True, "group": "Catalyst Bank 1", "decode": lambda data: (((data[0] * 256) + data[1]) / 10) - 40 if len(data) >= 2 else None},
    0x3F: {"name": "Catalyst Temperature: Bank 2, Sensor 2", "unit": "°C", "cluster": "Emissions", "dynamic": True, "group": "Catalyst Bank 2", "decode": lambda data: (((data[0] * 256) + data[1]) / 10) - 40 if len(data) >= 2 else None},
    0x40: {"name": "PIDs supported [41 - 60]", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x41: {"name": "Monitor status this drive cycle", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x42: {"name": "Control module voltage", "unit": "V", "cluster": "System", "dynamic": True, "decode": lambda data: ((data[0] * 256) + data[1]) / 1000 if len(data) >= 2 else None},
    0x43: {"name": "Absolute load value", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Engine Load", "decode": lambda data: ((data[0] * 256) + data[1]) / 2.55 if len(data) >= 2 else None},
    0x44: {"name": "Commanded Equivalence Ratio", "unit": "ratio", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: ((data[0] * 256) + data[1]) / 32768 if len(data) >= 2 else None},
    0x45: {"name": "Relative throttle position", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Throttle Position", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x46: {"name": "Ambient air temperature", "unit": "°C", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: data[0] - 40 if len(data) >= 1 else None},
    0x47: {"name": "Absolute throttle position B", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Throttle Position", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x48: {"name": "Absolute throttle position C", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Throttle Position", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x49: {"name": "Accelerator pedal position D", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Accelerator Pedal", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x4A: {"name": "Accelerator pedal position E", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Accelerator Pedal", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x4B: {"name": "Accelerator pedal position F", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Accelerator Pedal", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x4C: {"name": "Commanded throttle actuator", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Throttle Position", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x4D: {"name": "Time run with MIL on", "unit": "minutes", "cluster": "Vehicle Info", "dynamic": False, "group": "MIL Time & Distance", "decode": lambda data: (data[0] * 256) + data[1] if len(data) >= 2 else None},
    0x4E: {"name": "Time since trouble codes cleared", "unit": "minutes", "cluster": "Vehicle Info", "dynamic": False, "group": "Cleared Time & Distance", "decode": lambda data: (data[0] * 256) + data[1] if len(data) >= 2 else None},
    0x51: {"name": "Fuel Type", "unit": "", "cluster": "Vehicle Info", "dynamic": False, "decode": lambda data: FUEL_TYPES.get(data[0], f"Unknown ({data[0]})") if len(data) >= 1 else None},
    0x52: {"name": "Ethanol fuel %", "unit": "%", "cluster": "Fuel System", "dynamic": False, "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x53: {"name": "Absolute Evap system Vapor Pressure", "unit": "kPa", "cluster": "Emissions", "dynamic": True, "group": "EVAP System", "decode": lambda data: (((data[0] * 256) + data[1]) / 200) if len(data) >= 2 else None},
    0x54: {"name": "Evap system vapor pressure", "unit": "Pa", "cluster": "Emissions", "dynamic": True, "group": "EVAP System", "decode": lambda data: (((data[0] * 256) + data[1]) - 32767) if len(data) >= 2 else None},
    0x59: {"name": "Fuel rail absolute pressure", "unit": "kPa", "cluster": "Fuel System", "dynamic": True, "decode": lambda data: (((data[0] * 256) + data[1]) * 10) if len(data) >= 2 else None},
    0x5A: {"name": "Relative accelerator pedal position", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Accelerator Pedal", "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x5B: {"name": "Hybrid battery pack remaining life", "unit": "%", "cluster": "Vehicle Info", "dynamic": False, "decode": lambda data: data[0] / 2.55 if len(data) >= 1 else None},
    0x5C: {"name": "Engine oil temperature", "unit": "°C", "cluster": "Engine Performance", "dynamic": True, "group": "Coolant & Oil Temperature", "decode": lambda data: data[0] - 40 if len(data) >= 1 else None},
    0x5D: {"name": "Fuel injection timing", "unit": "°", "cluster": "Fuel System", "dynamic": True, "decode": lambda data: (((data[0] * 256) + data[1]) / 128) - 210 if len(data) >= 2 else None},
    0x5E: {"name": "Engine fuel rate", "unit": "L/h", "cluster": "Fuel System", "dynamic": True, "decode": lambda data: ((data[0] * 256) + data[1]) / 20 if len(data) >= 2 else None},
    0x5F: {"name": "Emission requirements to which vehicle is designed", "unit": "enum", "cluster": "Vehicle Info", "dynamic": False, "decode": lambda data: data[0] if len(data) >= 1 else None},
    0x60: {"name": "PIDs supported [61 - 80]", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x61: {"name": "Driver's demand engine - percent torque", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Engine Torque", "decode": lambda data: data[0] - 125 if len(data) >= 1 else None},
    0x62: {"name": "Actual engine - percent torque", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "group": "Engine Torque", "decode": lambda data: data[0] - 125 if len(data) >= 1 else None},
    0x63: {"name": "Engine reference torque", "unit": "Nm", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: (data[0] * 256) + data[1] if len(data) >= 2 else None},
    0x64: {"name": "Engine percent torque data", "unit": "%", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: [d - 125 for d in data]},
    0x65: {"name": "Auxiliary input / output supported", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0x66: {"name": "Mass air flow sensor", "unit": "", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: data.hex()},
    0x67: {"name": "Engine coolant temperature 2", "unit": "°C", "cluster": "Engine Performance", "dynamic": True, "group": "Coolant & Oil Temperature", "min": 80, "max": 110, "decode": lambda data: data[1] - 40 if len(data) >= 2 else (data[0] - 40 if len(data) >= 1 else None)},
    0x68: {"name": "Intake air temperature sensor", "unit": "", "cluster": "Engine Performance", "dynamic": True, "decode": lambda data: data.hex()},
    0x80: {"name": "PIDs supported [81 - A0]", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0xA0: {"name": "PIDs supported [A1 - C0]", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
    0xC0: {"name": "PIDs supported [C1 - E0]", "unit": "bitmask", "cluster": "System", "dynamic": False, "decode": lambda data: data.hex()},
}

def decode_pid(pid, data):
    if pid in OBD2_PIDS:
        return OBD2_PIDS[pid]["decode"](data)
    return data.hex() if data else None

def get_pid_info(pid):
    entry = OBD2_PIDS.get(pid, {
        "name": f"Unknown PID 0x{pid:02X}", 
        "unit": "",
        "cluster": "Uncategorized",
        "dynamic": True
    }).copy()
    # Add defaults if not present
    if "group" not in entry:
        entry["group"] = entry["name"]
    return entry
