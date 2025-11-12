"""
FLOPs calculation and optimization - MVP Sovereign
Calculs de métriques de performance exactes pour la régression logistique
"""

import logging
from typing import Tuple
import numpy as np

logger = logging.getLogger(__name__)


def calculate_logistic_regression_flops(
    n_samples: int,
    n_features: int,
    n_iterations: int
) -> float:
    """
    Calcule les FLOPs exacts pour une régression logistique.

    Architecture:
    1. Forward pass: X @ w → (n_samples, n_features) @ (n_features, 1) = n_samples * n_features muls
    2. Sigmoid: exp + additions → ~4 * n_samples FLOPs
    3. Loss computation: log + additions → ~3 * n_samples FLOPs
    4. Gradient: X.T @ error → (n_features, n_samples) @ (n_samples, 1) = n_features * n_samples muls
    5. Weight update: w - lr * grad → n_features FLOPs

    Par itération:
    - Forward (matmul): n_samples * n_features
    - Sigmoid: 4 * n_samples
    - Loss: 3 * n_samples
    - Gradient (matmul): n_features * n_samples
    - Update: n_features

    Total par itération ≈ 2 * n_samples * n_features + 7 * n_samples + n_features

    Args:
        n_samples: Nombre d'échantillons d'entraînement
        n_features: Nombre de features
        n_iterations: Nombre d'itérations de gradient descent

    Returns:
        Nombre total de FLOPs
    """
    # FLOPs par itération
    forward_flops = n_samples * n_features  # X @ w
    sigmoid_flops = 4 * n_samples  # exp, div, additions
    loss_flops = 3 * n_samples  # log, sum
    gradient_flops = n_features * n_samples  # X.T @ error
    update_flops = n_features  # w = w - lr * grad

    flops_per_iteration = (
        forward_flops +
        sigmoid_flops +
        loss_flops +
        gradient_flops +
        update_flops
    )

    total_flops = flops_per_iteration * n_iterations

    logger.debug(
        f"FLOPs calculation: {n_samples}×{n_features} over {n_iterations} iters "
        f"= {total_flops:,.0f} FLOPs"
    )

    return total_flops


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Fonction sigmoid stable numériquement"""
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))


def simple_logistic_regression(
    n_samples: int,
    n_features: int,
    n_iterations: int,
    seed: int = 42
) -> Tuple[float, float]:
    """
    Implémente une régression logistique simple offline avec comptage exact de FLOPs.

    Cette implémentation est volontairement simple et auditable:
    - Pas de frameworks ML lourds (TensorFlow, PyTorch)
    - Gradient descent vanilla
    - FLOPs calculés exactement
    - Seed fixe pour reproductibilité

    Args:
        n_samples: Nombre d'échantillons
        n_features: Nombre de features
        n_iterations: Nombre d'itérations
        seed: Seed aléatoire pour reproductibilité

    Returns:
        Tuple (accuracy_delta_percent, total_flops)
        - accuracy_delta_percent: Amélioration en % (ex: 15.2%)
        - total_flops: Nombre exact de FLOPs utilisés
    """
    logger.info(f"🧮 Régression logistique: {n_samples} samples, {n_features} features, {n_iterations} iters")

    # Seed fixe pour reproductibilité
    np.random.seed(seed)

    # Génération des données synthétiques
    # X: features aléatoires
    X = np.random.randn(n_samples, n_features)

    # y: labels binaires avec une structure (pour avoir de l'amélioration)
    # On crée un vrai signal: y dépend de certaines features
    true_weights = np.random.randn(n_features) * 0.5
    y_prob = sigmoid(X @ true_weights)
    y = (y_prob > 0.5).astype(float)

    # Initialisation des poids (petites valeurs aléatoires)
    w = np.random.randn(n_features) * 0.01

    # Accuracy initiale (baseline)
    y_pred_init = (sigmoid(X @ w) > 0.5).astype(float)
    accuracy_init = np.mean(y_pred_init == y)

    # Entraînement avec gradient descent
    learning_rate = 0.01

    for iteration in range(n_iterations):
        # Forward pass
        z = X @ w  # (n_samples,)
        y_pred_prob = sigmoid(z)

        # Gradient
        error = y_pred_prob - y  # (n_samples,)
        gradient = (X.T @ error) / n_samples  # (n_features,)

        # Update
        w = w - learning_rate * gradient

    # Accuracy finale
    y_pred_final = (sigmoid(X @ w) > 0.5).astype(float)
    accuracy_final = np.mean(y_pred_final == y)

    # Calcul de l'amélioration en %
    accuracy_delta = (accuracy_final - accuracy_init) * 100.0

    # Calcul des FLOPs exacts
    total_flops = calculate_logistic_regression_flops(n_samples, n_features, n_iterations)

    logger.info(
        f"✅ Régression terminée: accuracy {accuracy_init:.2%} → {accuracy_final:.2%} "
        f"(Δ={accuracy_delta:.2f}%), FLOPs={total_flops:,.0f}"
    )

    return accuracy_delta, total_flops


def estimate_cost(flops: float, mode: str = "offline") -> dict:
    """
    Estime le coût d'une opération en fonction des FLOPs.

    Args:
        flops: Nombre de FLOPs
        mode: Mode de fonctionnement

    Returns:
        Dictionnaire avec estimations de coût
    """
    cost_per_gflop = 0.0 if mode == "offline" else 0.001  # $0.001 par GFLOPs en mode LLM

    gflops = flops / 1e9
    estimated_cost = gflops * cost_per_gflop

    return {
        "flops": flops,
        "gflops": gflops,
        "estimated_cost_usd": estimated_cost,
        "mode": mode,
    }
