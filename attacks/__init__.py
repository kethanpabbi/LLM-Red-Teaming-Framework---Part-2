from attacks.prompt_injection import JailbreakAttacks, SystemPromptLeakAttacks
from attacks.pii_leakage import PIILeakageAttacks, TrainingDataExtractionAttacks
from attacks.alignment_bypass import AlignmentBypassAttacks

ALL_ATTACK_CLASSES = [
    JailbreakAttacks,
    SystemPromptLeakAttacks,
    PIILeakageAttacks,
    TrainingDataExtractionAttacks,
    AlignmentBypassAttacks,
]
