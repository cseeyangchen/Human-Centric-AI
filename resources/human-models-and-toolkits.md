<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>

# 🧑 Human Models and Toolkits

This page collects reusable human-specific models, libraries, and research toolkits. Unlike the paper index, entries here support recurring workflows across perception, reconstruction, identity and behavior analysis, motion processing, video understanding, rendering, and visualization.

> **Access note.** A public project page or source repository does not imply unrestricted use. Parametric body models, pretrained weights, datasets, and bundled assets may have terms that differ from the surrounding code. Always verify the current license on the official source before redistribution or commercial use.

## Contents

- [Parametric Human Models](#parametric-human-models)
- [Human Perception and Capture](#human-perception-and-capture)
- [Identity and Behavioral Analysis](#identity-and-behavioral-analysis)
- [Motion and Biomechanics](#motion-and-biomechanics)
- [Video and Activity Understanding](#video-and-activity-understanding)
- [Rendering and Visualization](#rendering-and-visualization)

## Parametric Human Models

| Resource | Scope | Primary Use | Access / License |
|:---|:---|:---|:---|
| [SMPL](https://smpl.is.tue.mpg.de/) | Articulated body shape and pose | Body fitting, reconstruction, animation, and motion representation | Registration required; model-specific terms |
| [SMPL-X](https://smpl-x.is.tue.mpg.de/) | Unified body, hands, and expressive face | Whole-body capture and expressive digital humans | Registration required; distinguish the SMPL-X Model and CC BY 4.0 SMPL-X Body terms |
| [MANO](https://mano.is.tue.mpg.de/) | Articulated hand shape and pose | Hand reconstruction, grasping, and hand-object interaction | Registration required; model-specific terms |
| [FLAME](https://flame.is.tue.mpg.de/) | Parametric head, jaw, neck, and expression | Face reconstruction, talking heads, and avatars | Registration required; model-specific terms |
| [STAR](https://star.is.tue.mpg.de/) | Sparse articulated human body model | Compact body modeling and SMPL-compatible pipelines | Registration required; model-specific terms |
| [SUPR](https://supr.is.tue.mpg.de/) | Part-based body representation | Full-body and body-part modeling | Registration required; model-specific terms |
| [SKEL](https://skel.is.tuebingen.mpg.de/) | Skin surface with a biomechanical skeleton | Anatomically grounded reconstruction and biomechanics | Registration required; model-specific terms |
| [MHR](https://github.com/facebookresearch/MHR) | Full-body rig with identity, pose, face, and multiple LODs | Real-time digital humans and CV/CG interoperability | Apache-2.0 code; verify downloaded asset terms |

## Human Perception and Capture

| Resource | Focus | Useful For | License / Access |
|:---|:---|:---|:---|
| [MMPose](https://github.com/open-mmlab/mmpose) · [Docs](https://mmpose.readthedocs.io/) | 2D/3D body, hand, face, and whole-body pose estimation | Training, inference, model comparison, and deployment | Apache-2.0 |
| [MMHuman3D](https://github.com/open-mmlab/mmhuman3d) · [Docs](https://mmhuman3d.readthedocs.io/) | Parametric 3D human models and unified HumanData conventions | Mesh recovery, dataset conversion, visualization, and benchmarking | Apache-2.0; body-model assets retain their own terms |
| [Sapiens](https://github.com/facebookresearch/sapiens) | Human-specific pretrained vision models | Pose, body-part segmentation, depth, and surface-normal estimation | CC BY-NC 4.0; non-commercial use |
| [Sapiens2](https://github.com/facebookresearch/sapiens2) | Multi-task human foundation models | Pose, segmentation, normals, pointmaps, and matting | Custom Sapiens2 license with use restrictions |
| [DensePose](https://github.com/facebookresearch/detectron2/tree/main/projects/DensePose) | Dense image-to-human-surface correspondence | Dense pose estimation, surface mapping, and body-region analysis | Apache-2.0 code; model and dataset terms may differ |
| [EasyMocap](https://github.com/zju3dv/EasyMocap) | Markerless monocular and multi-view motion capture | Camera calibration, annotation, SMPL-family fitting, and capture pipelines | Educational, research, and non-profit use; commercial use requires permission |
| [XRMoCap](https://github.com/openxrlab/xrmocap) | Multi-view, multi-person motion capture | 3D keypoints, association, triangulation, and SMPL fitting | Apache-2.0 code; dependency and model terms apply separately |
| [SMPLify-X](https://github.com/vchoutas/smplify-x) | Optimization-based expressive body fitting | Recovering SMPL-X bodies, hands, and faces from 2D evidence | Non-commercial scientific research license |
| [MediaPipe](https://github.com/google-ai-edge/mediapipe) · [Pose](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) · [Hand](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) · [Face](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) | Efficient body, hand, and face landmarks | On-device and real-time human sensing prototypes | Apache-2.0 code; individual models may have separate notices |
| [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) | Multi-person body, foot, face, and hand keypoints | Whole-body 2D pose extraction and legacy baselines | Free for non-commercial use under its custom license |
| [AlphaPose](https://github.com/MVIG-SJTU/AlphaPose) | Multi-person whole-body pose and tracking | Pose extraction from crowded images and videos | Academic/non-profit non-commercial research license |

## Identity and Behavioral Analysis

| Resource | Focus | Useful For | License / Access |
|:---|:---|:---|:---|
| [InsightFace](https://github.com/deepinsight/insightface) | Face recognition, detection, and alignment | Face analysis and identity-aware visual pipelines | MIT code; released training data and pretrained models are non-commercial research resources |
| [DeepFace](https://github.com/serengil/deepface) | Unified interface to face analysis models | Face verification, recognition, attributes, and model comparison | MIT wrapper; bundled model licenses apply separately |
| [FastReID](https://github.com/JDAI-CV/fast-reid) | Person and instance re-identification toolbox | Training, evaluation, and deployment of ReID models | Apache-2.0 |
| [Torchreid](https://github.com/KaiyangZhou/deep-person-reid) | Person ReID research library | Reproducible baselines, domain generalization, and cross-dataset evaluation | MIT |
| [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace) | Facial behavior analysis | Landmarks, head pose, gaze, and facial action units | Free for research use; commercial licensing available separately |
| [OpenGait](https://github.com/ShiqiYu/OpenGait) | Gait recognition framework and model zoo | Gait representation, training, evaluation, and benchmark comparison | Academic use only; commercial use prohibited |

## Motion and Biomechanics

| Resource | Focus | Useful For | License / Access |
|:---|:---|:---|:---|
| [OpenSim](https://github.com/opensim-org/opensim-core) | Musculoskeletal modeling and dynamic simulation | Biomechanics, movement analysis, rehabilitation, and physically grounded human modeling | Apache-2.0 |
| [smplx](https://github.com/vchoutas/smplx) | PyTorch implementation of SMPL-family models | Differentiable body-model layers and model-to-model transfer | Code license and downloaded model terms apply separately |
| [Human Body Prior](https://github.com/nghorbani/human_body_prior) | Learned priors for human pose and motion | VPoser-based fitting, latent pose modeling, and motion optimization | Check repository and model terms |

## Video and Activity Understanding

| Resource | Focus | Useful For | License / Access |
|:---|:---|:---|:---|
| [MMAction2](https://github.com/open-mmlab/mmaction2) · [Docs](https://mmaction2.readthedocs.io/) | Video and skeleton-based action understanding | Action recognition, localization, detection, and video retrieval | Apache-2.0 |
| [PyTorchVideo](https://github.com/facebookresearch/pytorchvideo) · [Tutorials](https://pytorchvideo.org/docs/tutorial_torchhub_inference) | Modular video-understanding library | Video models, transforms, data pipelines, acceleration, and inference tutorials | Apache-2.0 |

## Rendering and Visualization

| Resource | Focus | Useful For | License / Access |
|:---|:---|:---|:---|
| [PyTorch3D](https://github.com/facebookresearch/pytorch3d) | Differentiable 3D operators and rendering | Mesh losses, cameras, transforms, point clouds, and differentiable rendering | BSD-3-Clause-style license |
| [Kaolin](https://github.com/NVIDIAGameWorks/kaolin) | 3D deep-learning and neural rendering components | Mesh, point-cloud, voxel, neural-field, and differentiable graphics workflows | Apache-2.0 |
| [nvdiffrast](https://github.com/NVlabs/nvdiffrast) | High-performance differentiable rasterization | Geometry optimization, texture fitting, and neural rendering | NVIDIA source-code license |
| [gsplat](https://github.com/nerfstudio-project/gsplat) | CUDA-accelerated Gaussian splatting | Dynamic-human and avatar rendering pipelines based on 3D Gaussians | Apache-2.0 |
| [Nerfstudio](https://github.com/nerfstudio-project/nerfstudio) · [Docs](https://docs.nerf.studio/) | Modular neural radiance field framework | Capture, training, evaluation, visualization, and custom neural-rendering methods | Apache-2.0 |
| [Gaussian Splatting](https://github.com/graphdeco-inria/gaussian-splatting) | Reference implementation of 3D Gaussian splatting | Scene and avatar reconstruction, novel-view synthesis, and method comparison | Research and evaluation only under its custom license |
| [Open3D](https://github.com/isl-org/Open3D) | 3D data processing and visualization | Point clouds, meshes, registration, RGB-D processing, and interactive inspection | MIT |
| [Blender](https://www.blender.org/) · [Python API](https://docs.blender.org/api/current/) | Open 3D creation and rendering suite | Rigging, retargeting, animation, synthetic data, and publication-quality rendering | GPL; generated outputs are generally not covered by the GPL |

---

<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>
