import os
import shutil
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


def parse_gradient(aop, num_atom):
    with open(aop, "r") as f:
        line = f.readline()
        while line:
            if line.startswith(" Dipole moment (field-independent basis, Debye):"):
                line = f.readline()  # skip blank line
                line = f.readline()  # dipole moment data
                arr = line.split()
                dipole = [arr[1], arr[3], arr[5]]
                dipole = [float(x) for x in dipole]

            if line.startswith(" Cartesian Force (Hartrees/Bohr):"):
                line = f.readline()  # skip blank line

                gradient = []

                for _ in range(num_atom):
                    line = f.readline()
                    arr = line.split()
                    gradient.append([float(x) for x in arr[1:]])

            if line.startswith(" Final Energy:"):
                energy = float(line.split()[-1])

            line = f.readline()

    return energy, gradient, dipole


def parse_hessian(aop, num_atom):
    pass


if __name__ == "__main__":
    # load Amesp template
    with open("template.aip", "r") as f:
        contents = [line.strip() for line in f.readlines()]

    # parse Gaussian cli args
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
        if line.startswith("! "):
            contents[idx] += " force"
        elif derivs == 2:
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

    if derivs == 1:
        # parse energy, gradient, and dipole
        energy, gradient, dipole = parse_gradient("mol.aop", atoms)

        with open(OutputFile, "w") as f:
            f.writelines(
                f"{energy:20.12E}{dipole[0]:20.12E}{dipole[1]:20.12E}{dipole[2]:20.12E}\n")

            gradient = np.array(gradient)
            np.savetxt(f, -1.0 * gradient, fmt="%20.12E", delimiter="")

    elif derivs == 2:
        # parse energy, gradient, and hessian
        pass

    print(">>> Done!")

    os.chdir(curr_dir)
