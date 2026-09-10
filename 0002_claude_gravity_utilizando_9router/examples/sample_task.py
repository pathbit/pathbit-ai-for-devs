"""Módulo de exemplo para testes do Claude Code com ClaudeGravity."""

import time


def calculate_fibonacci(n: int) -> int:
    """Calcula o enésimo número de Fibonacci de forma recursiva simples."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


def main():
    start = time.time()
    result = calculate_fibonacci(10)
    elapsed = time.time() - start
    print(f"Fibonacci(10) = {result} (tempo: {elapsed:.6f}s)")


if __name__ == "__main__":
    main()
