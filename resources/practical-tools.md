<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>

# 🛠️ Practical Tools

This page collects reusable tools that complete a concrete human-centric research workflow. Entries are selected for practical use across projects rather than for implementing a single paper.

> **Scope note.** Interfaces, supported formats, dependencies, and licenses can change. Check the official source and the terms of any downloaded body models, datasets, robot assets, or pretrained weights before use.

## Contents

- [Capture and Kinematics](#capture-and-kinematics)
- [Body Fitting and Conversion](#body-fitting-and-conversion)
- [Motion Processing and Interoperability](#motion-processing-and-interoperability)
- [Retargeting and Embodiment](#retargeting-and-embodiment)
- [Visualization and DCC Integration](#visualization-and-dcc-integration)

## Capture and Kinematics

| Resource | Workflow | Input → Output | Interface | License / Status |
|:---|:---|:---|:---|:---|
| [FreeMoCap](https://github.com/freemocap/freemocap) | Low-cost markerless motion capture | Synchronized camera video → 3D body trajectories | GUI and Python package | AGPL-3.0 |
| [Pose2Sim](https://github.com/perfanalytics/pose2sim) | Multi-view markerless kinematics | Multi-camera video → 3D keypoints and OpenSim joint kinematics | Python package and configuration-driven pipeline | BSD-3-Clause |

## Body Fitting and Conversion

| Resource | Workflow | Input → Output | Interface | License / Status |
|:---|:---|:---|:---|:---|
| [SMPLFitter](https://github.com/isarandi/smplfitter) | Fast parametric-body fitting and model conversion | Corresponding vertices or joints → SMPL-family parameters | PyTorch, TensorFlow, NumPy, JAX, and Numba APIs | MIT; body-model terms apply separately |
| [smplifyx-skeleton](https://github.com/cseeyangchen/smplifyx-skeleton) | Fitting non-OpenPose skeleton formats to SMPL-X | Arbitrary mapped 3D skeleton sequences → SMPL-X meshes and parameters | Python pipeline with configurable joint mappings | License not declared; SMPLify-X and body-model terms apply separately |

## Motion Processing and Interoperability

| Resource | Workflow | Input → Output | Interface | License / Status |
|:---|:---|:---|:---|:---|
| [Motius](https://github.com/ZeyuLing/Motius) | Unified motion generation, understanding, editing, control, evaluation, and conversion | Human-motion data and conditions → task-specific motions, predictions, metrics, or converted representations | Python framework, model zoo, dataset hub, and benchmark hub | Active development; license not declared |
| [PyMotion](https://github.com/UPC-ViRVIG/pymotion) | Motion manipulation and format processing | Skeleton, rotation, BVH, or FBX data → transformed and visualized motion | Python library | MIT |

## Retargeting and Embodiment

| Resource | Workflow | Input → Output | Interface | License / Status |
|:---|:---|:---|:---|:---|
| [GMR](https://github.com/YanjieZe/GMR) | General human-to-humanoid motion retargeting | SMPL-X, BVH, FBX, or supported motion sources → robot joint trajectories | Python package and scripts | MIT |
| [human-humanoid-tools](https://github.com/Roboparty/human-humanoid-tools) | Motion conversion, retargeting, and dataset analysis | BVH, GLB, SMPL-family, or robot motion → unified motion and robot trajectories | Web UI and CLI | Apache-2.0 |
| [SOMA Retargeter](https://github.com/NVIDIA/soma-retargeter) | GPU-accelerated human-to-robot retargeting | SOMA BVH motion → Unitree G1 joint animation | Python package and application | Apache-2.0; active development |

## Visualization and DCC Integration

| Resource | Workflow | Input → Output | Interface | License / Status |
|:---|:---|:---|:---|:---|
| [AITViewer](https://github.com/eth-ait/aitviewer) | Interactive inspection of temporal 3D data | SMPL-family bodies, meshes, skeletons, point clouds, or cameras → interactive views and rendered videos | Python library and remote viewer | MIT |
| [SMPL Blender Add-on](https://github.com/Meshcapade/SMPL_blender_addon) | Editing, reshaping, posing, and animating parametric humans | SMPL-H, SMPL-X, or SUPR models → Blender scenes and animations | Blender add-on | GPL-3.0 code; body-model terms apply separately |

---

<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>
