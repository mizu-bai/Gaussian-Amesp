#!/bin/bash

# energy

echo "[INFO] Test energy parser..."
cd 0-energy

echo "[INFO] Running g16..."
g16 < H2O-g16.gjf | tee H2O-g16.out

echo "[INFO] Running g16-amesp..."
g16 < H2O-g16-amesp.gjf | tee H2O-g16-amesp.out

echo "[INFO] Energy parser tests done!"
cd ..

# force

echo "[INFO] Test force parser..."
cd 1-force

echo "[INFO] Running g16..."
g16 < H2O-force-g16.gjf | tee H2O-force-g16.out

echo "[INFO] Running g16-amesp..."
g16 < H2O-force-g16-amesp.gjf | tee H2O-force-g16-amesp.out

echo "[INFO] Force parser tests done!"
cd ..

# hessian
echo "[INFO] Test hessian parser..."
cd 2-hessian

echo "[INFO] Running g16..."
g16 < H2O-hessian-g16.gjf | tee H2O-hessian-g16.out

echo "[INFO] Running g16-amesp..."
g16 < H2O-hessian-g16-amesp.gjf | tee H2O-hessian-g16-amesp.out

echo "[INFO] Hessian parser tests done!"
cd ..
