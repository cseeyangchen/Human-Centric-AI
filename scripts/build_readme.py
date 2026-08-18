#!/usr/bin/env python3
"""Build the Human-Centric AI Resources Markdown pages from curated sources.

The script combines survey citations and tables with verified post-survey method
updates, while retaining the manuscript as the source of truth for its contents.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
from collections import OrderedDict
from datetime import date
from pathlib import Path
from typing import Iterable


# Set this after the survey is publicly available on arXiv. The badge is
# rendered without a link while the value is empty.
SURVEY_ARXIV_URL = ""
GITHUB_REPOSITORY = "cseeyangchen/Human-Centric-AI"
GITHUB_REPOSITORY_URL = f"https://github.com/{GITHUB_REPOSITORY}"
VISITOR_COUNTER_ID = "cseeyangchen-Human-Centric-AI"

ROMAN_NUMERALS = ("I", "II", "III", "IV", "V", "VI", "VII")

METHOD_LEVEL_ICONS = {
    "Visual Appearance": "assets/level-icons/visual-appearance.png",
    "Spatial Geometry": "assets/level-icons/spatial-geometry.png",
    "Kinematic Dynamics": "assets/level-icons/kinematic-dynamics.png",
    "Interaction Modeling": "assets/level-icons/interaction-modeling.png",
    "World Simulation": "assets/level-icons/world-simulation.png",
    "Embodied Agency": "assets/level-icons/embodied-agency.png",
}

DATA_GROUP_ICONS = {
    "Human Subject Resources": "assets/resource-icons/human-subject-resources.png",
    "Human Dynamics Resources": "assets/resource-icons/human-dynamics-resources.png",
    "Human Interaction Resources": "assets/resource-icons/human-interaction-resources.png",
    "Human Embodiment Resources": "assets/resource-icons/human-embodiment-resources.png",
}

# Some works are discussed outside the main method prose but still belong in
# the survey resource index. Apply these corrections after automatic parsing.
METHOD_CATEGORY_OVERRIDES = {
    "li2026humanclaw": "Generalist Humanoid Control",
}

# Official links that appeared in the manuscript or earlier metadata but no
# longer resolve. Replacements are supplied through website_overrides.json
# when the authors provide a current location.
DEAD_WEBSITE_URLS = {
    "https://cuiaiyu.github.io/streettryon",
    "https://github.com/arthoi-reconstruction/arthoi",
    "https://github.com/cyan-c/mt2m",
    "https://github.com/msed-ebrahimi/gif",
    "https://github.com/yanghfu/sigman",
    "https://hot3d.github.io",
    "https://jnnan.github.io/project/chairs",
    "https://lsn33096.github.io/lucas",
    "https://maoxie.github.io/synbody",
    "https://ntu-aiot-lab.github.io/mm-fi",
    "https://rohithpeddi.github.io/captaincook",
    "https://robotdata-market.jdcloud.com/console/market",
    "https://shandaai.github.io/project_mio_page",
    "https://sizhean.github.io/mri",
    "https://sunzhihao18.github.io/handworld",
    "https://yanghfu.github.io/sigman",
}


AWESOME_RESEARCH_LISTS = OrderedDict(
    [
        (
            "General Human-Centric AI",
            [
                (
                    "Awesome Human-Centric AI Survey Resources (Our Survey)",
                    "awesome-human-centric-ai-survey-resources.md",
                    "list",
                ),
                (
                    "Awesome Human-Centric Foundation Models",
                    "https://github.com/HumanCentricModels/Awesome-Human-Centric-Foundation-Models",
                    "repository",
                ),
            ],
        ),
        (
            "Digital Humans and Generative Content",
            [
                ("Awesome Digital Human", "https://github.com/weihaox/awesome-digital-human", "repository"),
                (
                    "Awesome 3D Human Reconstruction",
                    "https://github.com/rlczddl/awesome-3d-human-reconstruction",
                    "repository",
                ),
                (
                    "Deep Learning-based Human Pose Estimation: A Survey",
                    "https://github.com/zczcwh/DL-HPE",
                    "repository",
                ),
                (
                    "Recovering 3D Human Mesh from Monocular Images: A Survey",
                    "https://github.com/tinatiansjz/hmr-survey",
                    "repository",
                ),
                (
                    "Awesome Human Video Generation",
                    "https://github.com/wentaoL86/Awesome-Human-Video-Generation",
                    "repository",
                ),
                ("Awesome Pose Transfer", "https://github.com/Zhangjinso/Awesome-pose-transfer", "repository"),
                ("Awesome Avatars", "https://github.com/pansanity666/Awesome-Avatars", "repository"),
                (
                    "Awesome Conditional Content Generation",
                    "https://github.com/haofanwang/awesome-conditional-content-generation",
                    "repository",
                ),
            ],
        ),
        (
            "Human Motion, Activity, and Sensing",
            [
                (
                    "Awesome Human Activity Recognition",
                    "https://github.com/haoranD/Awesome-Human-Activity-Recognition",
                    "repository",
                ),
                ("Awesome Human Motion", "https://github.com/Foruck/Awesome-Human-Motion", "repository"),
                (
                    "Awesome Human Motion Video Generation",
                    "https://github.com/Winn1y/Awesome-Human-Motion-Video-Generation",
                    "repository",
                ),
                (
                    "Awesome Human Interaction Motion Generation",
                    "https://github.com/soraproducer/Awesome-Human-Interaction-Motion-Generation",
                    "repository",
                ),
                (
                    "Awesome Skeleton-based Action Recognition",
                    "https://github.com/firework8/Awesome-Skeleton-based-Action-Recognition",
                    "repository",
                ),
                (
                    "Awesome WiFi-based Human Sensing",
                    "https://github.com/NTUMARS/Awesome-WiFi-CSI-Sensing",
                    "repository",
                ),
            ],
        ),
        (
            "Human Interaction and Mobility",
            [
                (
                    "Hand-Object Interaction in the Age of Large Foundation Models: Reconstruction, Generation, and Embodied Transfer",
                    "https://github.com/SeanChenxy/Hand3DResearch/tree/hoi-survey",
                    "repository",
                ),
                (
                    "Awesome Human-Agent Collaboration and Interaction Systems",
                    "https://github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems",
                    "repository",
                ),
                (
                    "Awesome Human-Human Interaction",
                    "https://github.com/liangxuy/awesome-human-human-interaction",
                    "repository",
                ),
                (
                    "Awesome Human Mobility Science Paper List",
                    "https://github.com/Star607/Awesome-Human-Mobility-Science-Paper-List",
                    "repository",
                ),
            ],
        ),
        (
            "Humanoid Intelligence",
            [
                (
                    "Awesome Humanoid Robot Learning",
                    "https://github.com/YanjieZe/awesome-humanoid-robot-learning",
                    "repository",
                ),
                (
                    "Awesome Humanoid Learning",
                    "https://github.com/jonyzhang2023/awesome-humanoid-learning",
                    "repository",
                ),
            ],
        ),
    ]
)


OPEN_COURSEWARE = [
    {
        "period": "Winter 2023/24",
        "title": "Virtual Humans",
        "course_url": "https://virtualhumans.mpi-inf.mpg.de/VH23/",
        "video_url": "https://www.youtube.com/playlist?list=PLD1ofCm3vxfz4Oe5XqHmyU6GTLsPJMI5s",
        "instructors": "Gerard Pons-Moll and the Real Virtual Humans team",
        "institution": "University of Tübingen and Max Planck Institute for Informatics",
        "coverage": "A full course on modeling, reconstructing, animating, and synthesizing digital humans, spanning parametric body models, clothing, neural representations, behavior capture, and human-scene interaction.",
    },
]


ACADEMIC_PRESENTATIONS = OrderedDict(
    [
        (
            "High-Level Perspectives on Human-Centric AI",
            [
                (
                    "2024",
                    "Distinguished lecture",
                    "What We See and What We Value: AI with a Human Perspective",
                    "https://www.youtube.com/watch?v=gzOwpEupP5w",
                    "Fei-Fei Li",
                    "University of Washington Allen School Distinguished Lecture",
                    "https://www.youtube.com/watch?v=gzOwpEupP5w",
                    "Human-centered foundations and spatial intelligence",
                ),
                (
                    "2024",
                    "Keynote",
                    "With Spatial Intelligence, AI Will Understand the Real World",
                    "https://www.ted.com/talks/fei_fei_li_with_spatial_intelligence_ai_will_understand_the_real_world",
                    "Fei-Fei Li",
                    "TED 2024",
                    "https://www.ted.com/talks/fei_fei_li_with_spatial_intelligence_ai_will_understand_the_real_world",
                    "Spatial intelligence and embodied understanding",
                ),
                (
                    "2019",
                    "Symposium archive",
                    "Human-Centered Artificial Intelligence Symposium",
                    "https://hai.stanford.edu/events/2019-hai-symposium?section=video-archive",
                    "Symposium speakers",
                    "Stanford Institute for Human-Centered AI",
                    "https://hai.stanford.edu/events/2019-hai-symposium",
                    "High-level perspectives on human-centered AI",
                ),
            ],
        ),
        (
            "Human Foundation Models and Digital Humans",
            [
                (
                    "2024",
                    "Invited talk",
                    "Learning Foundation Models for 3D Humans: A Data Request",
                    "https://www.dropbox.com/scl/fi/s5cnkmnzxx5hb3o2uiagm/SiyuTang.mp4?dl=0&rlkey=bf729wf0bmicwsm7biz4ygve4&st=hpv5zjkw",
                    "Siyu Tang",
                    "ECCV Foundation Models for 3D Humans",
                    "https://human-foundation.github.io/workshop-eccv-2024/",
                    "Human foundation models and data scaling",
                ),
                (
                    "2024",
                    "Invited talk",
                    "Human Models for Embodied AI",
                    "https://www.dropbox.com/scl/fi/2cb6ua4x9dzqe5tdidlql/ECCVW2024_HumanFoundation_Xavier.mp4?dl=0&rlkey=5scm64sv60w6wcolu5xx78esg&st=ai4x8egp",
                    "Xavier Puig",
                    "ECCV Foundation Models for 3D Humans",
                    "https://human-foundation.github.io/workshop-eccv-2024/",
                    "Human models and embodied agents",
                ),
                (
                    "2024",
                    "Invited talk",
                    "Towards Anatomically Correct Digital Human: From Imaging to Foundation Models",
                    "https://www.dropbox.com/scl/fi/w529zzoony2p834vtxkps/ECCVW2024_HumanFoundation_Jingyi.mp4?dl=0&rlkey=pnh061apolg5if8hnbd3dkrwn&st=hwvs5k0m",
                    "Jingyi Yu",
                    "ECCV Foundation Models for 3D Humans",
                    "https://human-foundation.github.io/workshop-eccv-2024/",
                    "Digital humans and anatomical modeling",
                ),
                (
                    "2025",
                    "Keynote series",
                    "BMVA Symposium on Digital Humans",
                    "https://www.youtube.com/playlist?list=PLW8VWHVjepIt1DrtzuLqW0aPYSMsVXFET",
                    "Tadas Baltrusaitis, Gerard Pons-Moll, Dimitris Tzionas, Abhijeet Ghosh, and Thu Nguyen-Phuoc",
                    "British Machine Vision Association",
                    "https://www.bmva.org/meetings/25-05-28-DigitalHumans.html",
                    "Digital humans, foundation models, capture, and generation",
                ),
                (
                    "2023",
                    "Academic seminar",
                    "Digital Humans",
                    "https://inf-opencast.mpi-inf.mpg.de/paella/ui/watch.html?id=5076feb5-46e2-413b-bc86-6d2b6f403ece",
                    "Marc Habermann",
                    "Saarland Informatics Campus",
                    "https://people.mpi-inf.mpg.de/~mhaberma/",
                    "Capture, reconstruction, and animation of digital humans",
                ),
                (
                    "2022",
                    "Distinguished lecture",
                    "What Is a Codec Avatar?",
                    "https://www.youtube.com/watch?v=AoXMpGmihms",
                    "Yaser Sheikh",
                    "Berkeley EECS Distinguished Lecture",
                    "https://eecs.berkeley.edu/research/colloquium/221207-2/",
                    "Photorealistic avatars and remote social presence",
                ),
                (
                    "2021",
                    "Research talk",
                    "Synthetic Data with Digital Humans",
                    "https://www.microsoft.com/en-us/research/video/synthetic-data-with-digital-humans/",
                    "Erroll Wood and Tadas Baltrusaitis",
                    "Microsoft Research",
                    "https://www.microsoft.com/en-us/research/video/synthetic-data-with-digital-humans/",
                    "Synthetic human data for computer vision",
                ),
                (
                    "2022",
                    "Guest lecture",
                    "Complete Codec Telepresence",
                    "https://www.youtube.com/watch?v=CM2rhJWiucQ",
                    "Michael Zollhöfer",
                    "TUM AI Guest Lecture Series",
                    "https://niessner.github.io/TUM-AI-Lecture-Series/",
                    "Photorealistic avatars and telepresence",
                ),
                (
                    "2021",
                    "Guest lecture",
                    "Towards Virtual Humans: Putting Realistic People in Realistic Scenes Doing Realistic Things",
                    "https://www.youtube.com/watch?v=MBHDAGCKKUQ",
                    "Michael J. Black",
                    "TUM AI Guest Lecture Series",
                    "https://niessner.github.io/TUM-AI-Lecture-Series/",
                    "Digital humans in realistic scenes",
                ),
                (
                    "2021",
                    "Guest lecture",
                    "AI-Generated Digital Humans",
                    "https://www.youtube.com/watch?v=Tvk5NqCfyO8",
                    "Hao Li",
                    "TUM AI Guest Lecture Series",
                    "https://niessner.github.io/TUM-AI-Lecture-Series/",
                    "Neural rendering and synthetic humans",
                ),
                (
                    "2020",
                    "Guest lecture",
                    "Perceiving Humans in the 3D World",
                    "https://www.youtube.com/watch?v=WOuCPT0lXio",
                    "Angjoo Kanazawa",
                    "TUM AI Guest Lecture Series",
                    "https://niessner.github.io/TUM-AI-Lecture-Series/",
                    "3D human perception",
                ),
                (
                    "2020",
                    "Guest lecture",
                    "Shape Representations: Parametric Meshes vs. Implicit Functions",
                    "https://www.youtube.com/watch?v=_4E2iEmJXW8",
                    "Gerard Pons-Moll",
                    "TUM AI Guest Lecture Series",
                    "https://niessner.github.io/TUM-AI-Lecture-Series/",
                    "Representations for 3D humans and clothing",
                ),
                (
                    "2020",
                    "Guest lecture",
                    "Photorealistic Telepresence",
                    "https://www.youtube.com/watch?v=2RuzbIS3fTY",
                    "Yaser Sheikh",
                    "TUM AI Guest Lecture Series",
                    "https://niessner.github.io/TUM-AI-Lecture-Series/",
                    "Codec avatars and social telepresence",
                ),
            ],
        ),
        (
            "3D Humans, Motion, and Egocentric Intelligence",
            [
                (
                    "2025",
                    "Invited talk",
                    "Estimating Human Motion in World Coordinates",
                    "https://youtu.be/_cMRL_i5VmU",
                    "Michael J. Black",
                    "CVPR Global 3D Human Poses",
                    "https://g3p-workshop.github.io/",
                    "Global human pose and motion",
                ),
                (
                    "2025",
                    "Invited talk",
                    "Understanding 3D Humans in Contextual 3D Spaces",
                    "https://youtu.be/QG-neoiKHvc",
                    "Hanbyul Joo",
                    "CVPR Global 3D Human Poses",
                    "https://g3p-workshop.github.io/",
                    "3D humans in contextual scenes",
                ),
                (
                    "2025",
                    "Invited talk",
                    "How to Train Your Humanoid",
                    "https://youtu.be/ip1qJAc9lag",
                    "Angjoo Kanazawa",
                    "CVPR Global 3D Human Poses",
                    "https://g3p-workshop.github.io/",
                    "Human motion and humanoid learning",
                ),
                (
                    "2024",
                    "Research talk",
                    "Building Large Models for Predicting Human Motion",
                    "https://youtu.be/eVyjeJhdxB4",
                    "C. Karen Liu",
                    "Stanford Frontiers in Robotics and Machine Learning",
                    "https://forum.stanford.edu/events/2024-annual-affiliates-meeting/day-2-frontiers-robotics-and-machine-learning-workshop",
                    "Large-scale models for human motion prediction",
                ),
                (
                    "2020",
                    "Distinguished lecture",
                    "First-Person Perception and Interaction",
                    "https://www.microsoft.com/en-us/research/video/first-person-perception-and-interaction/",
                    "Kristen Grauman",
                    "Microsoft Research",
                    "https://www.microsoft.com/en-us/research/video/first-person-perception-and-interaction/",
                    "Egocentric perception and human-environment interaction",
                ),
                (
                    "2020",
                    "Guest lecture",
                    "Sights, Sounds, and Space: Audio-Visual Learning in 3D Environments",
                    "https://www.youtube.com/watch?v=1EQ6helfvtM",
                    "Kristen Grauman",
                    "TUM AI Guest Lecture Series",
                    "https://niessner.github.io/TUM-AI-Lecture-Series/",
                    "Egocentric and multimodal spatial learning",
                ),
                (
                    "2024",
                    "Workshop recording",
                    "Workshop on Human Motion Generation",
                    "https://www.youtube.com/watch?v=lkQ4sDK4u9U",
                    "Daniel Holden, Michael Neff, Karen Liu, and Siyu Tang",
                    "CVPR HuMoGen",
                    "https://humogen.github.io/2024/",
                    "Motion generation and control",
                ),
                (
                    "2024",
                    "Workshop recording",
                    "New Challenges in 3D Human Understanding",
                    "https://www.youtube.com/watch?v=KwmVZhTnwHM",
                    "Workshop speakers",
                    "CVPR 2024",
                    "https://cvpr.thecvf.com/virtual/2024/workshop/23604",
                    "3D human reconstruction and understanding",
                ),
                (
                    "2023",
                    "Workshop recording",
                    "Joint 3rd Ego4D and 11th EPIC Workshop on Egocentric Vision",
                    "https://www.youtube.com/watch?v=Kc0tjwth_Mc",
                    "Workshop speakers",
                    "CVPR 2023",
                    "https://cvpr.thecvf.com/virtual/2023/workshop/18537",
                    "Egocentric perception and action",
                ),
            ],
        ),
        (
            "World Models and Embodied Intelligence",
            [
                (
                    "2026",
                    "Workshop recording",
                    "Sense of Space: Multi-Sensory Modeling for Embodied Intelligence",
                    "https://youtu.be/LqLruZeQ6PA",
                    "Workshop speakers",
                    "CVPR 2026",
                    "https://sense-of-space.github.io/",
                    "Spatial, tactile, and embodied intelligence",
                ),
                (
                    "2026",
                    "Invited talk",
                    "Observational Learning for Manipulation via Visual Imitation of Humans",
                    "https://youtu.be/LqLruZeQ6PA?t=12120",
                    "Homanga Bharadhwaj",
                    "CVPR Sense of Space",
                    "https://sense-of-space.github.io/",
                    "Human-to-robot skill transfer",
                ),
                (
                    "2025",
                    "Tutorial",
                    "From Video Generation to World Model",
                    "https://www.youtube.com/watch?v=XiYayWC5pao",
                    "Tutorial speakers",
                    "CVPR 2025",
                    "https://cvpr.thecvf.com/virtual/2025/tutorial/35905",
                    "Video generation and world models",
                ),
                (
                    "2025",
                    "Workshop recording",
                    "3D-LLM/VLA: Bridging Language, Vision and Action in 3D Environments",
                    "https://www.youtube.com/watch?v=3Dd3CwsVlqA",
                    "Workshop speakers",
                    "CVPR 2025",
                    "https://cvpr.thecvf.com/virtual/2025/workshop/32287",
                    "3D foundation models and embodied agents",
                ),
                (
                    "2025",
                    "Workshop recording",
                    "2nd Workshop on Embodied Humans",
                    "https://www.youtube.com/watch?v=GaCC_-qcD_k",
                    "Workshop speakers",
                    "CVPR 2025",
                    "https://cvpr.thecvf.com/virtual/2025/workshop/32359",
                    "Virtual humans and humanoid robots",
                ),
                (
                    "2024",
                    "Research talk",
                    "Interactive Robotics in the Era of Large Pretrained Models",
                    "https://youtu.be/05-XbxY3aqs",
                    "Dorsa Sadigh",
                    "Stanford Frontiers in Robotics and Machine Learning",
                    "https://forum.stanford.edu/events/2024-annual-affiliates-meeting/day-2-frontiers-robotics-and-machine-learning-workshop",
                    "Large pretrained models and interactive robotics",
                ),
                (
                    "2022",
                    "Guest lecture",
                    "Learning to Walk with Vision and Proprioception",
                    "https://www.youtube.com/watch?v=zjsdCiOAjNA",
                    "Jitendra Malik",
                    "TUM AI Guest Lecture Series",
                    "https://niessner.github.io/TUM-AI-Lecture-Series/",
                    "Visuomotor learning and embodied locomotion",
                ),
            ],
        ),
        (
            "Humanoid Learning and Human-Robot Interaction",
            [
                (
                    "2026",
                    "Invited talk",
                    "Scaling Whole-Body Humanoid Skills with Human Demonstration",
                    "https://youtu.be/z6vdlkJXDdY",
                    "Tianyu Li",
                    "RSS Embodied Intelligence in the Wild",
                    "https://opendrivelab.com/rss2026/workshop",
                    "Human demonstrations and humanoid control",
                ),
                (
                    "2026",
                    "Invited talk",
                    "Beyond Imitation: Executable, Correctable, and Adaptable Skills for Humanoid Robots",
                    "https://youtu.be/6J5yugqOZxc",
                    "Li Yi",
                    "RSS Embodied Intelligence in the Wild",
                    "https://opendrivelab.com/rss2026/workshop",
                    "Adaptable humanoid skills",
                ),
                (
                    "2026",
                    "Invited talk",
                    "Learning Personalized Whole-Arm Manipulation Around Humans",
                    "https://youtu.be/CX3A0ha4SSk",
                    "Tapomayukh Bhattacharjee",
                    "RSS Embodied Intelligence in the Wild",
                    "https://opendrivelab.com/rss2026/workshop",
                    "Human-aware manipulation",
                ),
                (
                    "2024",
                    "Academic seminar",
                    "Modeling Humans for Humanoid Robots",
                    "https://www.youtube.com/watch?v=uQ-5BryUNv8",
                    "Xiaolong Wang",
                    "Stanford Robotics Seminar",
                    "https://youtu.be/uQ-5BryUNv8",
                    "Human modeling and humanoid learning",
                ),
                (
                    "2026",
                    "Robotics seminar",
                    "Shaping the Future of Human-Robot Collaboration",
                    "https://www.youtube.com/watch?v=Y6baiESk-04",
                    "Oussama Khatib",
                    "MIT Robotics Seminar",
                    "https://www.youtube.com/watch?v=Y6baiESk-04",
                    "Physical interaction and human-robot collaboration",
                ),
                (
                    "2020",
                    "Robotics seminar",
                    "Optimizing for Coordination with People",
                    "https://youtu.be/AQ-w5o2oGI8",
                    "Anca Dragan",
                    "Carnegie Mellon Robotics Institute Seminar",
                    "https://www.ri.cmu.edu/event/ri-seminar-anca-dragan-university-of-california-berkeley-assistant-professor-2020-02-28/",
                    "Human-robot coordination and preference inference",
                ),
                (
                    "2018",
                    "High-level talk",
                    "Will Artificial Intelligence Mean the End of Social Interaction?",
                    "https://vimeo.com/295242186",
                    "Justine Cassell",
                    "National Academies Distinctive Voices",
                    "https://vimeo.com/295242186",
                    "Social interaction with virtual humans and conversational agents",
                ),
                (
                    "2017",
                    "Robotics seminar",
                    "Modeling Human Movements for Robotics",
                    "https://youtu.be/WymnyQlD6kc",
                    "C. Karen Liu",
                    "Robohub Robotics Talk",
                    "https://youtu.be/WymnyQlD6kc",
                    "Human motion modeling for robot control",
                ),
                (
                    "2020",
                    "Talk playlist",
                    "Emergent Behaviors in Human-Robot Systems",
                    "https://www.youtube.com/playlist?list=PLALgrVO1YLmsXdaRKWtABqONtA81J0t2O",
                    "Workshop speakers",
                    "Robotics: Science and Systems Workshop",
                    "https://iliad.stanford.edu/rss-workshop/iframe.html",
                    "Human-robot interaction and collaboration",
                ),
            ],
        ),
    ]
)


WORKSHOPS_BY_YEAR = OrderedDict(
    [
        (
            "2026",
            [
                ("The 2nd Workshop on Advancing Artificial Intelligence through Theory of Mind", "AAAI 2026", "https://tom4ai.github.io/events/AAAI2026/"),
                ("AERO-HPR: Human Perception and Recognition in Aerial Surveillance", "CVPR 2026", "https://aero-hpr.github.io/"),
                ("The 3rd Workshop on Human Motion Generation (HuMoGen): New Perspectives on Simulation, Animation, and VR Applications", "CVPR 2026", "https://humogen.github.io/"),
                ("The 2nd Workshop on Photorealistic 3D Head Avatars", "CVPR 2026", "https://kaldir.vc.cit.tum.de/nersemble_benchmark/cvpr2026"),
                ("Workshop on Multimodal Human Motion Analysis", "CVPR 2026", "https://hri.iit.it/en/cvpr2026-workshop"),
                ("PhysHuman: Physically Grounded Human Perception and Modeling", "CVPR 2026", "https://physhuman.github.io/"),
                ("Computer Vision for Biomechanics Workshop", "CVPR 2026", "https://cvbw2026.github.io/"),
                ("Humans of Generative AI", "CVPR 2026", "https://humansofgenerativeai.github.io/"),
                ("The 2nd Workshop on Human-Interactive Generation and Editing", "CVPR 2026", "https://cvpr.thecvf.com/Conferences/2026/Workshops"),
                ("The 10th Workshop on Affective & Behavior Analysis in-the-Wild", "CVPR 2026", "https://cvpr.thecvf.com/Conferences/2026/Workshops"),
                ("The 7th International Workshop on Eye and Gaze in Computer Vision", "CVPR 2026", "https://cvpr.thecvf.com/Conferences/2026/Workshops"),
                ("The 2nd Workshop on Agents in Interaction, from Humans to Robots", "CVPR 2026", "https://agents-in-interactions.github.io/"),
                ("Third Joint Egocentric Vision (EgoVis) Workshop", "CVPR 2026", "https://egovis.github.io/cvpr26/"),
                ("The 7th Embodied AI Workshop", "CVPR 2026", "https://embodied-ai.org/"),
                ("The 2nd Workshop on Foundation Models Meet Embodied Agents", "CVPR 2026", "https://cvpr.thecvf.com/Conferences/2026/Workshops"),
                ("The 2nd Workshop on Foundation & Generative Models in Biometrics", "CVPR 2026", "https://foundgen-bio.github.io/"),
                ("Workshop on Vision-based Assistants in the Real-World", "CVPR 2026", "https://varworkshop.github.io/"),
                ("The 1st Workshop on Vision for Intelligent Task Assistants", "CVPR 2026", "https://cvpr.thecvf.com/Conferences/2026/Workshops"),
                ("Second Workshop on Skilled Activity Understanding, Assessment & Feedback Generation", "CVPR 2026", "https://sauafg-workshop.github.io/"),
                ("Generative AI for Sign Language", "CVPR 2026", "https://genai4sl.github.io/"),
                ("The 2nd Workshop on Multimodal Sign Language Recognition", "CVPR 2026", "https://cvpr.thecvf.com/Conferences/2026/Workshops"),
                ("Generative AI for XR and Identity-based Applications", "CVPR 2026", "https://bmdj-vt.github.io/workshops/cvpr_2026"),
                ("Rediscovering Intelligence: Can AI Still Learn from Humans?", "CVPR 2026", "https://cvpr.thecvf.com/Conferences/2026/Workshops"),
                ("IPA: Interactive Physical AI Workshop", "CVPR 2026", "https://research.nvidia.com/labs/amri/projects/IPA/2026/"),
                ("Bridging Vision, Language, and Action: What's Missing in Actionable Visual Perception for Robotics", "CVPR 2026", "https://activis-workshop.github.io/"),
                ("From Lab Demos to Daily Tasks: Embodied Intelligence in the Wild", "CVPR 2026", "https://opendrivelab.com/cvpr2026/workshop"),
                ("Sense of Space: Multi-Sensory Modeling for Embodied Intelligence", "CVPR 2026", "https://sense-of-space.github.io/"),
                ("The 1st Workshop on Multi-Agent Robotic Systems: Scaling with Compositional Intelligence", "CVPR 2026", "https://mars-eai.github.io/CVPR-SCI-MARS-Webpage/"),
                ("Embodied Reasoning in Action: Embodied Reasoning for Robotic Manipulation", "CVPR 2026", "https://embodied-reasoning.github.io/"),
                ("4D Digital Twins: Real-to-Sim-to-Real for Physical AI", "CVPR 2026", "https://research.nvidia.com/labs/amri/projects/4DDT/2026/"),
                ("RobustifAI: Robustifying Generative AI for Reliable, Safe, and Human-Centric Systems", "IJCAI-ECAI 2026", "https://sites.google.com/view/robustifai-workshop"),
                ("AI-Based Humanoid Robot Design and Control through the Lens of HRI, Evolution, and Biomechanics", "IJCAI-ECAI 2026", "https://hominoid-robot.dfki-bremen.de/"),
                ("The First Joint Workshop on Human Behavior Analysis and Interaction for Emotional Intelligence, with the 4th MiGA Challenge", "IJCAI-ECAI 2026", "https://ei-miga.github.io/"),
                ("3D Human Understanding: Towards Human-Centric World Models", "ECCV 2026", "https://sites.google.com/view/3d-humans-eccv2026"),
                ("Human-Centered Multimodal Intelligence in the Wild: Foundation Models and Beyond", "ECCV 2026", "https://eccv.ecva.net/Conferences/2026/Workshops"),
                ("Human Motion-Informed World Models and Socially Intelligent Action", "ECCV 2026", "https://eccv.ecva.net/Conferences/2026/Workshops"),
                ("Human-Scene Interaction: Towards Scene-Aware Motion, Communication, and Embodied Agents", "ECCV 2026", "https://www.hsi-workshop.com/"),
                ("CONTEXTUS: Understanding Multi-Actor Scene Interaction in Context", "ECCV 2026", "https://lap.chalearn.eu/public/ECCV26-CONTEXTUS"),
                ("Interactive Social Avatars with the 4th GENEA Gesture Generation Challenge", "ECCV 2026", "https://interactive-social-avatars.github.io/"),
                ("Observing and Acting as Dexterous Hands", "ECCV 2026", "https://hands-workshop.org/workshop2026.html"),
                ("Multimodal Digital Agents Workshop", "ECCV 2026", "https://mda-workshop.allen.ai/"),
                ("Wearables AI: Towards Building Real-Time Multimodal Contextual Assistants", "ECCV 2026", "https://wearable-ai-workshop.github.io/"),
                ("The 3rd Workshop on Foundation & Generative Models in Biometrics", "ECCV 2026", "https://foundgen-bio.github.io/"),
                ("The 11th Workshop on Affective & Behavior Analysis in-the-Wild", "ECCV 2026", "https://eccv.ecva.net/Conferences/2026/Workshops"),
                ("The 14th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2026", "https://eccv.ecva.net/Conferences/2026/Workshops"),
                ("The 3rd Workshop on Human-Inspired Computer Vision", "ECCV 2026", "https://eccv.ecva.net/Conferences/2026/Workshops"),
                ("Human Motion in Real-World and Clinical Settings", "ECCV 2026", "https://mocha.care-pd.ca/"),
                ("Workshop on Human-AI Co-Creation", "ECCV 2026", "https://eccv.ecva.net/Conferences/2026/Workshops"),
                ("Agent in World: Living Worlds with Interactive Agents", "ECCV 2026", "https://eccv.ecva.net/Conferences/2026/Workshops"),
                ("Embodied Agent and Dialog", "ECCV 2026", "https://ead-workshop.github.io/"),
                ("The 8th Workshop on Long-Term Human Motion Prediction", "ICRA 2026", "https://motionpredictionicra2026.github.io/"),
                ("A User-Centered Perspective on Human-Robot Sensorimotor Augmentation", "ICRA 2026", "https://2026.ieee-icra.org/workshops-and-tutorials/"),
                ("Multimodal Embodied Interaction in Robots", "ICRA 2026", "https://2026.ieee-icra.org/workshops-and-tutorials/"),
                ("Shared Challenges in Human-Centered and Resilient Robotic Autonomy", "ICRA 2026", "https://2026.ieee-icra.org/workshops-and-tutorials/"),
                ("Beyond Teleoperation: Learning from Diverse Human and Simulation Data", "ICRA 2026", "https://2026.ieee-icra.org/workshops-and-tutorials/"),
                ("Bridging the Gap between Robot Learning and Human-Robot Interaction", "ICRA 2026", "https://2026.ieee-icra.org/workshops-and-tutorials/"),
                ("Workshop on Pedestrian Behavior Prediction", "ICRA 2026", "https://workshop-pbp2026.github.io/"),
                ("Human-Inspired Principles for Robotic Dexterous Manipulation", "ICRA 2026", "https://2026.ieee-icra.org/workshops-and-tutorials/"),
                ("The 4th Workshop on NeuroDesign in Human-Robot Interaction: The making of engaging HRI technology your brain can't resist", "ICRA 2026", "https://neurodesign-in-hri.webflow.io/"),
                ("Perception and Decision Making for Athletic Humanoid Robotics", "IROS 2026", "https://iros-2026-athletic-humanoid.github.io/workshop/"),
                ("Beyond the Lab: Human Behavior Monitoring and Modeling in In-the-Wild Human-Robot Interaction", "RSS 2026", "https://sites.google.com/view/rss26-beyond-the-lab-hri/home"),
                ("It's the Demos: The Role of Demonstration Quality in Imitation-Based Robot Manipulation", "RSS 2026", "https://its-the-demos.github.io/"),
                ("The 4th Workshop on Dexterous Manipulation: Scalable Learning for Human-Level Skills", "RSS 2026", "https://dex-manipulation.github.io/rss2026/"),
                ("Whole-Body Control and Bimanual Manipulation: Applications in Humanoids and Beyond", "RSS 2026", "https://wcbm-workshop.github.io/rss2026/"),
                ("Human-Centric Mobile Manipulation Workshop", "RSS 2026", "https://adacompnus.github.io/human-centric-mobile-manipulation/"),
                ("Differentiable Physics for Graphics and AI", "SIGGRAPH 2026", "https://s2026.conference-schedule.org/presentation/?id=twork_111&sess=sess224"),
            ],
        ),
        (
            "2025",
            [
                ("Advancing Artificial Intelligence through Theory of Mind: Bridging Human Cognition and Artificial Intelligence", "AAAI 2025", "https://aaai.org/conference/aaai/aaai-25/workshop-list/"),
                ("3D Digital Twin: Progress, Challenges, and Future Directions", "CVPR 2025", "https://cvpr.thecvf.com/virtual/2025/workshop/32303"),
                ("The 1st Workshop on Photorealistic 3D Head Avatars", "CVPR 2025", "https://kaldir.vc.cit.tum.de/nersemble_benchmark/cvpr2025"),
                ("The 2nd Workshop on Human Motion Generation (HuMoGen)", "CVPR 2025", "https://humogen.github.io/2025/"),
                ("Second Joint Egocentric Vision (EgoVis) Workshop", "CVPR 2025", "https://egovis.github.io/cvpr25/"),
                ("Computer Vision for Mixed Reality", "CVPR 2025", "https://cv4mr.github.io/"),
                ("Workshop on Vision-based Assistants in the Real-World", "CVPR 2025", "https://varworkshop.github.io/2025/schedule/"),
                ("The 6th Embodied AI Workshop", "CVPR 2025", "https://embodied-ai.org/"),
                ("Embodied Intelligence for Autonomous Systems on the Horizon", "CVPR 2025", "https://cvpr.thecvf.com/Conferences/2025/workshop-list"),
                ("The 2nd Workshop on Multi-Agent Embodied Intelligent Systems Meet Generative-AI Era", "CVPR 2025", "https://openreview.net/group?id=thecvf.com%2FCVPR%2F2025%2FWorkshop%2FMEIS"),
                ("The 1st Workshop on Agents in Interaction, from Humans to Robots", "CVPR 2025", "https://agents-in-interactions.github.io/"),
                ("The 2nd Workshop on Embodied Humans: Symbiotic Intelligence between Virtual Humans and Humanoid Robots", "CVPR 2025", "https://cvpr.thecvf.com/virtual/2025/workshop/32359"),
                ("The 8th Workshop on Affective & Behavior Analysis in-the-Wild", "CVPR 2025", "https://cvpr.thecvf.com/Conferences/2025/workshop-list"),
                ("Global 3D Human Poses", "CVPR 2025", "https://g3p-workshop.github.io/"),
                ("The 3rd RHOBIN Challenge on Reconstruction of Human-Object Interaction", "CVPR 2025", "https://rhobin-challenge.github.io/"),
                ("The 1st Workshop on Humanoid Agents", "CVPR 2025", "https://humanoid-agents.github.io/"),
                ("The 2nd Workshop on 3D Human Understanding", "CVPR 2025", "https://sites.google.com/view/3d-humans-cvpr2025"),
                ("The 1st Workshop on Foundation Models Meet Embodied Agents", "CVPR 2025", "https://cvpr.thecvf.com/Conferences/2025/workshop-list"),
                ("The 1st Workshop on Interactive Human-Centric Foundation Models", "ICCV 2025", "https://i-hfm-2025.github.io/I-HFM-2025/"),
                ("Human-Robot-Scene Interaction and Collaboration", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/workshop/2837"),
                ("The 1st Workshop on Foundation & Generative Models in Biometrics", "ICCV 2025", "https://foundgen-bio.github.io/"),
                ("The 1st Workshop on Human-Interactive Generation and Editing", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/workshop/2772"),
                ("The 2nd EgoMotion Workshop", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/workshop/2800"),
                ("Binocular Egocentric-360 Multimodal Scene Understanding in the Wild", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/events/workshop"),
                ("First Workshop on Skilled Activity Understanding, Assessment and Feedback Generation", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/events/workshop"),
                ("The 1st Embodied Spatial Reasoning Workshop", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/workshop/2746"),
                ("Artificial Social Intelligence Workshop", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/events/workshop"),
                ("Multimodal AI Agents", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/events/workshop"),
                ("The 9th Workshop on Affective & Behavior Analysis in-the-Wild", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/events/workshop"),
                ("The 13th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/workshop/2836"),
                ("The 2nd Workshop on Human-Inspired Computer Vision", "ICCV 2025", "https://iccv.thecvf.com/virtual/2025/workshop/2725"),
                ("The 8th Workshop on AI for Aging Rehabilitation and Intelligent Assisted Living", "IJCAI 2025", "https://sites.google.com/view/arial2025/home"),
                ("User-Aligned Assessment of Adaptive AI Systems", "IJCAI 2025", "https://aair-lab.github.io/aia2025/"),
                ("Generative AI and Theory of Mind in Communicating Agents", "IJCAI 2025", "https://tomworkshop.github.io/"),
                ("The 3rd Workshop and Challenge on Human Behavior Analysis for Emotion Understanding", "IJCAI 2025", "https://cv-ac.github.io/MiGA2025/"),
                ("Foundation Models for the Brain and Body", "NeurIPS 2025", "https://neurips.cc/virtual/2025/workshop/109571"),
                ("Embodied World Models for Decision Making", "NeurIPS 2025", "https://neurips.cc/virtual/2025/workshop/109532"),
                ("Embodied and Safe-Assured Robotic Systems", "NeurIPS 2025", "https://neurips.cc/virtual/2025/workshop/127833"),
                ("The 6th GENEA Workshop", "ACM MM 2025", "https://genea-workshop.github.io/2025/workshop/"),
                ("The 7th Workshop on Long-Term Human Motion Prediction", "ICRA 2025", "https://motionpredictionicra2025.github.io/"),
                ("Human-Centered Robot Learning in the Era of Big Data and Large Models", "ICRA 2025", "https://2025.ieee-icra.org/event/human-centered-robot-learning-in-the-era-of-big-data-and-large-models/"),
                ("Advances in Social Robot Navigation: Planning, HRI, and Beyond", "ICRA 2025", "https://socialnav2025.pages.dev/"),
                ("Multi-Agent Embodied Intelligent Systems Meet Foundation Models and Large-scale Datasets", "ICRA 2025", "https://maeismaeis.github.io/"),
                ("Building a Common Humanoid Platform Infrastructure for AI-Based Testing", "ICRA 2025", "https://2025.ieee-icra.org/workshops-and-tutorials/"),
                ("Nonverbal Cues for Human-Robot Cooperative Intelligence", "ICRA 2025", "https://2025.ieee-icra.org/events/category/sessions/workshops-tutorials/day/2025-05-23/"),
                ("Enhancing Human Engagement in Social Assistive Robotics", "IROS 2025", "https://iros25.org/WorkshopsTutorials.html"),
                ("Action and Interaction: Humans and Robots in Collaboration", "IROS 2025", "https://iros25.org/WorkshopsTutorials.html"),
                ("Augmentative Human-Robot Interaction", "IROS 2025", "https://iros25.org/WorkshopsTutorials.html"),
                ("Shared Autonomy and Sense of Agency", "IROS 2025", "https://iros25.org/WorkshopsTutorials.html"),
                ("Workshop on Continual Robot Learning from Humans", "RSS 2025", "https://continual-robot-learning-from-humans.github.io/"),
                ("EgoAct: The 1st Workshop on Egocentric Perception and Action for Robot Learning", "RSS 2025", "https://egoact.github.io/rss2025"),
                ("Human-Robot Contact and Manipulation", "RSS 2025", "https://hrcm-workshop.github.io/2025/"),
                ("The 2nd Workshop on Generative Modeling Meets Human-Robot Interaction", "RSS 2025", "https://sites.google.com/view/gai-hri"),
                ("Human-in-the-Loop Robot Learning: Teaching, Correcting, and Adapting", "RSS 2025", "https://hitl-robot-learning.github.io/"),
                ("Large Foundation Models for Interactive Robot Learning", "RSS 2025", "https://lfmrss2025.weebly.com/"),
                ("Whole-Body Control and Bimanual Manipulation: Applications in Humanoids and Beyond", "RSS 2025", "https://wcbm-workshop.github.io/"),
                ("Generalizing Natural Behavior: Retargeting Human or Animal Motion to Robotic Forms", "SIGGRAPH 2025", "https://s2025.conference-schedule.org/presentation/?id=twork_105&sess=sess277"),
                ("Hybrid Dance Xplorations: Artist-Centric XR/AI Sandbox for Co-Creation and Performance", "SIGGRAPH 2025", "https://s2025.conference-schedule.org/presentation/?id=fwork_112&sess=sess248"),
            ],
        ),
        (
            "2024",
            [
                ("Human-Centric Representation Learning", "AAAI 2024", "https://hcrl-workshop.github.io/2024/schedule.html"),
                ("AI for Digital Human", "AAAI 2024", "https://digitalhumanworkshop.github.io/"),
                ("Machine Learning for Cognitive and Mental Health", "AAAI 2024", "https://aaai.org/aaai-24-conference/aaai-24-workshop-list/"),
                ("The 1st Workshop on Human Motion Generation (HuMoGen)", "CVPR 2024", "https://humogen.github.io/2024/"),
                ("The 1st EgoMotion Workshop", "CVPR 2024", "https://cvpr.thecvf.com/virtual/2024/events/workshop"),
                ("First Joint Egocentric Vision (EgoVis) Workshop", "CVPR 2024", "https://egovis.github.io/cvpr24/"),
                ("The 2nd Workshop on Computer Vision for Mixed Reality", "CVPR 2024", "https://cv4mr.github.io/"),
                ("The 5th Embodied AI Workshop", "CVPR 2024", "https://embodied-ai.org/"),
                ("The 2nd Workshop on Embodied Humans: Symbiotic Intelligence between Virtual Humans and Humanoid Robots", "CVPR 2024", "https://cvpr.thecvf.com/virtual/2024/workshop/23651"),
                ("The 6th Workshop on Affective & Behavior Analysis in-the-Wild", "CVPR 2024", "https://cvpr.thecvf.com/Conferences/2024/workshop-list"),
                ("The 6th International Workshop on Eye and Gaze in Computer Vision", "CVPR 2024", "https://cvpr.thecvf.com/Conferences/2024/workshop-list"),
                ("The 2nd RHOBIN Challenge on Reconstruction of Human-Object Interaction", "CVPR 2024", "https://rhobin-challenge.github.io/"),
                ("New Challenges in 3D Human Understanding", "CVPR 2024", "https://cvpr.thecvf.com/Conferences/2024/workshop-list"),
                ("Social Presence with Codec Avatars", "CVPR 2024", "https://cvpr.thecvf.com/virtual/2024/events/workshop"),
                ("The 5th Workshop on Robot Visual Perception in Human-Crowded Environments", "CVPR 2024", "https://cvpr.thecvf.com/virtual/2024/events/workshop"),
                ("Workshop on Virtual Try-On", "CVPR 2024", "https://cvpr.thecvf.com/Conferences/2024/workshop-list"),
                ("New Trends in Multimodal Human Action Perception, Understanding, and Generation", "CVPR 2024", "https://cvpr.thecvf.com/Conferences/2024/workshop-list"),
                ("Computer Vision with Humans in the Loop", "CVPR 2024", "https://cvpr.thecvf.com/Conferences/2024/workshop-list"),
                ("Populating Empty Cities: Virtual Humans for Robotics and Autonomous Driving", "CVPR 2024", "https://poets2024.github.io/"),
                ("Foundation Models for 3D Humans", "ECCV 2024", "https://human-foundation.github.io/workshop-eccv-2024/"),
                ("T-CAP: Towards Human-Centric AI through Continual and Active Perception", "ECCV 2024", "https://eccv2024.ecva.net/virtual/2024/events/workshop"),
                ("Artificial Social Intelligence", "ECCV 2024", "https://eccv2024.ecva.net/virtual/2024/events/workshop"),
                ("Expressive Encounters: Computational Modeling of Human and Animal Social Behavior", "ECCV 2024", "https://eccv2024.ecva.net/virtual/2024/events/workshop"),
                ("Observing and Understanding Hands in Action", "ECCV 2024", "https://eccv2024.ecva.net/virtual/2024/events/workshop"),
                ("The 7th Workshop on Affective & Behavior Analysis in-the-Wild", "ECCV 2024", "https://eccv2024.ecva.net/virtual/2024/events/workshop"),
                ("The 12th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2024", "https://eccv2024.ecva.net/virtual/2024/events/workshop"),
                ("The 1st Workshop on Human-Inspired Computer Vision", "ECCV 2024", "https://openreview.net/group?id=thecvf.com%2FECCV%2F2024%2FWorkshop%2FHCV"),
                ("Multimodal Agents", "ECCV 2024", "https://eccv2024.ecva.net/virtual/2024/events/workshop"),
                ("The Eyes of the Future: Smart Eyewear for Egocentric Vision", "ECCV 2024", "https://eccv2024.ecva.net/virtual/2024/events/workshop"),
                ("The 4th International Workshop on Deep Learning for Human Activity Recognition", "IJCAI 2024", "https://ijcai24.org/workshops/index.html"),
                ("The 2nd Challenge and Workshop on Micro-Gesture Analysis for Hidden Emotion Understanding", "IJCAI 2024", "https://ijcai24.org/workshops/index.html"),
                ("The 5th International Workshop on Human-Centric Multimedia Analysis", "ACM MM 2024", "https://hcma2024.github.io/"),
                ("Models of Human Feedback for AI Alignment", "ICML 2024", "https://icml.cc/virtual/2024/events/workshop"),
                ("Humans, Algorithmic Decision-Making and Society: Modeling Interactions and Impact", "ICML 2024", "https://icml.cc/virtual/2024/events/workshop"),
                ("Pluralistic Alignment Workshop", "NeurIPS 2024", "https://neurips.cc/virtual/2024/events/workshop"),
                ("Generative AI and Creativity: A Dialogue between Machine Learning Researchers and Creative Professionals", "NeurIPS 2024", "https://neurips.cc/virtual/2024/events/workshop"),
                ("The 6th Workshop on Long-Term Human Motion Prediction", "ICRA 2024", "https://motionpredictionicra2024.github.io/"),
                ("Humanoid Whole-Body Control: From Human Motion Understanding to Humanoid Locomotion", "ICRA 2024", "https://icra-2024-humanoid.github.io/"),
                ("Towards Collaborative Partners: Physical Human-Robot Interaction", "ICRA 2024", "https://sites.google.com/view/icra24-physical-hri"),
                ("Workshop on Human-Aligned Reinforcement Learning for Autonomous Agents and Robots", "ICRA 2024", "https://harlworkshop.github.io/"),
                ("The 2nd Workshop on NeuroDesign in Human-Robot Interaction: The making of engaging HRI technology your brain can't resist", "ICRA 2024", "https://www.neurodesign-hri.ws/"),
                ("Safety and Normative Behaviors in Human-Robot Interaction", "RSS 2024", "https://sites.google.com/view/safe-hri/"),
                ("Mechanisms for Mapping Human Input to Robots: From Robot Learning to Shared Control and Autonomy", "RSS 2024", "https://mechanisms-hri.github.io"),
                ("Workshop on Embodied Voices", "RSS 2024", "https://rosielab.github.io/wev/"),
                ("Unsolved Problems in Social Robot Navigation", "RSS 2024", "https://unsolvedsocialnav.org"),
                ("Robots That Help and Ask for Help", "RSS 2024", "https://sites.google.com/unisi.it/robots-that-ask-for-help"),
                ("Social Intelligence in Humans and Robots", "RSS 2024", "https://social-intelligence-human-ai.github.io/proposal.html"),
                ("GROUND: Advancing Group Understanding and Robots' Adaptive Behavior", "RSS 2024", "https://ground-hri.github.io/workshop/"),
            ],
        ),
        (
            "2023",
            [
                ("Recent Trends in Human-Centric AI", "AAAI 2023", "https://r2hcai.github.io/"),
                ("User-Centric AI for Assistance in At-Home Tasks", "AAAI 2023", "https://ai4athome.github.io/"),
                ("Workshop on High-Fidelity Neural Actors", "CVPR 2023", "https://hfna-workshop.github.io/"),
                ("The 1st Workshop on Computer Vision for Mixed Reality", "CVPR 2023", "https://cvpr.thecvf.com/Conferences/2023/workshop-list"),
                ("Accessibility, Vision, and Autonomy Meet", "CVPR 2023", "https://cvpr.thecvf.com/Conferences/2023/workshop-list"),
                ("4D Hand-Object Interaction", "CVPR 2023", "https://cvpr.thecvf.com/Conferences/2023/workshop-list"),
                ("The 1st RHOBIN Challenge on Reconstruction of Human-Object Interaction", "CVPR 2023", "https://rhobin-challenge.github.io/"),
                ("Joint 3rd Ego4D and 11th EPIC Workshop on Egocentric Vision", "CVPR 2023", "https://cvpr.thecvf.com/virtual/2023/workshop/18537"),
                ("The 5th Workshop on Affective & Behavior Analysis in-the-Wild", "CVPR 2023", "https://cvpr.thecvf.com/Conferences/2023/workshop-list"),
                ("The 5th International Workshop on Eye and Gaze in Computer Vision", "CVPR 2023", "https://cvpr.thecvf.com/Conferences/2023/workshop-list"),
                ("The 4th Embodied AI Workshop", "CVPR 2023", "https://embodied-ai.org/"),
                ("Visual Pre-training for Robotics", "CVPR 2023", "https://vispr-workshop.github.io/"),
                ("To NeRF or Not to NeRF: A View Synthesis Challenge for Human Heads", "ICCV 2023", "https://sites.google.com/view/vschh/home"),
                ("Artificial Social Intelligence Workshop and Challenge", "ICCV 2023", "https://openaccess.thecvf.com/ICCV2023_workshops/menu"),
                ("Analysis and Modeling of Faces and Gestures", "ICCV 2023", "https://openaccess.thecvf.com/ICCV2023_workshops/menu"),
                ("The 4th Workshop on Visual Perception for Navigation in Human Environments", "ICCV 2023", "https://jrdb.erc.monash.edu.au/workshops/iccv2023"),
                ("The 11th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2023", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
                ("Ethics and Trust in Human-AI Collaboration: Socio-Technical Approaches", "IJCAI 2023", "https://sites.google.com/view/ethaics-2023/"),
                ("The 1st Workshop on Micro-Gesture Analysis for Hidden Emotion Understanding", "IJCAI 2023", "https://cv-ac.github.io/MiGA2023/"),
                ("AI & Human-Computer Interaction", "ICML 2023", "https://icml.cc/virtual/2023/workshop/21491"),
                ("Interactive Learning with Implicit Human Feedback", "ICML 2023", "https://icml.cc/virtual/2023/events/workshop"),
                ("Theory of Mind in Communicating Agents", "ICML 2023", "https://icml.cc/virtual/2023/events/workshop"),
                ("Gaze Meets Machine Learning", "NeurIPS 2023", "https://neurips.cc/virtual/2023/events/workshop"),
                ("The 4th International Workshop on Human-Centric Multimedia Analysis", "ACM MM 2023", "https://www.acmmm2023.org/workshops"),
                ("The 5th Workshop on Long-Term Human Motion Prediction", "ICRA 2023", "https://motionpredictionicra2023.github.io/"),
                ("Communicating Robot Learning across Human-Robot Interaction", "ICRA 2023", "https://www.icra2023.org/programme/workshops-tutorials"),
                ("The 2nd Workshop on Social Robot Navigation", "IROS 2023", "https://2023.ieee-iros.org/workshops-tutorials/"),
                ("The Next Step for Humanoids", "IROS 2023", "https://2023.ieee-iros.org/workshops-tutorials/"),
                ("Human Multi-Robot Interaction", "IROS 2023", "https://2023.ieee-iros.org/workshops-tutorials/"),
                ("The 6th Workshop on Ergonomic Physical Human-Robot Collaboration", "IROS 2023", "https://2023.ieee-iros.org/workshops-tutorials/"),
                ("Assistive Robotics for Citizens", "IROS 2023", "https://2023.ieee-iros.org/workshops-tutorials/"),
                ("Social Intelligence in Humans and Robots", "RSS 2023", "https://roboticsconference.org/2023/program/workshops/"),
                ("Toward Natural Motion Generation", "RSS 2023", "https://roboticsconference.org/2023/program/workshops/"),
                ("Frontiers Workshop: Digital Avatars: Risks, Harms, Barriers, Opportunities", "SIGGRAPH 2023", "https://faculty.eng.ufl.edu/jain/teaching/frontiers-workshop-digital-avatars-risks-harms-barriers-opportunities/"),
            ],
        ),
        (
            "2022",
            [
                ("Human-Centric Self-Supervised Learning", "AAAI 2022", "https://aaai.org/conference/aaai/aaai-22/ws22workshops/"),
                ("Interactive Machine Learning", "AAAI 2022", "https://aaai.org/conference/aaai/aaai-22/ws22workshops/"),
                ("Artificial Social Intelligence", "CVPR 2022", "https://cvpr2022.thecvf.com/workshop-schedule"),
                ("Joint 1st Ego4D and 10th EPIC Workshop on Egocentric Vision", "CVPR 2022", "https://ego4d-data.org/workshops/cvpr22/"),
                ("Human-Centered Intelligent Services", "CVPR 2022", "https://cvpr2022.thecvf.com/workshop-schedule"),
                ("The 3rd Workshop on Affective & Behavior Analysis in-the-Wild", "CVPR 2022", "https://cvpr2022.thecvf.com/workshop-schedule"),
                ("The 4th International Workshop on Eye and Gaze in Computer Vision", "CVPR 2022", "https://cvpr2022.thecvf.com/workshop-schedule"),
                ("The 3rd Embodied AI Workshop", "CVPR 2022", "https://embodied-ai.org/"),
                ("Human-Machine Collaboration and Teaming", "ICML 2022", "https://icml.cc/virtual/2022/workshop/13478"),
                ("Human-Centered AI", "NeurIPS 2022", "https://neurips.cc/virtual/2022/events/workshop"),
                ("Gaze Meets Machine Learning", "NeurIPS 2022", "https://gaze-meets-ml.github.io/gaze_ml_2022/"),
                ("Human Evaluation of Generative Models", "NeurIPS 2022", "https://neurips.cc/virtual/2022/workshop/49978"),
                ("Trustworthy and Socially Responsible Machine Learning for Embodied AI", "NeurIPS 2022", "https://neurips.cc/virtual/2022/workshop/49972"),
                ("The 3rd International Workshop on Human-Centric Multimedia Analysis", "ACM MM 2022", "https://hcma2022.github.io/"),
                ("The 4th Person in Context Workshop and Challenge", "ACM MM 2022", "https://www.sigmm.org/opentoc/PIC2022-TOC"),
                ("Facial Micro-Expression Analysis", "ACM MM 2022", "https://2022.acmmm.org/workshops/"),
                ("The 4th Workshop on Sensing, Understanding and Synthesizing Humans", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("People Analysis: From Face, Body and Fashion to 3D Virtual Avatars", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("Human Body, Hands, and Activities from Egocentric and Multi-View Cameras", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("Observing and Understanding Hands in Action", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("The 2nd Workshop on Cross-Modal Human-Robot Interaction", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("The 2nd International Ego4D Workshop", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("The 3rd Workshop on Visual Perception for Navigation in Human Environments", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("Sign Language Understanding", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("The 4th Workshop on Affective & Behavior Analysis in-the-Wild", "ECCV 2022", "https://eccv2022.ecva.net/program/workshop-schedule/"),
                ("The 10th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2022", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
                ("Communication in Human-AI Interactions", "IJCAI-ECAI 2022", "https://chai-workshop.github.io/"),
                ("The 4th Workshop on Long-Term Human Motion Prediction", "ICRA 2022", "https://motionpredictionicra2022.github.io/"),
                ("Social Robot Navigation: Advances and Evaluation", "ICRA 2022", "https://seanavbench.interactive-machines.com/"),
                ("Reinforcement Learning Meets Human-Robot Interaction, Control, and Formal Methods", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Social and Cognitive Interactions for Assistive Robotics", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Ergonomic Human-Robot Collaboration", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Artificial Intelligence for Social Robots Interacting with Humans in the Real World", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Robot Trust for Symbiotic Societies", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Human-Multi-Robot Systems: Challenges for Real World Applications", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Human Theory of Machines and Machine Theory of Mind for Human-Agent Teams", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Soft Robots for Humanity", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Assistive Robots in the Real World", "IROS 2022", "https://iros2022.org/program/workshops-and-tutorials/"),
                ("Close-Proximity Human-Robot Collaboration: Challenges and Opportunities", "RSS 2022", "https://roboticsconference.org/2022/program/workshops/"),
                ("Workshop on Social Intelligence in Humans and Robots", "RSS 2022", "https://social-intelligence-human-ai.github.io/"),
                ("Toward Robot Avatars: Perspectives on the ANA Avatar XPRIZE Competition", "RSS 2022", "https://roboticsconference.org/2022/program/workshops/"),
            ],
        ),
    ]
)


METHOD_LEVELS = OrderedDict(
    [
        (
            "Visual Appearance",
            [
                "Generalist Human Perception",
                "Discriminative Identity Understanding",
                "Controllable Human Generation",
            ],
        ),
        (
            "Spatial Geometry",
            ["Structured Geometry Modeling", "Renderable Avatar Modeling"],
        ),
        (
            "Kinematic Dynamics",
            ["Scalable Motion Modeling", "Human Video Animation"],
        ),
        (
            "Interaction Modeling",
            [
                "Human-Object Interaction",
                "Human-Scene Interaction",
                "Social Interaction",
            ],
        ),
        (
            "World Simulation",
            ["Human-Centered World Generation", "Actionable World Planning"],
        ),
        (
            "Embodied Agency",
            ["Generalist Humanoid Control", "Human-to-Agent Skill Transfer"],
        ),
    ]
)

PERSPECTIVE_GROUPS = OrderedDict(
    [
        (
            "Perspectives",
            ["Human-Centric Agentic AI"],
        ),
    ]
)

METHOD_SECTION_FILES = [
    "sections/4_appearance_geometry.tex",
    "sections/5_dynamics_interaction.tex",
    "sections/6_world_embodied.tex",
]

METHOD_TABLE_FILES = [
    "tables/summary_4_appearance_geometry.tex",
    "tables/summary_5_dynamics.tex",
    "tables/summary_5_interaction.tex",
    "tables/summary_6_world_embodied.tex",
]

DATA_GROUPS = OrderedDict(
    [
        (
            "Human Subject Resources",
            [
                "Visual Human Observation",
                "Multisensory Human Sensing",
                "Human Identity Understanding",
                "Renderable Human Geometry",
            ],
        ),
        (
            "Human Dynamics Resources",
            [
                "Human Video Generation and Animation",
                "Human Video Behavior Understanding",
                "Human Kinematic Motion Resources",
                "Human Gait Understanding",
                "Sport Analysis",
                "Virtual Try-On",
            ],
        ),
        (
            "Human Interaction Resources",
            [
                "Egocentric Procedural Activities",
                "Human-Object Interaction Data",
                "Human-Scene Interaction Data",
                "Social Interaction Data",
            ],
        ),
        (
            "Human Embodiment Resources",
            ["Human Data for Embodied AI", "Physical Humanoid Control"],
        ),
    ]
)

DATA_TABLE_CATEGORY = {
    "tables/summary_7_db_renderable.tex": "Renderable Human Geometry",
    "tables/summary_7_db_motion.tex": "Human Kinematic Motion Resources",
    "tables/summary_7_db_egocentric.tex": "Egocentric Procedural Activities",
    "tables/summary_7_db_embodied.tex": "Human Data for Embodied AI",
}

CITE_RE = re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\]\s*)*\{([^}]+)\}")
HREF_RE = re.compile(r"\\href\{([^}]+)\}\{[^}]*\}")
RESOURCE_META_RE = re.compile(
    r"\|\s*(Dataset\+Benchmark|Dataset|Benchmark)\s*\|\s*([^|]+?)\s*\|"
)


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        cut = None
        for index, char in enumerate(line):
            if char == "%" and (index == 0 or line[index - 1] != "\\"):
                cut = index
                break
        lines.append(line if cut is None else line[:cut])
    return "\n".join(lines)


def citation_keys(text: str) -> list[str]:
    keys: list[str] = []
    for match in CITE_RE.finditer(text):
        keys.extend(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def parse_bibtex(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    cursor = 0
    while True:
        match = re.search(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text[cursor:], re.S)
        if not match:
            break
        entry_type, key = match.group(1).lower(), match.group(2)
        body_start = cursor + match.end()
        depth = 1
        index = body_start
        quoted = False
        escaped = False
        while index < len(text) and depth:
            char = text[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted and char == "{":
                depth += 1
            elif not quoted and char == "}":
                depth -= 1
            index += 1
        body = text[body_start : index - 1]
        fields: dict[str, str] = {"ENTRYTYPE": entry_type, "ID": key}
        field_cursor = 0
        while field_cursor < len(body):
            field_match = re.search(r"([A-Za-z][\w-]*)\s*=\s*", body[field_cursor:])
            if not field_match:
                break
            field = field_match.group(1).lower()
            value_start = field_cursor + field_match.end()
            if value_start >= len(body):
                break
            opener = body[value_start]
            if opener == "{":
                value_depth = 1
                value_index = value_start + 1
                escaped = False
                while value_index < len(body) and value_depth:
                    char = body[value_index]
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == "{":
                        value_depth += 1
                    elif char == "}":
                        value_depth -= 1
                    value_index += 1
                value = body[value_start + 1 : value_index - 1]
            elif opener == '"':
                value_index = value_start + 1
                escaped = False
                while value_index < len(body):
                    char = body[value_index]
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == '"':
                        value_index += 1
                        break
                    value_index += 1
                value = body[value_start + 1 : value_index - 1]
            else:
                value_index = value_start
                while value_index < len(body) and body[value_index] not in ",\n":
                    value_index += 1
                value = body[value_start:value_index]
            fields[field] = value.strip()
            field_cursor = value_index
        entries[key] = fields
        cursor = index
    return entries


def latex_to_text(value: str) -> str:
    value = value.strip()
    while len(value) >= 2 and value[0] == "{" and value[-1] == "}":
        value = value[1:-1].strip()
    replacements = {
        r"\\&": "&",
        r"\\_": "_",
        r"\\%": "%",
        r"\\#": "#",
        "~": " ",
        "--": "-",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"\\(?:textit|textbf|emph|mathrm|mathbf|mathit)\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\(?:em|sc)\s+", "", value)
    value = value.replace("$", "")
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\\[A-Za-z]+", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def split_cells(row: str) -> list[str]:
    return [cell.strip() for cell in re.split(r"(?<!\\)&", row)]


def clean_row_name(cell: str) -> str:
    cell = CITE_RE.sub("", cell)
    cell = re.sub(r"\\rowcolor\{[^}]+\}", "", cell)
    cell = re.sub(r"\\textsuperscript\{([^}]+)\}", r"\1", cell)
    cell = re.sub(r"\\(?:textbf|textit)\{([^{}]+)\}", r"\1", cell)
    return latex_to_text(cell).strip()


def row_metadata(row: str, resource_type: str | None = None, meta_venue: str | None = None) -> dict:
    cells = split_cells(row)
    keys = citation_keys(row)
    if not keys or len(cells) < 3:
        return {}
    paper_links = HREF_RE.findall(cells[-2]) if len(cells) >= 2 else []
    web_links = HREF_RE.findall(cells[-1]) if cells else []
    return {
        "keys": keys,
        "name": clean_row_name(cells[0]),
        "venue": latex_to_text(cells[1]),
        "paper_links": paper_links,
        "web_links": web_links,
        "resource_type": resource_type,
        "meta_venue": latex_to_text(meta_venue or ""),
    }


def parse_active_table(path: Path, known_categories: Iterable[str]) -> tuple[dict[str, set[str]], dict[str, dict]]:
    categories = {name: set() for name in known_categories}
    metadata: dict[str, dict] = {}
    current_category: str | None = None
    pending_type: str | None = None
    pending_venue: str | None = None
    buffer: list[str] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.lstrip()
        if stripped.startswith("%"):
            meta_match = RESOURCE_META_RE.search(stripped)
            if meta_match:
                pending_type = meta_match.group(1).replace("+", " + ")
                pending_venue = meta_match.group(2).strip()
            continue
        line = strip_comments(raw_line).strip()
        if not line:
            continue
        for category in known_categories:
            if category in line and "Sec.~\\ref" in line:
                current_category = category
                break
        buffer.append(line)
        if "\\\\" not in line:
            continue
        row = " ".join(buffer)
        buffer = []
        parsed = row_metadata(row, pending_type, pending_venue)
        if not parsed:
            continue
        for key in parsed["keys"]:
            metadata[key] = merge_metadata(metadata.get(key), parsed)
            if current_category:
                categories[current_category].add(key)
        pending_type = None
        pending_venue = None
    return categories, metadata


def parse_all_table_rows(path: Path) -> dict[str, dict]:
    """Parse active and commented-out table rows to recover links for prose citations."""
    metadata: dict[str, dict] = {}
    row_buffer: list[str] = []
    collecting = False
    pending_type: str | None = None
    pending_venue: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.lstrip()
        meta_match = RESOURCE_META_RE.search(stripped)
        if meta_match:
            pending_type = meta_match.group(1).replace("+", " + ")
            pending_venue = meta_match.group(2).strip()
        if stripped.startswith("%"):
            normalized = re.sub(r"^%+\s?", "", stripped)
        else:
            normalized = strip_comments(raw_line).strip()
        if not collecting and CITE_RE.search(normalized) and "&" in normalized:
            collecting = True
            row_buffer = [normalized]
        elif collecting:
            row_buffer.append(normalized)
        if collecting and "\\\\" in normalized:
            parsed = row_metadata(" ".join(row_buffer), pending_type, pending_venue)
            for key in parsed.get("keys", []):
                metadata[key] = merge_metadata(metadata.get(key), parsed)
            collecting = False
            row_buffer = []
            pending_type = None
            pending_venue = None
    return metadata


def merge_metadata(existing: dict | None, incoming: dict) -> dict:
    if not existing:
        return {
            "title": incoming.get("title", ""),
            "name": incoming.get("name", ""),
            "venue": incoming.get("venue", ""),
            "paper_links": list(incoming.get("paper_links", [])),
            "web_links": list(incoming.get("web_links", [])),
            "resource_type": incoming.get("resource_type"),
            "meta_venue": incoming.get("meta_venue", ""),
        }
    merged = dict(existing)
    for field in ("title", "name", "venue", "resource_type", "meta_venue"):
        if not merged.get(field) and incoming.get(field):
            merged[field] = incoming[field]
    for field in ("paper_links", "web_links"):
        merged[field] = list(dict.fromkeys(merged.get(field, []) + incoming.get(field, [])))
    return merged


def strip_float_environments(text: str) -> str:
    """Remove floats whose citations describe illustrations rather than methods."""
    for environment in ("figure", "figure*", "wrapfigure", "table", "table*", "wraptable"):
        text = re.sub(
            rf"\\begin\{{{re.escape(environment)}\}}.*?\\end\{{{re.escape(environment)}\}}",
            "",
            text,
            flags=re.S,
        )
    return text


def extract_subsubsection_citations(path: Path, allowed: set[str]) -> tuple[dict[str, set[str]], set[str]]:
    text = strip_float_environments(strip_comments(path.read_text(encoding="utf-8")))
    matches = list(re.finditer(r"\\subsubsection\{([^}]+)\}", text))
    result = {name: set() for name in allowed}
    assigned: set[str] = set()
    for index, match in enumerate(matches):
        title = latex_to_text(match.group(1))
        next_heading = re.search(r"\\(?:subsubsection|subsection|section)\{", text[match.end() :])
        end = match.end() + next_heading.start() if next_heading else len(text)
        if title not in allowed:
            continue
        keys = set(citation_keys(text[match.end() : end]))
        result[title].update(keys)
        assigned.update(keys)
    return result, set(citation_keys(text)) - assigned


def extract_marked_citations(text: str, markers: list[str], end_marker: str | None = None) -> dict[str, set[str]]:
    clean = strip_comments(text)
    end_limit = clean.find(end_marker) if end_marker and end_marker in clean else len(clean)
    positions: list[tuple[int, str, int]] = []
    for marker in markers:
        token = f"\\textbf{{{marker}.}}"
        position = clean.find(token)
        if position < 0:
            raise ValueError(f"Could not find dataset category marker: {marker}")
        positions.append((position, marker, position + len(token)))
    positions.sort()
    result: dict[str, set[str]] = {}
    for index, (_, marker, content_start) in enumerate(positions):
        candidates = [end_limit]
        if index + 1 < len(positions):
            candidates.append(positions[index + 1][0])
        next_subsubsection = clean.find("\\subsubsection{", content_start)
        if next_subsubsection >= 0:
            candidates.append(next_subsubsection)
        content_end = min(candidate for candidate in candidates if candidate >= content_start)
        result[marker] = set(citation_keys(clean[content_start:content_end]))
    return result


def bib_paper_url(entry: dict[str, str]) -> str:
    url = latex_to_text(entry.get("url", ""))
    if url.startswith("http"):
        return url
    doi = latex_to_text(entry.get("doi", ""))
    if doi:
        return doi if doi.startswith("http") else f"https://doi.org/{doi}"
    eprint = latex_to_text(entry.get("eprint", ""))
    if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", eprint):
        return f"https://arxiv.org/abs/{eprint}"
    journal = latex_to_text(entry.get("journal", ""))
    arxiv_match = re.search(r"arXiv[: ](\d{4}\.\d{4,5})", journal, re.I)
    if arxiv_match:
        return f"https://arxiv.org/abs/{arxiv_match.group(1)}"
    return ""


def venue_name(entry: dict[str, str]) -> str:
    raw = latex_to_text(entry.get("booktitle") or entry.get("journal") or "")
    lower = raw.lower()
    mappings = [
        ("computer vision and pattern recognition", "CVPR"),
        ("international conference on computer vision", "ICCV"),
        ("european conference on computer vision", "ECCV"),
        ("neural information processing systems", "NeurIPS"),
        ("learning representations", "ICLR"),
        ("machine learning", "ICML"),
        ("artificial intelligence", "AAAI"),
        ("robotics and automation", "ICRA"),
        ("intelligent robots and systems", "IROS"),
        ("computer graphics and interactive techniques", "SIGGRAPH"),
        ("multimedia", "ACM MM"),
    ]
    for needle, short in mappings:
        if needle in lower:
            return short
    if lower.startswith("arxiv"):
        return "arXiv"
    return raw


def normalize_venue(table_venue: str, entry: dict[str, str]) -> str:
    year = latex_to_text(entry.get("year", ""))
    venue = table_venue.strip()
    venue = venue.replace("'", " ")
    venue = re.sub(r"\s+", " ", venue).strip()
    if venue and venue not in {"NA", "Not Mentioned"}:
        if re.search(r"\b\d{2}\b", venue):
            venue = re.sub(r"\b(\d{2})\b", lambda match: f"20{match.group(1)}", venue, count=1)
        if re.search(r"\b\d{2,4}\b", venue):
            return venue
        return f"{venue} {year}".strip()
    fallback = venue_name(entry)
    return f"{fallback} {year}".strip() or year or "-"


def title_prefix(title: str) -> str:
    if ":" in title:
        prefix = title.split(":", 1)[0].strip()
        if 1 <= len(prefix.split()) <= 8 and len(prefix) <= 70:
            return prefix
    return title


def infer_resource_type(title: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    lower = title.lower()
    has_dataset = "dataset" in lower or "data set" in lower
    has_benchmark = "benchmark" in lower
    if has_dataset and has_benchmark:
        return "Dataset + Benchmark"
    if has_benchmark:
        return "Benchmark"
    return "Dataset"


def website_links(links: Iterable[str]) -> list[dict[str, str]]:
    result = []
    seen = set()
    for url in (link for link in links if link.startswith("http")):
        canonical = url.rstrip("/").removesuffix(".git").lower()
        if canonical in DEAD_WEBSITE_URLS:
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        host = urllib.parse.urlparse(url).netloc.lower()
        if "github.com" in host or "gitlab" in host:
            kind = "github"
        elif "huggingface.co" in host:
            kind = "huggingface"
        else:
            kind = "homepage"
        result.append({"kind": kind, "url": url})
    return result


def build_record(key: str, bib: dict[str, dict[str, str]], metadata: dict[str, dict], resource: bool) -> dict:
    entry = bib.get(key, {})
    meta = metadata.get(key, {})
    title = meta.get("title") or latex_to_text(entry.get("title", "")) or meta.get("name") or key
    paper_links = meta.get("paper_links", [])
    paper_url = paper_links[0] if paper_links else bib_paper_url(entry)
    year = latex_to_text(entry.get("year", ""))
    table_venue = meta.get("meta_venue") if resource and meta.get("meta_venue") else meta.get("venue", "")
    record = {
        "bibkey": key,
        "name": meta.get("name") or title_prefix(title),
        "title": title,
        "year": year,
        "venue": normalize_venue(table_venue or "", entry),
        "paper_url": paper_url,
        "websites": website_links(meta.get("web_links", [])),
    }
    if resource:
        record["type"] = infer_resource_type(title, meta.get("resource_type"))
    return record


def build_supplemental_method_record(entry: dict) -> dict:
    required = ("bibkey", "category", "name", "title", "year", "venue", "paper_url")
    missing = [field for field in required if not entry.get(field)]
    if missing:
        raise ValueError(f"Supplemental method entry is missing {missing}: {entry}")
    return {
        "bibkey": entry["bibkey"],
        "name": entry["name"],
        "title": entry["title"],
        "year": str(entry["year"]),
        "venue": entry["venue"],
        "paper_url": entry["paper_url"],
        "websites": website_links(entry.get("websites", [])),
    }


def build_supplemental_resource_record(entry: dict) -> dict:
    required = ("bibkey", "category", "name", "title", "year", "venue", "paper_url")
    missing = [field for field in required if not entry.get(field)]
    if missing:
        raise ValueError(f"Supplemental resource entry is missing {missing}: {entry}")
    return {
        "bibkey": entry["bibkey"],
        "name": entry["name"],
        "title": entry["title"],
        "year": str(entry["year"]),
        "venue": entry["venue"],
        "paper_url": entry["paper_url"],
        "websites": website_links(entry.get("websites", [])),
        "type": infer_resource_type(entry["title"], entry.get("type")),
    }


def record_sort_key(record: dict) -> tuple[int, str]:
    venue_years = [int(year) for year in re.findall(r"\b20\d{2}\b", record.get("venue", ""))]
    year_match = re.search(r"\d{4}", record.get("year", ""))
    year = max(venue_years) if venue_years else (int(year_match.group()) if year_match else 0)
    return (-year, record.get("title", "").lower())


def md_escape(value: str) -> str:
    return html.escape(value, quote=False).replace("|", "\\|").replace("\n", " ")


def paper_link(url: str) -> str:
    return f'[:page_facing_up:]({url} "Paper page")' if url else "-"


def web_link_cell(websites: list[dict[str, str]]) -> str:
    if not websites:
        return "-"
    labels = {
        "github": ":octocat:",
        "homepage": ":house:",
        "huggingface": "🤗",
    }
    tooltips = {
        "github": "GitHub",
        "homepage": "Homepage",
        "huggingface": "Hugging Face",
    }
    return " ".join(
        f'[{labels[item["kind"]]}]({item["url"]} "{tooltips[item["kind"]]}")'
        for item in websites
    )


def method_table(records: list[dict], first_column: str = "Method") -> str:
    lines = [
        f"| {first_column} | Paper | Venue | Paper Page | Website |",
        "|---|---|:---:|:---:|:---:|",
    ]
    for record in records:
        lines.append(
            "| {name} | {title} | {venue} | {paper} | {website} |".format(
                name=md_escape(record["name"]),
                title=md_escape(record["title"]),
                venue=md_escape(record["venue"]),
                paper=paper_link(record["paper_url"]),
                website=web_link_cell(record["websites"]),
            )
        )
    return "\n".join(lines)


def resource_table(records: list[dict]) -> str:
    lines = [
        "| Resource | Type | Venue | Paper | Paper Page | Website |",
        "|---|:---:|:---:|---|:---:|:---:|",
    ]
    for record in records:
        lines.append(
            "| {name} | {type} | {venue} | {title} | {paper} | {website} |".format(
                name=md_escape(record["name"]),
                type=md_escape(record["type"]),
                venue=md_escape(record["venue"]),
                title=md_escape(record["title"]),
                paper=paper_link(record["paper_url"]),
                website=web_link_cell(record["websites"]),
            )
        )
    return "\n".join(lines)


def anchor(text: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", text.lower()).replace(" ", "-")


def blockquote(markdown: str) -> str:
    """Indent a generated Markdown block while preserving nested rendering."""
    return "\n".join(f"> {line}" if line else ">" for line in markdown.splitlines())


HISTORICAL_WORKSHOPS = (
    ("2014", "The 2nd International Workshop on Assistive Computer Vision and Robotics", "ECCV 2014", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
    ("2015", "The 3rd International Workshop on Assistive Computer Vision and Robotics", "ICCV 2015", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
    ("2016", "The 4th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2016", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
    ("2017", "The 5th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2017", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
    ("2018", "The 6th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2018", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
    ("2019", "The 7th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2019", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
    ("2019", "The 1st Workshop on Gaze Estimation and Prediction in the Wild (GAZE 2019)", "ICCV 2019", "https://gazeworkshop.github.io/2019/"),
    ("2019", "The 1st Workshop on Sensing, Understanding and Synthesizing Humans", "ICCV 2019", "https://sense-human.github.io/index_2019.html"),
    ("2019", "The 1st Workshop on Long-Term Human Motion Prediction", "ICRA 2019", "https://motionpredictionicra2019.github.io/"),
    ("2020", "The 8th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2020", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
    ("2020", "The 2nd International Workshop on Gaze Estimation and Prediction in the Wild (GAZE 2020)", "ECCV 2020", "https://eccv2020.eu/workshops/"),
    ("2020", "The 1st Embodied AI Workshop", "CVPR 2020", "https://embodied-ai.org/cvpr2020/"),
    ("2020", "The 2nd Workshop on Sensing, Understanding and Synthesizing Humans", "ECCV 2020", "https://sense-human.github.io/index_2020.html"),
    ("2020", "The 1st International Workshop on Human-centric Multimedia Analysis", "ACM MM 2020", "https://hcma2020.github.io/"),
    ("2020", "The 2nd Workshop on Long-Term Human Motion Prediction", "ICRA 2020", "https://motionpredictionicra2020.github.io/"),
    ("2021", "The 9th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2021", "https://iplab.dmi.unict.it/acvr2024/previous-editions.html"),
    ("2021", "The 3rd International Workshop on Gaze Estimation and Prediction in the Wild (GAZE 2021)", "CVPR 2021", "https://gazeworkshop.github.io/2021/"),
    ("2021", "The 2nd Embodied AI Workshop", "CVPR 2021", "https://embodied-ai.org/cvpr2021/"),
    ("2021", "The 3rd Workshop on Sensing, Understanding and Synthesizing Humans", "ICCV 2021", "https://sense-human.github.io/index_2021.html"),
    ("2021", "The 2nd International Workshop on Human-centric Multimedia Analysis", "ACM MM 2021", "https://hcma2021.github.io/"),
    ("2021", "The 3rd Workshop on Long-Term Human Motion Prediction", "ICRA 2021", "https://motionpredictionicra2021.github.io/"),
)


# A conference-wide list can verify that an event existed, but it is not a
# usable workshop link. Keep those records in the discovery inventory above
# while excluding them from the public page until a dedicated homepage or an
# exact conference-hosted event page is available.
GENERIC_WORKSHOP_PATHS = tuple(
    re.compile(pattern, flags=re.IGNORECASE)
    for pattern in (
        r"/conferences/\d{4}/(?:workshops|workshop-list)/?",
        r"/conference/aaai/aaai-\d+/workshop-list/?",
        r"/conference/aaai/aaai-\d+/ws\d+workshops/?",
        r"/aaai-\d+-conference/aaai-\d+-workshop-list/?",
        r"/virtual/\d{4}/events/workshop/?",
        r"/program/workshop-schedule/?",
        r"/workshop-schedule/?",
        r"/program/workshops/?",
        r"/\d{4}/program/workshops/?",
        r"/workshops/?",
        r"/workshops/index\.html",
        r"/workshops-and-tutorials/?",
        r"/workshops-tutorials/?",
        r"/program/workshops-and-tutorials/?",
        r"/programme/workshops-tutorials/?",
        r"/events/category/sessions/workshops-tutorials(?:/.*)?",
        r"/workshopstutorials\.html",
        r"/full-program/?",
        r"/program/technical-workshops/?",
        r"/iccv\d{4}_workshops/menu/?",
    )
)


EXCLUDED_WORKSHOP_RECORDS = {
    # The original domain now resolves to an unrelated page, and no active
    # workshop-specific replacement could be verified.
    ("Unsolved Problems in Social Robot Navigation", "RSS 2024"),
    # Entries removed during manual curation of the public workshop list.
    ("The 2nd International Workshop on Assistive Computer Vision and Robotics", "ECCV 2014"),
    ("The 3rd International Workshop on Assistive Computer Vision and Robotics", "ICCV 2015"),
    ("The 4th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2016"),
    ("The 5th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2017"),
    ("The 6th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2018"),
    ("The 7th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2019"),
    ("The 1st Workshop on Gaze Estimation and Prediction in the Wild (GAZE 2019)", "ICCV 2019"),
    ("The 8th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2020"),
    ("The 9th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2021"),
    ("The 3rd International Workshop on Gaze Estimation and Prediction in the Wild (GAZE 2021)", "CVPR 2021"),
    ("The 2nd Workshop on Advancing Artificial Intelligence through Theory of Mind", "AAAI 2026"),
    ("The 1st Workshop on Multi-Agent Robotic Systems: Scaling with Compositional Intelligence", "CVPR 2026"),
    ("4D Digital Twins: Real-to-Sim-to-Real for Physical AI", "CVPR 2026"),
    ("AI-Based Humanoid Robot Design and Control through the Lens of HRI, Evolution, and Biomechanics", "IJCAI-ECAI 2026"),
    ("The 4th Workshop on NeuroDesign in Human-Robot Interaction: The making of engaging HRI technology your brain can't resist", "ICRA 2026"),
    ("It's the Demos: The Role of Demonstration Quality in Imitation-Based Robot Manipulation", "RSS 2026"),
    ("Differentiable Physics for Graphics and AI", "SIGGRAPH 2026"),
    ("3D Digital Twin: Progress, Challenges, and Future Directions", "CVPR 2025"),
    ("Computer Vision for Mixed Reality", "CVPR 2025"),
    ("The 2nd Workshop on Multi-Agent Embodied Intelligent Systems Meet Generative-AI Era", "CVPR 2025"),
    ("The 1st Embodied Spatial Reasoning Workshop", "ICCV 2025"),
    ("The 13th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2025"),
    ("User-Aligned Assessment of Adaptive AI Systems", "IJCAI 2025"),
    ("Generative AI and Theory of Mind in Communicating Agents", "IJCAI 2025"),
    ("Embodied World Models for Decision Making", "NeurIPS 2025"),
    ("Embodied and Safe-Assured Robotic Systems", "NeurIPS 2025"),
    ("Advances in Social Robot Navigation: Planning, HRI, and Beyond", "ICRA 2025"),
    ("Multi-Agent Embodied Intelligent Systems Meet Foundation Models and Large-scale Datasets", "ICRA 2025"),
    ("Large Foundation Models for Interactive Robot Learning", "RSS 2025"),
    ("The 2nd Workshop on Computer Vision for Mixed Reality", "CVPR 2024"),
    ("Workshop on Human-Aligned Reinforcement Learning for Autonomous Agents and Robots", "ICRA 2024"),
    ("The 2nd Workshop on NeuroDesign in Human-Robot Interaction: The making of engaging HRI technology your brain can't resist", "ICRA 2024"),
    ("Workshop on Embodied Voices", "RSS 2024"),
    ("Robots That Help and Ask for Help", "RSS 2024"),
    ("Visual Pre-training for Robotics", "CVPR 2023"),
    ("The 11th International Workshop on Assistive Computer Vision and Robotics", "ICCV 2023"),
    ("Ethics and Trust in Human-AI Collaboration: Socio-Technical Approaches", "IJCAI 2023"),
    ("Human Evaluation of Generative Models", "NeurIPS 2022"),
    ("Trustworthy and Socially Responsible Machine Learning for Embodied AI", "NeurIPS 2022"),
    ("The 10th International Workshop on Assistive Computer Vision and Robotics", "ECCV 2022"),
    ("Communication in Human-AI Interactions", "IJCAI-ECAI 2022"),
    ("Social Robot Navigation: Advances and Evaluation", "ICRA 2022"),
}


def has_direct_workshop_page(title: str, venue: str, url: str) -> bool:
    """Return whether a record links to a workshop-specific public page."""
    if (title, venue) in EXCLUDED_WORKSHOP_RECORDS:
        return False
    path = urllib.parse.urlparse(url).path or "/"
    return not any(pattern.fullmatch(path) for pattern in GENERIC_WORKSHOP_PATHS)


ORDINAL_WORDS = {
    "first": "1st",
    "second": "2nd",
    "third": "3rd",
    "fourth": "4th",
    "fifth": "5th",
    "sixth": "6th",
    "seventh": "7th",
    "eighth": "8th",
    "ninth": "9th",
    "tenth": "10th",
    "eleventh": "11th",
    "twelfth": "12th",
    "thirteenth": "13th",
    "fourteenth": "14th",
}


def conference_name(venue: str) -> str:
    conference = re.sub(r"\s+\d{4}$", "", venue)
    return "IJCAI" if conference == "IJCAI-ECAI" else conference


def split_workshop_edition(title: str) -> tuple[str | None, int | None, str]:
    """Separate a leading official edition marker without rewriting the title."""
    numeric = re.match(r"^(?:The\s+)?(\d+(?:st|nd|rd|th))\s+(.+)$", title, flags=re.IGNORECASE)
    if numeric:
        label = numeric.group(1).lower()
        return label, int(re.match(r"\d+", label).group()), numeric.group(2).strip()

    words = "|".join(ORDINAL_WORDS)
    word = re.match(rf"^(?:The\s+)?({words})\s+(.+)$", title, flags=re.IGNORECASE)
    if word:
        label = ORDINAL_WORDS[word.group(1).lower()]
        return label, int(re.match(r"\d+", label).group()), word.group(2).strip()
    return None, None, title.strip()


WORKSHOP_SERIES_NAMES = {
    "joint 1st ego4d and 10th epic workshop on egocentric vision": "Joint Ego4D and EPIC Workshop on Egocentric Vision",
    "joint 3rd ego4d and 11th epic workshop on egocentric vision": "Joint Ego4D and EPIC Workshop on Egocentric Vision",
    "social intelligence in humans and robots": "Social Intelligence in Humans and Robots",
    "workshop on social intelligence in humans and robots": "Social Intelligence in Humans and Robots",
    "workshop on human motion generation (humogen)": "Workshop on Human Motion Generation (HuMoGen)",
    "workshop on human motion generation (humogen): new perspectives on simulation, animation, and vr applications": "Workshop on Human Motion Generation (HuMoGen)",
}


WORKSHOP_CATEGORIES = OrderedDict(
    [
        (
            "Human Perception and Understanding",
            (
                "AERO-HPR: Human Perception and Recognition in Aerial Surveillance",
                "Computer Vision for Biomechanics Workshop",
                "Gaze Meets Machine Learning",
                "Global 3D Human Poses",
                "International Workshop on Human-centric Multimedia Analysis",
                "Person in Context Workshop and Challenge",
                "PhysHuman: Physically Grounded Human Perception and Modeling",
                "Workshop on 3D Human Understanding",
                "Workshop on Human-Inspired Computer Vision",
                "Workshop on Micro-Gesture Analysis for Hidden Emotion Understanding",
                "Workshop on Sensing, Understanding and Synthesizing Humans",
            ),
        ),
        (
            "Digital Humans and Generative Modeling",
            (
                "3D Human Understanding: Towards Human-Centric World Models",
                "AI for Digital Human",
                "Frontiers Workshop: Digital Avatars: Risks, Harms, Barriers, Opportunities",
                "GENEA Workshop",
                "Generative AI for XR and Identity-based Applications",
                "Hybrid Dance Xplorations: Artist-Centric XR/AI Sandbox for Co-Creation and Performance",
                "Interactive Social Avatars with the 4th GENEA Gesture Generation Challenge",
                "Populating Empty Cities: Virtual Humans for Robotics and Autonomous Driving",
                "To NeRF or Not to NeRF: A View Synthesis Challenge for Human Heads",
                "Workshop on High-Fidelity Neural Actors",
                "Workshop on Human-Interactive Generation and Editing",
                "Workshop on Human Motion Generation (HuMoGen)",
                "Workshop on Photorealistic 3D Head Avatars",
            ),
        ),
        (
            "Human Motion, Behavior, and Social Interaction",
            (
                "CONTEXTUS: Understanding Multi-Actor Scene Interaction in Context",
                "Generalizing Natural Behavior: Retargeting Human or Animal Motion to Robotic Forms",
                "GROUND: Advancing Group Understanding and Robots' Adaptive Behavior",
                "Human Motion in Real-World and Clinical Settings",
                "Human-Scene Interaction: Towards Scene-Aware Motion, Communication, and Embodied Agents",
                "Joint Workshop on Human Behavior Analysis and Interaction for Emotional Intelligence, with the 4th MiGA Challenge",
                "RHOBIN Challenge on Reconstruction of Human-Object Interaction",
                "Social Intelligence in Humans and Robots",
                "Workshop and Challenge on Human Behavior Analysis for Emotion Understanding",
                "Workshop on Long-Term Human Motion Prediction",
                "Workshop on Multimodal Human Motion Analysis",
                "Workshop on Pedestrian Behavior Prediction",
                "Workshop on Skilled Activity Understanding, Assessment & Feedback Generation",
            ),
        ),
        (
            "Egocentric, Assistive, and Multimodal Intelligence",
            (
                "AI & Human-Computer Interaction",
                "EgoAct: The 1st Workshop on Egocentric Perception and Action for Robot Learning",
                "EgoMotion Workshop",
                "Generative AI for Sign Language",
                "Joint Ego4D and EPIC Workshop on Egocentric Vision",
                "Joint Egocentric Vision (EgoVis) Workshop",
                "Sense of Space: Multi-Sensory Modeling for Embodied Intelligence",
                "User-Centric AI for Assistance in At-Home Tasks",
                "Wearables AI: Towards Building Real-Time Multimodal Contextual Assistants",
                "Workshop on AI for Aging Rehabilitation and Intelligent Assisted Living",
                "Workshop on Vision-based Assistants in the Real-World",
                "Workshop on Visual Perception for Navigation in Human Environments",
            ),
        ),
        (
            "Human-Robot Interaction and Collaboration",
            (
                "Beyond the Lab: Human Behavior Monitoring and Modeling in In-the-Wild Human-Robot Interaction",
                "Human-Centered Robot Learning in the Era of Big Data and Large Models",
                "Human-in-the-Loop Robot Learning: Teaching, Correcting, and Adapting",
                "Human-Machine Collaboration and Teaming",
                "Human-Robot Contact and Manipulation",
                "Human-Robot-Scene Interaction and Collaboration",
                "Mechanisms for Mapping Human Input to Robots: From Robot Learning to Shared Control and Autonomy",
                "Safety and Normative Behaviors in Human-Robot Interaction",
                "Towards Collaborative Partners: Physical Human-Robot Interaction",
                "Workshop on Agents in Interaction, from Humans to Robots",
                "Workshop on Continual Robot Learning from Humans",
                "Workshop on Generative Modeling Meets Human-Robot Interaction",
            ),
        ),
        (
            "Embodied AI and Humanoid Robotics",
            (
                "Bridging Vision, Language, and Action: What's Missing in Actionable Visual Perception for Robotics",
                "Embodied Agent and Dialog",
                "Embodied AI Workshop",
                "Embodied Reasoning in Action: Embodied Reasoning for Robotic Manipulation",
                "From Lab Demos to Daily Tasks: Embodied Intelligence in the Wild",
                "Human-Centric Mobile Manipulation Workshop",
                "Humanoid Whole-Body Control: From Human Motion Understanding to Humanoid Locomotion",
                "IPA: Interactive Physical AI Workshop",
                "Observing and Acting as Dexterous Hands",
                "Perception and Decision Making for Athletic Humanoid Robotics",
                "Whole-Body Control and Bimanual Manipulation: Applications in Humanoids and Beyond",
                "Workshop on Dexterous Manipulation: Scalable Learning for Human-Level Skills",
                "Workshop on Embodied Humans: Symbiotic Intelligence between Virtual Humans and Humanoid Robots",
                "Workshop on Humanoid Agents",
            ),
        ),
        (
            "Foundation Models and Human-Centered AI",
            (
                "Foundation Models for 3D Humans",
                "Foundation Models for the Brain and Body",
                "Human-Centric Representation Learning",
                "Humans of Generative AI",
                "Multimodal Digital Agents Workshop",
                "Recent Trends in Human-Centric AI",
                "RobustifAI: Robustifying Generative AI for Reliable, Safe, and Human-Centric Systems",
                "Workshop on Foundation & Generative Models in Biometrics",
                "Workshop on Interactive Human-Centric Foundation Models",
            ),
        ),
    ]
)


def workshop_series_name(core_title: str) -> str:
    """Normalize verified title variants that refer to the same series."""
    return WORKSHOP_SERIES_NAMES.get(core_title.casefold(), core_title)


def render_research_lists_page() -> str:
    lines = [
        '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
        "",
        "# 📚 Awesome Research",
        "",
        "This page collects maintained paper lists and resource indexes spanning human-centric AI, digital humans, human motion, interaction, sensing, and humanoid intelligence.",
        "",
        "> **Organization note.** Resources are grouped by their primary research focus. Each entry links to the original list maintained by its respective authors or community.",
        "",
    ]

    for category, resources in AWESOME_RESEARCH_LISTS.items():
        lines.extend([f"## {category}", ""])
        for name, url, link_label in resources:
            lines.append(f"- **{name}**: [{link_label}]({url}).")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
            "",
        ]
    )
    return "\n".join(lines)


def render_academic_presentations_page() -> str:
    lines = [
        '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
        "",
        "# 🎥 Academic Presentations",
        "",
        "This page curates publicly accessible talks, tutorials, keynotes, seminars, guest lectures, symposia, and workshop recordings that offer broad perspectives on human-centric AI rather than presentations centered on a single paper.",
        "",
        "> **Organization note.** Videos are grouped by their primary theme rather than assigned exclusively to one taxonomy level, since many talks connect human perception, motion, interaction, world modeling, and embodied agency.",
        "",
        "> For multi-lecture courses with a sustained syllabus, see [Open Courseware](open-courseware.md).",
        "",
        "## Contents",
        "",
        *[
            f"- [{category}](#{anchor(category)})"
            for category in ACADEMIC_PRESENTATIONS
        ],
        "",
    ]

    for category, talks in ACADEMIC_PRESENTATIONS.items():
        lines.extend(
            [
                f'<a id="{anchor(category)}"></a>',
                "",
                f"## {category}",
                "",
                "| Year | Format | Talk | Speaker / Event | Focus |",
                "|:---:|:---|:---|:---|:---|",
            ]
        )
        for year, talk_type, title, video_url, speaker, event, event_url, focus in sorted(
            talks, key=lambda item: item[0], reverse=True
        ):
            lines.append(
                f"| {year} | {talk_type} | [{title}]({video_url}) | "
                f"{speaker}<br>[{event}]({event_url}) | {focus} |"
            )
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
            "",
        ]
    )
    return "\n".join(lines)


def render_open_courseware_page() -> str:
    lines = [
        '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
        "",
        "# 📖 Open Courseware",
        "",
        "This page is reserved for publicly accessible, multi-lecture courses with a sustained syllabus and a substantial sequence of classes. Individual guest lectures, tutorials, keynotes, and seminars are collected under [Academic Presentations](academic-presentations.md).",
        "",
        "> **Inclusion scope.** A resource belongs here only when it provides a coherent curriculum delivered across multiple classes, rather than a short thematic lecture or a collection of independent talks.",
        "",
    ]

    for course in OPEN_COURSEWARE:
        lines.extend(
            [
                f"### [{course['title']}]({course['course_url']})",
                "",
                f"**Offering:** {course['period']}  ",
                f"**Instructors:** {course['instructors']}  ",
                f"**Institution:** {course['institution']}  ",
                f"**Access:** [Course website]({course['course_url']}) | [Video playlist]({course['video_url']})",
                "",
                course["coverage"],
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
            "",
        ]
    )
    return "\n".join(lines)


def render_workshop_page() -> str:
    discovered_rows = list(HISTORICAL_WORKSHOPS) + [
        (year, title, venue, url)
        for year, workshops in WORKSHOPS_BY_YEAR.items()
        for title, venue, url in workshops
    ]
    raw_rows = [
        row
        for row in discovered_rows
        if has_direct_workshop_page(row[1], row[2], row[3])
    ]
    candidates: dict[str, list[dict]] = {}
    for year, title, venue, url in raw_rows:
        conference = conference_name(venue)
        _, _, core_title = split_workshop_edition(title)
        series_name = workshop_series_name(core_title)
        candidates.setdefault(series_name.casefold(), []).append(
            {
                "title": title,
                "core_title": series_name,
                "conference": conference,
                "year": int(year),
                "url": url,
            }
        )

    workshops = []
    for records in candidates.values():
        records.sort(key=lambda item: (-item["year"], item["conference"], item["url"]))
        workshops.append(
            {
                "name": records[0]["core_title"],
                "latest_year": max(record["year"] for record in records),
                "records": records,
            }
        )

    category_by_name = {
        name.casefold(): category
        for category, names in WORKSHOP_CATEGORIES.items()
        for name in names
    }
    categorized_workshops = OrderedDict(
        (category, []) for category in WORKSHOP_CATEGORIES
    )
    for workshop in workshops:
        category = category_by_name.get(workshop["name"].casefold())
        if category is None:
            raise ValueError(f"Uncategorized workshop series: {workshop['name']}")
        categorized_workshops[category].append(workshop)

    lines = [
        '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
        "",
        "# 🧑‍🏫 Workshop Collections",
        "",
        "This page presents a thematic collection of human-centric, egocentric, and embodied AI workshops. Recurring workshops are consolidated across host conferences after removing edition markers and reconciling verified title variants from the same series.",
        "",
        "> **Organization note.** Each workshop appears under one broad research theme. Within each theme, series are ordered by their most recent year, while editions within each series are listed from newest to oldest. Every link is labeled by its host conference and year.",
        "",
    ]

    for category, category_workshops in categorized_workshops.items():
        lines.extend([f"## {category}", ""])
        for workshop in sorted(
            category_workshops,
            key=lambda item: (-item["latest_year"], item["name"].casefold()),
        ):
            edition_links = ", ".join(
                f"[{record['conference']}{record['year']}]({record['url']})"
                for record in workshop["records"]
            )
            lines.append(f"- **{workshop['name']}**: {edition_links}.")
        lines.append("")

    lines.extend(["---", "", '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>', ""])
    return "\n".join(lines)


def render_markdown_pages(index: dict) -> dict[str, str]:
    arxiv_badge_image = '<img src="https://img.shields.io/badge/arXiv-Survey-B31B1B?logo=arxiv&logoColor=white" alt="arXiv">'
    arxiv_badge = arxiv_badge_image
    if SURVEY_ARXIV_URL:
        arxiv_badge = f'<a href="{SURVEY_ARXIV_URL}">{arxiv_badge_image}</a>'

    badge_line = " ".join(
        [
            '<a href="https://awesome.re"><img src="https://img.shields.io/badge/Awesome-fc60a8?logo=awesomelists&logoColor=white" alt="Awesome"></a>',
            '<a href="https://cseeyangchen.github.io/Human-Centric-AI/homepage/"><img src="https://img.shields.io/badge/Homepage-2f766f?logo=homeassistant&logoColor=white" alt="Homepage"></a>',
            f'<img src="https://komarev.com/ghpvc/?username={VISITOR_COUNTER_ID}&label=Visitors&color=2563eb&style=flat" alt="Visitors">',
            f'<a href="{GITHUB_REPOSITORY_URL}"><img src="https://img.shields.io/github/stars/{GITHUB_REPOSITORY}?label=Stars&logo=github&color=f59e0b" alt="Stars"></a>',
            f'<a href="{GITHUB_REPOSITORY_URL}/forks"><img src="https://img.shields.io/github/forks/{GITHUB_REPOSITORY}?label=Forks&logo=github&color=0f766e" alt="Forks"></a>',
            arxiv_badge,
            f'<a href="{GITHUB_REPOSITORY_URL}/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>',
            f'<a href="{GITHUB_REPOSITORY_URL}/commits/main"><img src="https://img.shields.io/github/last-commit/{GITHUB_REPOSITORY}?label=Last%20updated&color=64748b" alt="Last updated"></a>',
        ]
    )

    lines = [
        '<h1 align="center"><img src="assets/human-centric-resources-logo-v4.png" width="58" height="58" align="absmiddle" alt="Human-Centric AI Resources logo">&nbsp; Human-Centric AI Resources</h1>',
        "",
        '<p align="center"><b>An open, community-driven hub for human-centric AI.</b></p>',
        "",
        f'<p align="center">{badge_line}</p>',
        "",
        '<p align="center">',
        '  <img src="assets/survey-overview.png" width="100%" alt="Overview of Human-Centric Intelligence in the Era of Foundation Models">',
        "</p>",
        "",
        "Human-Centric AI Resources is an open and evolving hub that brings together academic knowledge, research infrastructure, community learning materials, and curated literature across human-centric AI. The accompanying survey provides a structured perspective through its six-level human context taxonomy, while this repository extends beyond the survey to support broader resource discovery and community curation.",
        "",
        "> [!TIP]",
        "> **Join the community.** We welcome everyone interested in human-centric AI to help maintain and enrich this open resource hub. If you are interested in getting involved, feel free to contact us using the details at the bottom of this page.",
        "",
        "## 🧭 Contents",
        "",
        "- [News](#news)",
        "- [Academic Knowledge](#academic-knowledge)",
        "- [Research Infrastructure](#research-infrastructure)",
        "- [Community Learning Hubs](#community-learning-hubs)",
        "- [Citation](#citation)",
        "- [Contact](#contact)",
        "- [License](#license)",
        "",
        '<a id="news"></a>',
        "",
        "## 📢 News",
        "",
        "- **2026-08-10:** Our [project homepage](https://cseeyangchen.github.io/Human-Centric-AI/homepage/) is now live.",
        "- **2026-08-08:** First resource release.",
        "",
        '<a id="academic-knowledge"></a>',
        "",
        "## 🎓 Academic Knowledge",
        "",
        "- 🔭 [**Awesome Research**](resources/awesome-research.md)",
        "- 🎟️ [**Workshop Collections**](resources/workshop-collections.md)",
        "- 📖 [**Open Courseware**](resources/open-courseware.md)",
        "- 🎙️ [**Academic Presentations**](resources/academic-presentations.md)",
        "",
        '<a id="research-infrastructure"></a>',
        "",
        "## 🧰 Research Infrastructure",
        "",
        "- 🧍 [**Human Models and Toolkits**](resources/human-models-and-toolkits.md)",
        "- 🔧 [**Practical Tools**](resources/practical-tools.md)",
        "- 🧪 [**Simulation and Evaluation**](resources/simulation-and-evaluation.md)",
        "",
        '<a id="community-learning-hubs"></a>',
        "",
        "## 🌐 Community Learning Hubs",
        "",
        "- 🧑 [**LearningHumans**](https://github.com/IsshikiHugh/LearningHumans)",
        "- 🏃 [**LearningMotion**](https://github.com/phj128/LearningMotion)",
        "- 📘 [**Meshcapade Body Modeling Wiki**](https://github.com/Meshcapade/wiki)",
        "",
    ]

    paper_lines = [
        '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
        "",
        "# 📚 Awesome Human-Centric AI Survey Resources",
        "",
        "This page brings together the papers, datasets, and benchmarks organized in **Human-Centric Intelligence in the Era of Foundation Models: A Survey**.",
        "",
        "## Contents",
        "",
        "- [Paper Resources](#paper-resources)",
        "- [Datasets and Benchmarks](#datasets-and-benchmarks)",
        "",
        '<a id="paper-resources"></a>',
        "",
        "## Paper Resources",
        "",
        "The paper index combines works cited in the Chapter 4--6 method discussions, works listed in the corresponding method tables, and verified post-survey updates. Broader perspective papers are listed separately from the six method levels. Each level and subcategory is collapsed by default for faster navigation.",
        "",
        "### Contents",
        "",
        *[
            f"- [{ROMAN_NUMERALS[level_number - 1]}. {level}](#{anchor(level)})"
            for level_number, level in enumerate(METHOD_LEVELS, start=1)
        ],
        *[
            f"- [{ROMAN_NUMERALS[len(METHOD_LEVELS) + group_number - 1]}. {group}](#{anchor(group)})"
            for group_number, group in enumerate(PERSPECTIVE_GROUPS, start=1)
        ],
        "",
    ]

    for level_number, (level, categories) in enumerate(METHOD_LEVELS.items(), start=1):
        level_records = index["method_papers"][level]
        level_index = ROMAN_NUMERALS[level_number - 1]
        level_icon = f"../{METHOD_LEVEL_ICONS[level]}"
        paper_lines.extend(
            [
                f'<a id="{anchor(level)}"></a>',
                "",
                "<details>",
                f'<summary><img src="{level_icon}" width="28" height="28" align="absmiddle" alt=""> &nbsp; <b>{level_index}. {level}</b></summary>',
                "",
            ]
        )
        for category_number, category in enumerate(categories, start=1):
            records = level_records[category]
            category_block = "\n".join(
                [
                    "<details>",
                    f"<summary><b>{level_index}.{category_number}</b> &nbsp; {category}</summary>",
                    "",
                    method_table(records),
                    "",
                    "</details>",
                ]
            )
            paper_lines.extend(
                [
                    blockquote(category_block),
                    "",
                ]
            )
        paper_lines.extend(["</details>", ""])

    for group_number, (group, categories) in enumerate(PERSPECTIVE_GROUPS.items(), start=1):
        group_index = ROMAN_NUMERALS[len(METHOD_LEVELS) + group_number - 1]
        group_records = index["perspective_papers"][group]
        paper_lines.extend(
            [
                f'<a id="{anchor(group)}"></a>',
                "",
                "<details>",
                f"<summary>💡 &nbsp; <b>{group_index}. {group}</b></summary>",
                "",
                "Perspective papers introduce broader paradigms, conceptual frameworks, or research agendas and are therefore kept separate from task-specific methods.",
                "",
            ]
        )
        for category_number, category in enumerate(categories, start=1):
            records = group_records[category]
            category_block = "\n".join(
                [
                    "<details>",
                    f"<summary><b>{group_index}.{category_number}</b> &nbsp; {category}</summary>",
                    "",
                    method_table(records, "Perspective"),
                    "",
                    "</details>",
                ]
            )
            paper_lines.extend([blockquote(category_block), ""])
        paper_lines.extend(["</details>", ""])

    paper_lines.extend(
        [
            "---",
            "",
        ]
    )

    dataset_lines = [
        '<a id="datasets-and-benchmarks"></a>',
        "",
        "## Datasets and Benchmarks",
        "",
        "Resources follow the organization used in Chapter 7 of the survey. Each resource group and subcategory is collapsed by default, and duplicate BibTeX entries are removed within each table.",
        "",
        "### Contents",
        "",
        *[
            f"- [{ROMAN_NUMERALS[group_number - 1]}. {group}](#{anchor(group)})"
            for group_number, group in enumerate(DATA_GROUPS, start=1)
        ],
        "",
    ]
    for group_number, (group, categories) in enumerate(DATA_GROUPS.items(), start=1):
        group_index = ROMAN_NUMERALS[group_number - 1]
        group_icon = f"../{DATA_GROUP_ICONS[group]}"
        dataset_lines.extend(
            [
                f'<a id="{anchor(group)}"></a>',
                "",
                "<details>",
                f'<summary><img src="{group_icon}" width="24" height="24" align="absmiddle" alt=""> &nbsp; <b>{group_index}. {group}</b></summary>',
                "",
            ]
        )
        for category_number, category in enumerate(categories, start=1):
            records = index["datasets_and_benchmarks"][group][category]
            category_block = "\n".join(
                [
                    "<details>",
                    f"<summary><b>{group_index}.{category_number}</b> &nbsp; {category}</summary>",
                    "",
                    resource_table(records),
                    "",
                    "</details>",
                ]
            )
            dataset_lines.extend(
                [
                    blockquote(category_block),
                    "",
                ]
            )
        dataset_lines.extend(["</details>", ""])

    dataset_lines.extend(
        [
            "---",
            "",
            '<p align="center"><a href="../README.md">&larr; Back to the main README</a></p>',
            "",
        ]
    )

    lines.extend(
        [
            '<a id="citation"></a>',
            "",
            "## ✍️ Citation",
            "",
            "If this resource collection is useful in your research, please cite the accompanying survey:",
            "",
            "```bibtex",
            "",
            "```",
            "",
            '<a id="contact"></a>',
            "",
            "## 📧 Contact",
            "",
            "For questions, suggestions, or collaboration inquiries, please contact the project lead, **Yang Chen**:",
            "",
            "- **Email:** [cs-yang.chen@connect.polyu.hk](mailto:cs-yang.chen@connect.polyu.hk)",
            "- **WeChat:** `cs-yangchen` (please include your name, institutional affiliation, and reason for contacting in the friend request)",
            "",
            '<a id="license"></a>',
            "",
            "## 📜 License",
            "",
            "Source code is licensed under the [MIT License](LICENSES/MIT.txt). Original documentation, curated resource metadata, and the authorized survey figures are licensed under [CC BY 4.0](LICENSES/CC-BY-4.0.txt). Logos, unlisted visual assets, and third-party materials may be subject to separate terms. See [LICENSE](LICENSE) and [Third-Party Notices](homepage/THIRD_PARTY_NOTICES.md) for the complete scope.",
            "",
            "---",
            "",
            '<p align="center">',
            '  <strong>⭐ If this project helps you, please give us a Star!</strong><br>',
            '  <sub>Curated and maintained by <a href="https://lumen-lab-polyu.github.io/"><strong>Lumen Lab</strong></a> @ <a href="https://www.polyu.edu.hk/"><strong>The Hong Kong Polytechnic University</strong></a></sub>',
            "</p>",
            "",
        ]
    )
    return {
        "README.md": "\n".join(lines),
        "resources/awesome-research.md": render_research_lists_page(),
        "resources/awesome-human-centric-ai-survey-resources.md": "\n".join(paper_lines + dataset_lines),
        "resources/academic-presentations.md": render_academic_presentations_page(),
        "resources/workshop-collections.md": render_workshop_page(),
    }


def build_index(
    survey_root: Path,
    overrides: dict[str, dict] | None = None,
    supplemental_methods: list[dict] | None = None,
    supplemental_perspectives: list[dict] | None = None,
    supplemental_resources: list[dict] | None = None,
) -> dict:
    bib = parse_bibtex(survey_root / "reference.bib")
    method_categories = {category for categories in METHOD_LEVELS.values() for category in categories}
    data_categories = {category for categories in DATA_GROUPS.values() for category in categories}

    all_table_metadata: dict[str, dict] = {}
    for relative in METHOD_TABLE_FILES + list(DATA_TABLE_CATEGORY):
        for key, meta in parse_all_table_rows(survey_root / relative).items():
            all_table_metadata[key] = merge_metadata(all_table_metadata.get(key), meta)
    method_keys = {category: set() for category in method_categories}
    unassigned_method_citations: dict[str, list[str]] = {}
    for relative in METHOD_SECTION_FILES:
        extracted, unassigned = extract_subsubsection_citations(survey_root / relative, method_categories)
        for category, keys in extracted.items():
            method_keys[category].update(keys)
        if unassigned:
            unassigned_method_citations[relative] = sorted(unassigned)

    for relative in METHOD_TABLE_FILES:
        active, active_meta = parse_active_table(survey_root / relative, method_categories)
        for category, keys in active.items():
            method_keys[category].update(keys)
        for key, meta in active_meta.items():
            all_table_metadata[key] = merge_metadata(all_table_metadata.get(key), meta)

    for key, category in METHOD_CATEGORY_OVERRIDES.items():
        for keys in method_keys.values():
            keys.discard(key)
        method_keys[category].add(key)

    evaluation_text = (survey_root / "sections/7_evaluation.tex").read_text(encoding="utf-8")
    data_keys = extract_marked_citations(
        evaluation_text,
        [category for categories in DATA_GROUPS.values() for category in categories],
        end_marker="\\subsection{Metrics}",
    )
    for relative, category in DATA_TABLE_CATEGORY.items():
        active, active_meta = parse_active_table(survey_root / relative, data_categories)
        row_keys = set()
        for keys in active.values():
            row_keys.update(keys)
        # Resource tables do not contain subsection group headers; all active rows
        # belong to the category selected by the surrounding Chapter 7 discussion.
        if not row_keys:
            row_keys.update(active_meta)
        data_keys[category].update(row_keys)
        for key, meta in active_meta.items():
            merged = merge_metadata(all_table_metadata.get(key), meta)
            # In the dataset index, the resource-table label and Dataset/Benchmark
            # annotation are more specific than a method name from Chapters 4--6.
            for field in ("name", "resource_type", "meta_venue"):
                if meta.get(field):
                    merged[field] = meta[field]
            all_table_metadata[key] = merged

    # Explicit corrections are applied last so that verified resource names and
    # links can refine automatically parsed table metadata without touching TeX.
    for key, override in (overrides or {}).items():
        override_meta = {
            "title": override.get("title", ""),
            "paper_links": [override["paper_url"]] if override.get("paper_url") else [],
            "web_links": override.get("websites", []),
            "name": override.get("name", ""),
            "venue": override.get("venue", ""),
            "resource_type": override.get("type"),
            "meta_venue": override.get("venue", ""),
        }
        merged = merge_metadata(all_table_metadata.get(key), override_meta)
        for field in ("title", "name", "resource_type", "venue", "meta_venue"):
            if override_meta.get(field):
                merged[field] = override_meta[field]
        all_table_metadata[key] = merged

    missing_bib = sorted(
        {
            key
            for keys in list(method_keys.values()) + list(data_keys.values())
            for key in keys
            if key not in bib
        }
    )

    method_output: dict[str, dict[str, list[dict]]] = OrderedDict()
    for level, categories in METHOD_LEVELS.items():
        method_output[level] = OrderedDict()
        for category in categories:
            records = [build_record(key, bib, all_table_metadata, False) for key in method_keys[category]]
            method_output[level][category] = sorted(records, key=record_sort_key)

    category_to_level = {
        category: level for level, categories in METHOD_LEVELS.items() for category in categories
    }
    supplemental_ids: set[str] = set()
    indexed_paper_urls = {
        record["paper_url"]
        for level in method_output.values()
        for records in level.values()
        for record in records
        if record["paper_url"]
    }
    for entry in supplemental_methods or []:
        category = entry.get("category", "")
        if category not in category_to_level:
            raise ValueError(f"Unknown supplemental method category: {category}")
        record = build_supplemental_method_record(entry)
        if record["bibkey"] in supplemental_ids or record["bibkey"] in bib:
            raise ValueError(f"Duplicate supplemental method key: {record['bibkey']}")
        if record["paper_url"] in indexed_paper_urls:
            raise ValueError(f"Duplicate supplemental method paper: {record['paper_url']}")
        supplemental_ids.add(record["bibkey"])
        indexed_paper_urls.add(record["paper_url"])
        level = category_to_level[category]
        method_output[level][category].append(record)

    for level in method_output.values():
        for category, records in level.items():
            level[category] = sorted(records, key=record_sort_key)

    perspective_output: dict[str, dict[str, list[dict]]] = OrderedDict()
    for group, categories in PERSPECTIVE_GROUPS.items():
        perspective_output[group] = OrderedDict((category, []) for category in categories)

    perspective_category_to_group = {
        category: group for group, categories in PERSPECTIVE_GROUPS.items() for category in categories
    }
    supplemental_perspective_ids: set[str] = set()
    for entry in supplemental_perspectives or []:
        category = entry.get("category", "")
        if category not in perspective_category_to_group:
            raise ValueError(f"Unknown supplemental perspective category: {category}")
        record = build_supplemental_method_record(entry)
        if (
            record["bibkey"] in supplemental_perspective_ids
            or record["bibkey"] in supplemental_ids
            or record["bibkey"] in bib
        ):
            raise ValueError(f"Duplicate supplemental perspective key: {record['bibkey']}")
        if record["paper_url"] in indexed_paper_urls:
            raise ValueError(f"Duplicate supplemental perspective paper: {record['paper_url']}")
        supplemental_perspective_ids.add(record["bibkey"])
        indexed_paper_urls.add(record["paper_url"])
        group = perspective_category_to_group[category]
        perspective_output[group][category].append(record)

    for group in perspective_output.values():
        for category, records in group.items():
            group[category] = sorted(records, key=record_sort_key)

    data_output: dict[str, dict[str, list[dict]]] = OrderedDict()
    for group, categories in DATA_GROUPS.items():
        data_output[group] = OrderedDict()
        for category in categories:
            records = [build_record(key, bib, all_table_metadata, True) for key in data_keys[category]]
            data_output[group][category] = sorted(records, key=record_sort_key)

    category_to_group = {
        category: group for group, categories in DATA_GROUPS.items() for category in categories
    }
    supplemental_resource_ids: set[str] = set()
    indexed_resource_urls = {
        record["paper_url"]
        for group in data_output.values()
        for records in group.values()
        for record in records
        if record["paper_url"]
    }
    for entry in supplemental_resources or []:
        category = entry.get("category", "")
        if category not in category_to_group:
            raise ValueError(f"Unknown supplemental resource category: {category}")
        record = build_supplemental_resource_record(entry)
        if (
            record["bibkey"] in supplemental_resource_ids
            or record["bibkey"] in supplemental_ids
            or record["bibkey"] in supplemental_perspective_ids
            or record["bibkey"] in bib
        ):
            raise ValueError(f"Duplicate supplemental resource key: {record['bibkey']}")
        if record["paper_url"] in indexed_resource_urls:
            raise ValueError(f"Duplicate supplemental resource paper: {record['paper_url']}")
        supplemental_resource_ids.add(record["bibkey"])
        indexed_resource_urls.add(record["paper_url"])
        group = category_to_group[category]
        data_output[group][category].append(record)

    for group in data_output.values():
        for category, records in group.items():
            group[category] = sorted(records, key=record_sort_key)

    unique_method = {key for keys in method_keys.values() for key in keys} | supplemental_ids
    unique_perspective = supplemental_perspective_ids
    unique_data = {key for keys in data_keys.values() for key in keys} | supplemental_resource_ids
    unresolved_paper_links = sorted(
        record["bibkey"]
        for level in method_output.values()
        for records in level.values()
        for record in records
        if not record["paper_url"]
    )
    unresolved_perspective_links = sorted(
        record["bibkey"]
        for group in perspective_output.values()
        for records in group.values()
        for record in records
        if not record["paper_url"]
    )
    unresolved_resource_links = sorted(
        record["bibkey"]
        for group in data_output.values()
        for records in group.values()
        for record in records
        if not record["paper_url"]
    )

    return {
        "generated_on": date.today().isoformat(),
        "summary": {
            "unique_method_papers": len(unique_method),
            "categorized_method_entries": sum(
                len(records) for level in method_output.values() for records in level.values()
            ),
            "unique_perspective_papers": len(unique_perspective),
            "categorized_perspective_entries": sum(
                len(records) for group in perspective_output.values() for records in group.values()
            ),
            "unique_resources": len(unique_data),
            "categorized_resource_entries": sum(
                len(records) for group in data_output.values() for records in group.values()
            ),
        },
        "method_papers": method_output,
        "perspective_papers": perspective_output,
        "datasets_and_benchmarks": data_output,
        "audit": {
            "missing_bib_entries": missing_bib,
            "unassigned_method_citations": unassigned_method_citations,
            "method_entries_without_paper_url": unresolved_paper_links,
            "perspective_entries_without_paper_url": unresolved_perspective_links,
            "resource_entries_without_paper_url": unresolved_resource_links,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--survey-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    overrides: dict[str, dict] = {}
    for filename in ("link_overrides.json", "website_overrides.json", "venue_overrides.json"):
        overrides_path = repo_root / "data" / filename
        if not overrides_path.exists():
            continue
        for key, value in json.loads(overrides_path.read_text(encoding="utf-8")).items():
            overrides[key] = {**overrides.get(key, {}), **value}
    supplemental_path = repo_root / "data" / "supplemental_methods.json"
    supplemental_methods = (
        json.loads(supplemental_path.read_text(encoding="utf-8"))
        if supplemental_path.exists()
        else []
    )
    supplemental_perspectives_path = repo_root / "data" / "supplemental_perspectives.json"
    supplemental_perspectives = (
        json.loads(supplemental_perspectives_path.read_text(encoding="utf-8"))
        if supplemental_perspectives_path.exists()
        else []
    )
    supplemental_resources_path = repo_root / "data" / "supplemental_resources.json"
    supplemental_resources = (
        json.loads(supplemental_resources_path.read_text(encoding="utf-8"))
        if supplemental_resources_path.exists()
        else []
    )
    index = build_index(
        args.survey_root.resolve(),
        overrides,
        supplemental_methods,
        supplemental_perspectives,
        supplemental_resources,
    )
    (repo_root / "data").mkdir(parents=True, exist_ok=True)
    (repo_root / "data" / "resources.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for relative_path, content in render_markdown_pages(index).items():
        output_path = repo_root / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    print(json.dumps(index["summary"], indent=2))
    print(json.dumps(index["audit"], indent=2))


if __name__ == "__main__":
    main()
