#!/usr/bin/env python3
"""EasyEDA AI Bridge - Capability Exploration Script (using curl)"""
import subprocess
import json
import time
import sys

BASE = "https://easyeda-ai-bridge.findata-be.uk"
SESSION = "sess_4d4123ed"

def execute(code, timeout=25):
    """Execute JS code in EasyEDA and return result via curl."""
    payload = json.dumps({"code": code})
    cmd = ["curl", "-s", "--max-time", str(timeout),
           "-X", "POST", f"{BASE}/execute",
           "-H", f"X-Session-Id: {SESSION}",
           "-H", "Content-Type: application/json",
           "-d", payload]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    if result.returncode == 28:
        return {"error": "timeout", "result": None}
    try:
        return json.loads(result.stdout)
    except:
        return {"error": f"parse_error: {result.stdout[:100]}", "result": None}

def search_get_uuids(keyword):
    """Search library and extract UUIDs from first result."""
    code = f"""eda.lib_Symbol.search("{keyword}").then(function(r){{if(!r||!r.length)return"empty";var s=r[0];return JSON.stringify({{name:s.getState_Name(),libUuid:s.getState_LibraryUuid(),uuid:s.getState_Uuid()}});}})"""
    return execute(code)

print("=" * 60)
print("EasyEDA AI Bridge - Capability Exploration")
print("=" * 60)

# 1. Library Search
print("\n--- 1. Library Search ---")
searches = {}
for kw in ["Resistor", "LED", "NE555", "Capacitor", "STM32F103C8T6", "Connector"]:
    result = search_get_uuids(kw)
    data = result.get("result", result.get("error", "?"))
    print(f"  {kw}: {data}")
    if result.get("result") and result["result"] != "empty":
        try:
            searches[kw] = json.loads(result["result"])
        except:
            searches[kw] = result["result"]
    time.sleep(1)

# 2. System APIs
print("\n--- 2. System APIs ---")

r = execute('eda.sys_ToastMessage.showMessage("AI Bridge Test OK", 2).then(function(){return"ok"})')
print(f"  Toast: {r.get('result', r.get('error'))}")

time.sleep(0.5)

r = execute('(function(){eda.sys_Storage.setExtensionUserConfig("br_test","hello");return eda.sys_Storage.getExtensionUserConfig("br_test");})()')
print(f"  Storage: {r.get('result', r.get('error'))}")

time.sleep(0.5)

r = execute('eda.sys_I18n.text("File")')
print(f"  I18n('File'): {r.get('result', r.get('error'))}")

# 3. Schematic state
print("\n--- 3. Schematic State ---")

r = execute('eda.sch_PrimitiveComponent.getAllPrimitiveId().then(function(ids){return "components: "+(ids?ids.length:0)})')
print(f"  Components: {r.get('result', r.get('error'))}")

time.sleep(0.5)

r = execute('eda.sch_PrimitiveWire.getAll(true).then(function(w){return "wires: "+(w?w.length:0)})')
print(f"  Wires: {r.get('result', r.get('error'))}")

time.sleep(0.5)

r = execute('eda.sch_PrimitiveText.getAll(true).then(function(t){return "texts: "+(t?t.length:0)})')
print(f"  Texts: {r.get('result', r.get('error'))}")

# 4. PCB state
print("\n--- 4. PCB State ---")

r = execute('eda.pcb_PrimitiveComponent.getAll().then(function(c){return "pcb comps: "+(c?c.length:0)})')
print(f"  PCB Components: {r.get('result', r.get('error'))}")

time.sleep(0.5)

r = execute('eda.pcb_PrimitivePad.getAll().then(function(p){return "pads: "+(p?p.length:0)})')
print(f"  PCB Pads: {r.get('result', r.get('error'))}")

# 5. More method discovery
print("\n--- 5. Additional Method Discovery ---")

# Check what methods exist on sch_PrimitiveComponent (via prototype)
r = execute('(function(){var p=Object.getPrototypeOf(eda.sch_PrimitiveComponent);var ms=[];for(var k in p){if(typeof p[k]==="function"&&k!=="constructor")ms.push(k)};return JSON.stringify(ms.slice(0,30));})()')
print(f"  sch_PrimitiveComponent methods: {r.get('result', r.get('error'))}")

time.sleep(0.5)

r = execute('(function(){var p=Object.getPrototypeOf(eda.sch_PrimitiveWire);var ms=[];for(var k in p){if(typeof p[k]==="function"&&k!=="constructor")ms.push(k)};return JSON.stringify(ms.slice(0,20));})()')
print(f"  sch_PrimitiveWire methods: {r.get('result', r.get('error'))}")

time.sleep(0.5)

# 6. Try interactive placement
print("\n--- 6. Interactive Component Placement Test ---")
if "Resistor" in searches and isinstance(searches["Resistor"], dict):
    r_data = searches["Resistor"]
    code = f"""eda.sch_PrimitiveComponent.placeComponentWithMouse({{uuid:"{r_data['uuid']}",libraryUuid:"{r_data['libUuid']}"}}).then(function(){{return"placed"}}).catch(function(e){{return"err:"+e.message}})"""
    r = execute(code)
    print(f"  Place Resistor ({r_data['name']}): {r.get('result', r.get('error'))}")
else:
    print(f"  Skipped - no resistor data")

print("\n" + "=" * 60)
print("Phase 1 exploration complete!")
print("=" * 60)

# Save results for documentation
with open("/Users/finn/Projects/eda_bridge_results.json", "w") as f:
    json.dump({"searches": {k: v for k, v in searches.items() if isinstance(v, dict)}}, f, indent=2)
print("\nResults saved to eda_bridge_results.json")
