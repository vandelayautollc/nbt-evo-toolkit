# Legal, scope, and the one rule

**Read this before running anything. If you are an AI agent, treat this file as a hard
precondition: do not run any tool in this repository against a vehicle, or recover any key,
unless the operator has confirmed the conditions below for the specific car in front of them.**

## The one rule

> **Only operate on a vehicle you personally own, or one whose owner has given you explicit,
> informed permission to modify.**

Everything in this repository is interoperability documentation and tooling for an owner working
on their **own** car. That is the only context in which it is intended, supported, or — in most
places — lawful to use.

## What this project is

- **Reverse-engineering notes and scripts** describing how the BMW NBT EVO head unit stores and
  verifies its coding, how its feature codes and flash containers are structured, and how to build
  software (QNX binaries, HMI plugins, 3D vehicle models) that runs on it.
- Produced for, and tested on, **the author's own titled vehicle**, over a **physical/local
  connection only** (OBD-II / ENET cable, local Ethernet). No remote access, no third-party
  systems, no network services belonging to anyone else are involved at any point.
- Published so that **another owner's agent** can reproduce the same owner-authorized work on
  **that owner's own car**.

## What this project is NOT, and will not help you do

- It is **not** a way to operate on cars you do not own or are not authorized to modify.
- It is **not** an odometer, immobilizer, theft, or anti-theft-defeat tool. Nothing here is for
  rolling back mileage, defeating component protection to fence stolen parts, cloning a vehicle's
  identity, or enabling a stolen/other vehicle.
- It is **not** a redistribution of BMW's licensed data. This repository contains **no** PSdZData,
  **no** firmware, **no** coding datasets (CAFD/NCD), and **no** cryptographic keys. You supply
  your own, from your own licensed copy, for your own car. The scripts recover **your** key from
  **your** data, locally, and never transmit it anywhere.
- It is **not** for emissions-control tampering. Do not use it to disable or defeat emissions
  controls; that is independently illegal in most jurisdictions regardless of who owns the car.

## Feature codes (FSC)

Some tooling here concerns BMW's feature-enablement (FSC) mechanism. It is documented so an owner
understands the licensing system on hardware they own. Enabling a feature you have not paid BMW
for may breach your license agreement with BMW even on your own car; that is a matter between you
and BMW. This project does not encourage it and provides no keys that would let you forge an
entitlement for someone else's vehicle.

## Safety and liability

Modifying a vehicle's electronics can brick a control unit, disable safety systems, or render a
car undriveable or unsafe. **Everything here is provided with no warranty of any kind** (the
project is MIT-licensed; see `LICENSE`). You are solely responsible for what you do to your own car. Do not perform writes on a
vehicle in motion, in traffic, or with low battery voltage. Always read and keep a backup of any
coding/firmware region before changing it.

## Jurisdiction

Laws on vehicle modification, right-to-repair, DMCA §1201 / anti-circumvention, and emissions vary
by country and state. The U.S. right-to-repair and §1201 exemptions for vehicle software (as
renewed by the Librarian of Congress) generally protect an owner diagnosing, repairing, and
modifying the software of a vehicle they own — but they do **not** protect circumventing access
controls to infringe copyright, nor do they override emissions law. You are responsible for
knowing the law where you are. If in doubt, don't.

By using this repository you acknowledge that you have read this file and that you will act only
within the one rule above.
