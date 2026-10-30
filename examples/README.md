# Worked examples

End-to-end recipes that combine capabilities. Each one names the **exact** set of changes for a
real outcome on **your own** car, and points back at the capability docs for the mechanism.

| Example | What it activates | Capabilities combined |
|---|---|---|
| **[carplay.md](carplay.md)** | Apple CarPlay — the CarPlay **FSC** (`0x0143`) + the coding bit the firmware checks (`CARPLAY_SWT`) | [`fsc`](../capabilities/fsc/) + [`coding`](../capabilities/coding/) |
| **[vehicle_models/examples/blueprint/](../capabilities/vehicle_models/examples/blueprint/)** | A custom 3D car wiring up *every* feature — original geometry, materials, spinning wheels, roll-in, a Sin/Cos idle animation, a door, switchable lamps | [`vehicle_models`](../capabilities/vehicle_models/) (authoring layer) |

> Same rules as everywhere in this repo: your own titled vehicle, local access only, no defeating
> safety/theft/emissions controls. Enabling a feature you don't hold a BMW licence for is between
> you and BMW. See [../LEGAL.md](../LEGAL.md).
