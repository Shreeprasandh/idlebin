"""
IdleBin Physics Engine
Kinematics, Mechanical Advantage, and Compaction Mechanics
Authored for IdleBin Municipal Innovation Suite
"""

import numpy as np


class PhysicsEngine:
    """
    Models the mechanical advantage, downward compaction force,
    pressure distribution, and PET plastic deformation dynamics of IdleBin.
    """

    PET_YIELD_FORCE_NEWTONS = 220.0  # Force required to initiate buckling in standard 1L empty PET bottle
    PET_PERMANENT_DEFORM_FORCE = 450.0  # Force required for permanent plastic crease yielding

    @staticmethod
    def calculate_kinematics(foot_weight_kg: float, pedal_length_cm: float, pivot_offset_cm: float, platen_diameter_cm: float):
        """
        Calculates:
        - Mechanical Advantage (MA)
        - Compaction Force (Newtons)
        - Platen Contact Area (cm^2)
        - Compaction Pressure (N/cm^2 and kPa)
        - Effective compaction ratio
        """
        if pivot_offset_cm <= 0:
            pivot_offset_cm = 1.0

        # Mechanical Advantage of class-2 / class-1 lever linkage
        ma = pedal_length_cm / pivot_offset_cm
        
        # Gravitational acceleration
        g = 9.80665
        
        # User downward force
        input_force_n = foot_weight_kg * g
        
        # Theoretical compaction force delivered to plunger plate
        compaction_force_n = input_force_n * ma
        
        # Platen surface area (A = pi * r^2)
        radius_cm = platen_diameter_cm / 2.0
        area_cm2 = np.pi * (radius_cm ** 2)
        
        # Compaction pressure
        pressure_n_per_cm2 = compaction_force_n / area_cm2 if area_cm2 > 0 else 0
        pressure_kpa = pressure_n_per_cm2 * 10.0  # 1 N/cm^2 = 10 kPa
        
        # Estimated Compaction Ratio (empirical curve: 1x uncompacted to ~4.5x fully deformed)
        if compaction_force_n < PhysicsEngine.PET_YIELD_FORCE_NEWTONS:
            compaction_ratio = 1.0 + (compaction_force_n / PhysicsEngine.PET_YIELD_FORCE_NEWTONS) * 0.8
            status = "Elastic Compression (Temporary, high bounce-back risk)"
            rebound_pct = 65.0
        elif compaction_force_n < PhysicsEngine.PET_PERMANENT_DEFORM_FORCE:
            compaction_ratio = 1.8 + ((compaction_force_n - PhysicsEngine.PET_YIELD_FORCE_NEWTONS) / 
                                      (PhysicsEngine.PET_PERMANENT_DEFORM_FORCE - PhysicsEngine.PET_YIELD_FORCE_NEWTONS)) * 1.5
            status = "Partial Plastic Deformation (Moderate bounce-back)"
            rebound_pct = 32.0
        else:
            compaction_ratio = 3.3 + min(1.2, ((compaction_force_n - PhysicsEngine.PET_PERMANENT_DEFORM_FORCE) / 500.0) * 1.0)
            status = "Permanent Plastic Creasing (Optimal ~4x Compaction, <15% Rebound)"
            rebound_pct = 12.0
            
        return {
            "mechanical_advantage": round(ma, 2),
            "input_force_n": round(input_force_n, 1),
            "compaction_force_n": round(compaction_force_n, 1),
            "platen_area_cm2": round(area_cm2, 1),
            "pressure_n_per_cm2": round(pressure_n_per_cm2, 2),
            "pressure_kpa": round(pressure_kpa, 1),
            "compaction_ratio": round(compaction_ratio, 2),
            "rebound_pct": round(rebound_pct, 1),
            "deformation_status": status,
            "exceeds_yield": compaction_force_n >= PhysicsEngine.PET_YIELD_FORCE_NEWTONS,
            "exceeds_permanent": compaction_force_n >= PhysicsEngine.PET_PERMANENT_DEFORM_FORCE,
        }

    @staticmethod
    def generate_force_weight_curve(pedal_length_cm: float = 38.0, pivot_offset_cm: float = 28.0):
        """Generates force curve across weight ranges from 30kg to 90kg."""
        weights = np.linspace(30, 95, 25)
        forces = []
        ma = pedal_length_cm / pivot_offset_cm
        for w in weights:
            forces.append(w * 9.80665 * ma)
        return weights, np.array(forces)
