# Backscatter-Based Multi-Tag Communication: Hardware and Simulation

This repository collects the design files and simulation materials for our internship project on backscatter-based communication and multiple-access techniques.

## Project at a glance

The work is organised into four related workstreams:

1. **RF tag and controller hardware** — KiCad schematics and PCB layouts.
2. **Electromagnetic analysis** — CST model and RCS study of ON/OFF loading conditions.
3. **Signal-level communication model** — GNU Radio flowgraph for three-tag signal generation and receiver processing.
4. **Packet-level random access study** — Python simulation comparing FSA, CRDSA with SIC, and IRSA with/without SIC.

> **Scope note:** The GNU Radio three-tag receiver model and the Python packet-level IRSA/SIC simulation are separate studies in this repository. Do not interpret them as a single integrated implementation. The PCB designs are design files; fabrication and physical validation should only be claimed if separately completed and documented.

## Repository map

```text
backscatter_github_project/
├── README.md
├── .gitignore
├── docs/
│   ├── presentation/       # Project presentation
│   └── reports/            # Report copy; confirm final/public version
├── gnuradio/
│   ├── flowgraphs/         # GNU Radio Companion (.grc) files
│   └── README.md
├── hardware/
│   ├── kicad/
│   │   ├── tag_pcb/        # RF tag schematic, PCB and project
│   │   └── esp32_controller/ # ESP32 controller schematic, PCB and project
│   └── manufacturing/     # ODB++ and Gerber manufacturing exports
├── cst/
│   ├── model/              # CST Studio Suite project
│   └── README.md
├── python/
│   └── irsa_sic/           # Packet-level random-access simulation
├── results/
│   ├── plots/              # Exported figures (add generated plots here)
│   └── data/               # Numeric result files (CSV, etc.)
└── scripts/                # Utility scripts, if needed
```

## Getting started

### GNU Radio

Open `gnuradio/flowgraphs/BC_NBits_MultiTag_3Rx.grc` with a compatible GNU Radio Companion installation. Review the block parameters and required GNU Radio modules before running it. See [`gnuradio/README.md`](gnuradio/README.md).

### Python IRSA/SIC comparison

Requirements:

```bash
python -m pip install numpy matplotlib
```

Run:

```bash
cd python/irsa_sic
python irsa_sic_comparison.py
```

The script compares IRSA with SIC, CRDSA with SIC, Frame-Slotted ALOHA and IRSA without SIC. Its packet-level collision model uses ideal SIC; it does not model RF waveforms, capture, fading or imperfect cancellation. Results from a new run may differ from the values shown in the presentation.

### KiCad

Open each `.kicad_pro` file in KiCad. Keep the associated schematic, PCB, project tables and custom library files together. Manufacturing archives are exports and are not replacements for the editable KiCad source files.

### CST Studio Suite

Open `cst/model/Tag_short.cst` in a compatible CST Studio Suite version. CST is proprietary software and is not included in this repository.

## Results and reproducibility

Place figures in `results/plots/` and raw numeric outputs in `results/data/`. Include the script or flowgraph settings used to generate each result. Clearly label simulated results and distinguish them from measured hardware results.

## Before publishing publicly

- Confirm that all contributors and supervisors approve public release.
- Check reports and slides for student IDs, private contact details, signatures and material that cannot be redistributed.
- Confirm that the report copy is the approved version for public release.
- Check third-party libraries, symbols, footprints and reference figures for redistribution terms.
- Choose a repository licence only after all contributors agree. Do not leave a placeholder copyright owner in a licence file.
- Avoid uploading credentials, API keys, private messages or personal data.

## Acknowledgement

Add the final agreed acknowledgement wording here after confirming the preferred names, titles and institutional wording with the project team and guides.
