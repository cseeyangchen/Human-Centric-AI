<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>

# 🧪 Simulation and Evaluation

This page collects infrastructure for building, training, and evaluating human-aware virtual agents, humanoids, and interactive AI systems. The emphasis is on platforms that expose humans, avatars, human demonstrations, social interaction, or articulated embodiment as first-class research components.

> **Platform note.** Simulator choice depends on the required embodiment, physics fidelity, visual realism, interaction model, hardware, and evaluation protocol. The entries below are complementary rather than interchangeable.

## Contents

- [Human-Aware Environments](#human-aware-environments)
- [Physics and Humanoid Learning](#physics-and-humanoid-learning)
- [Data, Annotation, and Model Analysis](#data-annotation-and-model-analysis)
- [Experiment and Artifact Infrastructure](#experiment-and-artifact-infrastructure)

## Human-Aware Environments

| Platform | Human-Centric Capability | Typical Tasks | Access |
|:---|:---|:---|:---|
| [Habitat 3.0](https://aihabitat.org/habitat3/) | Simulated humanoids, avatar diversity, human-in-the-loop interfaces, and human-robot collaboration | Social navigation, collaborative rearrangement, and embodied interaction | [Habitat-Lab](https://github.com/facebookresearch/habitat-lab), MIT |
| [BEHAVIOR and OmniGibson](https://behavior.stanford.edu/) | Interactive household scenes, realistic object states, and long-horizon daily activities | Household assistance, mobile manipulation, and activity planning | [Repository](https://github.com/StanfordVL/BEHAVIOR-1K); check platform and asset terms |
| [iGibson](https://svl.stanford.edu/igibson/) | Interactive indoor scenes with human demonstrations and social navigation support | Navigation, manipulation, human-aware planning, and sim-to-real research | Open-source platform; check dataset terms |
| [VirtualHome](https://virtual-home.org/) | Programs and simulations of human activities in household environments | Activity reasoning, program generation, planning, and multi-agent interaction | [Repository](https://github.com/xavierpuigf/virtualhome), non-commercial research terms apply to some assets |
| [AI2-THOR](https://ai2thor.allenai.org/) | Interactive household environments and embodied agents | Visual navigation, object interaction, task planning, and language grounding | [Repository](https://github.com/allenai/ai2thor), Apache-2.0 code |

## Physics and Humanoid Learning

| Platform | Strength | Human-Centric Use | Access |
|:---|:---|:---|:---|
| [Isaac Lab](https://isaac-sim.github.io/IsaacLab/) | GPU-accelerated simulation, sensors, RL/IL environments, and scalable training | Humanoid locomotion, whole-body control, imitation learning, and sim-to-real | [Repository](https://github.com/isaac-sim/IsaacLab), BSD-3-Clause; Isaac Sim terms also apply |
| [MuJoCo](https://mujoco.org/) | Fast articulated-body physics and mature control interfaces | Humanoid control, motion imitation, biomechanics, and reinforcement learning | [Repository](https://github.com/google-deepmind/mujoco), Apache-2.0 |
| [ManiSkill](https://maniskill.readthedocs.io/) | GPU-parallel simulation, rendering, demonstrations, and robot-learning baselines | Humanoid and mobile manipulation, imitation learning, RL, and VLA evaluation | [Repository](https://github.com/mani-skill/ManiSkill), Apache-2.0 |
| [SAPIEN](https://sapien.ucsd.edu/) | Articulated-object simulation, rendering, and robot-learning interfaces | Human-object environments, manipulation, synthetic data, and task construction | [Repository](https://github.com/haosulab/SAPIEN); check current terms |
| [OpenSim](https://opensim.stanford.edu/) | Musculoskeletal dynamics and biomechanics | Human movement simulation, rehabilitation, exoskeletons, and physically grounded motion | [Repository](https://github.com/opensim-org/opensim-core), Apache-2.0 |

## Data, Annotation, and Model Analysis

| Resource | Function | Human-Centric Use | Access |
|:---|:---|:---|:---|
| [CVAT](https://www.cvat.ai/) | Image, video, and point-cloud annotation | Keypoints, skeletons, tracks, masks, attributes, and COCO Keypoints export | [Repository](https://github.com/cvat-ai/cvat), MIT |
| [FiftyOne](https://github.com/voxel51/fiftyone) | Dataset curation, visualization, and model analysis | Inspecting human annotations, errors, embeddings, duplicates, and evaluation slices | Open-source core; Apache-2.0 |
| [Label Studio](https://labelstud.io/) | Configurable multimodal data labeling | Images, video, audio, text, keypoints, and human feedback collection | [Repository](https://github.com/HumanSignal/label-studio), Apache-2.0 |
| [MMEval](https://github.com/open-mmlab/mmeval) | Unified metric interfaces for ML libraries | Reusable evaluation components for perception and generation pipelines | Apache-2.0 |
| [FiftyOne Model Evaluation](https://docs.voxel51.com/user_guide/evaluation.html) | Interactive analysis of predictions and ground truth | Per-class, per-sample, and failure-mode inspection beyond aggregate scores | Part of FiftyOne |

## Experiment and Artifact Infrastructure

| Resource | Function | Recommended Use | Access |
|:---|:---|:---|:---|
| [Hugging Face Hub](https://huggingface.co/) | Hosting and discovery for models, datasets, demos, and collections | Building a maintained Human-Centric AI collection with model and dataset cards | Public hub with per-resource licenses |
| [Weights & Biases](https://wandb.ai/) | Experiment tracking, artifact management, reports, and sweeps | Comparing human-centric models and sharing benchmark runs | Hosted service; client library is open source |
| [MLflow](https://mlflow.org/) | Open-source experiment and model lifecycle management | Logging parameters, metrics, checkpoints, and evaluation artifacts | Apache-2.0 |
| [DVC](https://dvc.org/) | Data and pipeline versioning | Reproducible preprocessing, dataset versions, and experiment dependencies | Apache-2.0 |
| [EvalAI](https://eval.ai/) | Hosted challenge evaluation | Private test labels, submission queues, and public leaderboards | Open-source platform and hosted service |
| [CodaBench](https://www.codabench.org/) | Reproducible competitions and benchmarks | Packaging ingestion/scoring programs and maintaining challenge leaderboards | Open platform; challenge-specific terms apply |

---

<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>
