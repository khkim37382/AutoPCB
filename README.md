🧠 AutoPCB Generator
AI-Assisted PCB Generation for KiCad
AutoPCB Generator is a command-line tool that converts natural language prompts or structured YAML specifications into production-ready KiCad PCB projects.
The goal is to bridge high-level hardware intent (“3.3V I2C breakout with pull-ups”) to schematic capture, component selection, and board layout automatically.

🚀 Features

📝 Natural language → PCB spec generation

📐 YAML-based structured hardware specification

🔌 Automatic schematic generation

🧭 Net assignment and I2C/SPI power routing support

⚡ Decoupling capacitor auto-placement

🔄 Pull-up resistor insertion for I2C

📦 KiCad project export (ready to open)

🤖 Optional AI-assisted spec generation

🛠 Tech Stack
Python 3.10+
KiCad 7/8
OpenAI API (optional for AI prompt mode)
pcbgen CLI framework
📦 Installation
Clone the repository:
git clone https://github.com/YOUR_USERNAME/autopcb-generator.git
cd autopcb-generator
Create a virtual environment:
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
Install dependencies:
pip install -r requirements.txt
🧪 Basic Usage
1️⃣ AI Prompt Mode
Generate a board from natural language:
python3 -m pcbgen.cli \
  --prompt "Make a 3.3V I2C breakout with 4-pin header, 4.7k pullups, 100n + 1u decoupling" \
  --out out/TestBoard \
  --ai
This will:
Convert your prompt into a hardware spec
Generate schematic
Create KiCad project files
2️⃣ YAML Spec Mode (Deterministic)
Create a YAML file:
name: I2C_Breakout
voltage: 3.3

components:
  - type: header
    pins: 4
    labels: [VCC, GND, SDA, SCL]

  - type: pullup
    value: 4.7k
    nets: [SDA, SCL]

  - type: capacitor
    value: 100nF
    net: VCC

  - type: capacitor
    value: 1uF
    net: VCC
Then run:
python3 -m pcbgen.cli --spec myboard.yaml --out out/MyBoard
📁 Output Structure
out/
 └── MyBoard/
      ├── MyBoard.kicad_pro
      ├── MyBoard.kicad_sch
      ├── MyBoard.kicad_pcb
      └── fabrication/
Open the .kicad_pro file directly in KiCad.
🧩 How It Works
Prompt → Parsed into structured board specification
Spec → Component list + net mapping
Schematic auto-generated
Nets assigned + power domains created
Board file generated
Exported to KiCad project
AI mode only affects spec generation — PCB generation itself remains deterministic.
🧠 Design Philosophy
AutoPCB is not meant to replace hardware engineers.
It accelerates:
Rapid prototyping
Educational PCB design
Repetitive breakout boards
Standard embedded subsystems
The engineer still:
Reviews routing
Verifies signal integrity
Approves footprint assignments
Performs final DRC/ERC checks
⚠️ Limitations
Does not currently optimize high-speed traces
No impedance control automation (yet)
No differential pair auto-routing
Limited component library mapping
AI prompt quality affects spec quality
🔮 Roadmap
 Differential pair support
 Power plane auto-generation
 Constraint-driven routing
 Local LLM integration (LM Studio)
 Parametric footprint selection
 4-layer stackup support
 Auto ERC/DRC verification pass
