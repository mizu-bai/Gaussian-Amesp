import os
import sys

import numpy as np

# constants
ANG2BOHR = 1.8897259886

ELEMENTS = [
    "Bq",
    "H ",                                                                                                                                                                                     "He",
    "Li", "Be",                                                                                                                                                 "B ", "C ", "N ", "O ", "F ", "Ne",
    "Na", "Mg",                                                                                                                                                 "Al", "Si", "P ", "S ", "Cl", "Ar",
    "K ", "Ca", "Sc", "Ti", "V ", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",                                                                                     "Ga", "Ge", "As", "Se", "Br", "Kr",
    "Rb", "Sr", "Y ", "Zr", "Nb", "Mo", "Te", "Ru", "Rh", "Pd", "Ag", "Cd",                                                                                     "In", "Sn", "Sb", "Te", "I ", "Xe",
    "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W ", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn",
    "Fr", "Ra", "Ac", "Th", "Pa", "U ", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
]


def _parse_energy(contents):
    energy = 0.0

    for line in contents:
        if line.startswith(" Final Energy"):
            energy = float(line.split()[-1])
            break

    return energy


def _parse_force(contents, num_atoms):
    force = np.zeros((num_atoms, 3))

    for (idx, line) in enumerate(contents):
        if line.startswith(" Cartesian Force"):
            _idx = idx + 1
            _force = []
            for j in range(1, num_atoms + 1):
                arr = contents[_idx + j].split()
                _force.append([float(x) for x in arr[1:]])

            force = np.array(_force)
            break

    return force


def _parse_hessian(contents, num_atoms):
    hessian = np.array([])
    num_rows = int(3 * num_atoms)
    num_items = int(num_rows * (num_rows + 1) / 2)
    mat = np.zeros((num_rows, num_rows))

    for (idx, line) in enumerate(contents):
        if line.startswith(" Cartesian Hessian"):
            _idx = idx + 2

            # check first col_line
            col_line = contents[_idx]
            col_arr = col_line.split()
            col_arr = [int(x) for x in col_arr]
            part_idx = 0

            while col_arr[-1] <= num_rows:
                for j in range(1, num_rows + 1 - part_idx * 5):
                    line = contents[_idx + j]
                    # arr = line.split()
                    # arr = [float(x) for x in arr[1:]]
                    arr = line.split()
                    row_idx = int(arr[0])
                    row_val = [float(x) for x in arr[1:]]
                    for (val_idx, val) in enumerate(row_val):
                        mat[row_idx - 1, col_arr[val_idx] - 1] = val

                if col_arr[-1] == num_rows:
                    break

                _idx += (num_rows + 1 - part_idx * 5)
                col_line = contents[_idx]
                col_arr = col_line.split()
                col_arr = [int(x) for x in col_arr]
                part_idx += 1

            _hessian = []

            for r in range(num_rows):
                for c in range(r + 1):
                    _hessian.append(mat[r, c])

            assert len(_hessian) == num_items

            hessian = np.array(_hessian)
            break

    return hessian


def parse_output(contents, num_atoms, derivs):
    res = {}

    # parse energy
    res["energy"] = _parse_energy(contents)

    # parse dipole
    res["dipole"] = _parse_dipole(contents)

    if derivs == 1 or derivs == 2:
        # parse gradient
        res["force"] = _parse_force(contents, num_atoms)

    if derivs == 2:
        # parse hessian
        res["hessian"] = _parse_hessian(contents, num_atoms)

    return res


def _parse_dipole(contents):
    dipole = np.zeros((3,))

    for (idx, line) in enumerate(contents):
        if line.startswith(" Dipole moment"):
            arr = contents[idx + 2].split()
            _dipole = [arr[1], arr[3], arr[5]]
            dipole = np.array([float(x) for x in _dipole])
            break

    return dipole


if __name__ == "__main__":
    # load Amesp template
    with open("template.aip", "r") as f:
        contents = [line.strip() for line in f.readlines()]

    # parse Gaussian args
    (layer, InputFile, OutputFile, MsgFile, FChkFile, MatElFile) = sys.argv[1:]

    with open(InputFile, "r") as f:
        (atoms, derivs, charge, spin) = [int(x) for x in f.readline().split()]

        contents.append(f">xyz {charge} {spin}")

        for i in range(atoms):
            arr = f.readline().split()
            tmp = [ELEMENTS[int(arr[0])]]
            tmp += [f"{(float(x) / ANG2BOHR):13.8f}" for x in arr[1:4]]
            contents.append("    ".join(tmp))

        contents.append("end")

    for (idx, line) in enumerate(contents):
        if not line.startswith("! "):
            continue

        if derivs == 1 or derivs == 2:
            contents[idx] += " force"

        if derivs == 2:
            contents[idx] += " freq"

    aip = "\n".join(contents)

    curr_dir = os.getcwd()
    curr_dir = os.path.abspath(curr_dir)

    if not os.path.exists("tmp"):
        os.mkdir("tmp")

    os.chdir("tmp")

    with open("mol.aip", "w") as f:
        f.write(aip)

    print(">>> Running Amesp...")

    os.system("amesp mol.aip")

    print(">>> Parsing Amesp output...")

    with open("mol.aop", "r") as f:
        contents = f.readlines()
        res = parse_output(contents, atoms, derivs)

    # write to Output
    contents = []

    # energy, dipole
    line = f"{res['energy']:20.12E}{res['dipole'][0]:20.12E}{res['dipole'][1]:20.12E}{res['dipole'][2]:20.12E}"
    contents.append(line)

    # force
    if derivs == 1 or derivs == 2:
        for force_on_atom in res["force"]:
            line = "".join([f"{(-1.0 * f):20.12E}" for f in force_on_atom])
            contents.append(line)

    # hessian
    if derivs == 2:
        empty_line = f"{0:20.12E}" * 3

        # polarizability
        for _ in range(2):
            contents.append(empty_line)

        # dipole derivatives
        for _ in range(3 * atoms):
            contents.append(empty_line)

        # hessian
        for component in res["hessian"].reshape((-1, 3)):
            line = "".join([f"{c:20.12E}" for c in component])
            contents.append(line)

    contents = "\n".join(contents)

    with open(OutputFile, "w") as f:
        f.write(contents)

    print(">>> 大师大法好！")

    os.chdir(curr_dir)
