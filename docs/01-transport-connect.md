# 01 · Transport — reaching the head unit (ENET / HSFZ / UDS)

Every capability rides on this. F-series BMWs (incl. the NBT EVO's host) speak **HSFZ** over
Ethernet, routed by the body gateway. This doc is the tested flow; the code is in
[`nbtevo/hsfz.py`](../nbtevo/hsfz.py) and [`nbtevo/uds.py`](../nbtevo/uds.py).

## Physical connection

The car's internal Ethernet is broken out onto specific pins of the **OBD-II port**, so you reach it
with an **OBD ENET cable**: a cable with a 16-pin **OBD-II connector** on one end and an **RJ45
(Ethernet) plug** on the other. Plug the OBD-II end into the car's OBD-II port (under the dash) and
the RJ45 end into your computer's Ethernet port — that puts your computer directly on the car's
diagnostic Ethernet segment. A plain ENET cable is a passive wiring adapter (no electronics, no
driver); any laptop or Raspberry Pi Ethernet port works.

> Not the same as a cheap "OBD-II to USB" ELM327/K-line dongle — those are the slow CAN tester
> interface, not Ethernet, and won't carry HSFZ. You want the OBD-II↔**RJ45** ENET cable.

- **Alternative — phone tethering**: the phone is the DHCP server and the car leases an address from
  it. (This is how the Android app does it, over Wi-Fi/USB tether instead of a cable.)

Either way you end up on a small Ethernet segment, usually **link-local `169.254.0.0/16`**, with the
car's gateway and the HU on it. With the cable, your computer self-assigns a `169.254.x.x` address
when nothing hands out DHCP (APIPA/link-local); if it doesn't, set a static `169.254.x.x` / `255.255.0.0`
on that interface. That address is the `bind_ip` you pass to discovery below.

## Step 1 — discovery (who's on the wire)

Broadcast an HSFZ **ident** request and read the replies:

```
UDP → <broadcast>:6811   payload = 00 00 00 00 00 11      (u32 len=0, u16 ctrl=0x0011)
```

Bind your socket to your host's address on the ENET segment so the probe egresses that interface.
Each reply's **source IP** is an endpoint; its payload (after the 6-byte header) is a latin-1
ident string with `DIAGADR<nn>` (the endpoint's diag address, hex), `BMWMAC<..>`, `BMWVIN<..>`.

You will typically see:

| Ident begins | Role | Use it for |
|---|---|---|
| `DIAGADR10…` | **FEM gateway** — routes to the whole car | whole-vehicle work; any module by target byte |
| (HU edge) | the **HU's own** HSFZ endpoint — serves `0x63` only | faster HU-only coding/flash |

Discovery structurally returns the gateway (the HU edge doesn't answer the ident broadcast), so the
old "which IP?" footgun is gone — take the `DIAGADR10` responder's IP as your gateway.

```python
from nbtevo.hsfz import discover
for ep in discover(bind_ip="169.254.199.50"):
    print(ep.ip, ep.diag_addr, ep.vin, ep.raw_ident)
```

## Step 2 — session (HSFZ over TCP 6801)

```
TCP → <gatewayIP>:6801
frame = u32 length · u16 ctrl · u8 src · u8 tgt · <uds…>
  length = 2 + len(uds)        # counts the bytes after the control word
  ctrl   = 0x0001 data · 0x0002 ack (drop it) · 0x0011 ident
  src    = 0xF4 (tester)
  tgt    = ECU address
```

Routing is the **target byte alone** — one socket to the gateway reaches every module; no
routing-activation handshake (that's DoIP, which these cars don't use). Handle `7F xx 78`
(responsePending) by re-arming the P2\* timer. `nbtevo.hsfz.HsfzClient.request()` does all of this.

**Addresses:** tester `0xF4` · functional `0xDF` · FEM gateway `0x10` · **NBT EVO head unit `0x63`**.

## Step 3 — UDS

Read the head unit's identity in the **default session, no SecurityAccess**:

```python
from nbtevo.hsfz import HsfzClient, TGT_HU
from nbtevo.uds import Uds

with HsfzClient("169.254.104.13") as c:   # the DIAGADR10 gateway IP from discovery
    hu = Uds(c, TGT_HU)
    print("VIN :", hu.read_vin())          # 22 F1 90
    svk = hu.read_svk()                     # 22 F1 01
    print("BTLD:", svk.bootloader)          # e.g. BTLD-00001FFD-007.051.002
    print("CAFD:", hu.read_live_cafd())     # 22 30 0F, else SVK CAFD entry
```

- **VIN** `22 F1 90` — latin-1, strip NUL/space. This is your safety anchor: a write tool checks it
  against the VIN you declared you own.
- **SVK** `22 F1 01` — the software-version table; decode gives BTLD / CAFD / SWFL / FLSL ids.
- **Module's own IP** `22 17 2A` → `ver | ip4 | mask4 | gw4`. The HU's **diagnostic** Ethernet
  endpoint. (Note the HU has a *second*, separate IP for its QNX dev/SSH interface, which `22 17
  2A` does **not** report — that's a `qnx_dev` concern, not a coding one.)

### Faster HU-only route

For coding/flash work that only touches the HU, connecting straight to the HU's own Ethernet node
(the IP from `22 17 2A`), target `0x63`, avoids the gateway's store-and-forward hop and is markedly
faster — it even answers in the bootloader across a programming-mode reboot. Use the gateway route
as the compatible fallback.

## Whole-car reads (handy for orientation)

- **Module list in one probe**: functional TesterPresent `3E 00` to `0xDF` — every awake ECU
  replies `7E` from its own source address.
- **Per-ECU DTCs**: `19 02 FF` to each address (default session, no SecurityAccess). No aggregate
  "all faults" service exists; address each ECU individually.

## Sessions and SecurityAccess (preview)

Reads are default-session. Coding **writes** need the coding session and SecurityAccess:
`10 03` → `10 41` → `27 01`/`27 02`. The detail, including which key, is in
`capabilities/coding/03-write-flow.md`.
