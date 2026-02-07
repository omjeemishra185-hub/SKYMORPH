SkyMorph is a ready-to-plug intelligent GNSS switching system designed to ensure uninterrupted and reliable navigation for drones and autonomous robotic platforms operating in GNSS-degraded, jammed, or spoofed environments 🛰️⚠️.

The system continuously monitors real-time GNSS signal integrity and automatically switches from GPS to India’s indigenous NavIC constellation within 100 ms ⏱️, maintaining meter-level positional accuracy even during active interference events.

Unlike conventional multi-GNSS receivers that demand firmware modifications or complex reconfiguration, SkyMorph offers a true plug-and-play architecture 🔌. By dynamically modifying the NMEA sentence prefix, it enables seamless compatibility with existing autopilot systems without any firmware changes, making deployment fast, safe, and scalable.

Key Features

🔁 Automatic GPS → NavIC switching within 100 ms

🛡️ Intelligent jamming & spoofing detection engine

📍 Meter-level positioning accuracy during signal loss

🔄 Dynamic NMEA prefix modification for universal autopilot compatibility

🔌 No autopilot firmware changes required (true plug-and-play)

🧠 STM32-based custom PCB

🪶 Compact, lightweight & low-power design

📊 MATLAB-validated simulations and performance analysis

🧩 System Architecture
🛠️ Hardware Layer

Microcontroller: STM32-based custom embedded platform

GNSS Inputs: GPS + NavIC dual-constellation support

Interfaces: UART-based standard NMEA input/output

Power: Optimized for drones and autonomous robots

🧠 Software & Intelligence Layer

Real-time GNSS signal quality monitoring (C/N₀, amplitude, stability)

Jamming and spoofing detection logic

Autonomous constellation switching mechanism

Dynamic NMEA sentence restructuring for seamless autopilot integration

🧪 Validation & Testing

MATLAB-based simulation and analysis framework

Evaluation of:

📉 Signal amplitude variation under jamming

📡 Carrier-to-Noise ratio (C/N₀) degradation

📍 Positioning error growth over time

🛸 Drone trajectory deviation during interference

🎯 Applications

🚑 Medical & emergency drone deliveries

🌪️ Disaster relief and search-and-rescue missions

🛡️ Defence and strategic navigation systems

🤖 Autonomous robots in GNSS-challenged environments
