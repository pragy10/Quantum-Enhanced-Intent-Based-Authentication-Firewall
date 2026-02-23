# File: backend/firewall/quantum_engine.py

import pennylane as qml
from pennylane import numpy as np
import hashlib
import time
from backend.utils.logger import logger

# Two-qubit device: wire 0 → Server, wire 1 → Client
dev = qml.device("default.qubit", wires=2)

def generate_challenge():
    """Generates a time-based cryptographic nonce."""
    nonce = str(time.time()).encode()
    return hashlib.sha256(nonce).hexdigest()

@qml.qnode(dev, shots=1024)
def quantum_authentication_circuit(phase_angle, tamper=False):
    # Bell pair preparation
    qml.Hadamard(0)
    qml.CNOT([0, 1])

    # Tampering / MITM simulation
    if tamper:
        qml.RX(np.pi / 4, wires=1)

    # Client encodes challenge
    qml.RZ(phase_angle, wires=1)

    # Correlation measurement
    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

class QuantumEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold
        
    def get_challenge(self):
        return generate_challenge()
        
    def authenticate_client(self, challenge_str, tamper=False):
        """
        Runs the quantum circuit and checks correlation fidelity.
        Returns (is_valid, fidelity_score)
        """
        # Calculate phase angle
        phase = int(challenge_str[:8], 16) % 360
        phase_rad = np.deg2rad(phase)

        # Execute circuit
        correlation = quantum_authentication_circuit(phase_rad, tamper)
        fidelity = abs(correlation)
        
        logger.info(f"Quantum ZZ Correlation: {correlation:.3f}, Fidelity: {fidelity:.3f}")

        if fidelity >= self.threshold:
            return True, float(fidelity)
        else:
            return False, float(fidelity)

quantum_engine = QuantumEngine()