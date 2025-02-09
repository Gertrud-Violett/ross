import os
from pathlib import Path
from tempfile import tempdir

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_almost_equal

import ross as rs
from ross.defects.misalignment import MisalignmentFlex
from ross.units import Q_

steel2 = rs.Material(name="Steel", rho=7850, E=2.17e11, G_s=81.2e9)

#  Rotor with 6 DoFs, with internal damping, with 10 shaft elements, 2 disks and 2 bearings.
i_d = 0
o_d = 0.019
n = 33

# fmt: off
L = np.array(
        [0  ,  25,  64, 104, 124, 143, 175, 207, 239, 271,
        303, 335, 345, 355, 380, 408, 436, 466, 496, 526,
        556, 586, 614, 647, 657, 667, 702, 737, 772, 807,
        842, 862, 881, 914]
        )/ 1000
# fmt: on

L = [L[i] - L[i - 1] for i in range(1, len(L))]

shaft_elem = [
    rs.ShaftElement6DoF(
        material=steel2,
        L=l,
        idl=i_d,
        odl=o_d,
        idr=i_d,
        odr=o_d,
        alpha=8.0501,
        beta=1.0e-5,
        rotary_inertia=True,
        shear_effects=True,
    )
    for l in L
]

Id = 0.003844540885417
Ip = 0.007513248437500

disk0 = rs.DiskElement6DoF(n=12, m=2.6375, Id=Id, Ip=Ip)
disk1 = rs.DiskElement6DoF(n=24, m=2.6375, Id=Id, Ip=Ip)

kxx1 = 4.40e5
kyy1 = 4.6114e5
kzz = 0
cxx1 = 27.4
cyy1 = 2.505
czz = 0
kxx2 = 9.50e5
kyy2 = 1.09e8
cxx2 = 50.4
cyy2 = 100.4553

bearing0 = rs.BearingElement6DoF(
    n=4, kxx=kxx1, kyy=kyy1, cxx=cxx1, cyy=cyy1, kzz=kzz, czz=czz
)
bearing1 = rs.BearingElement6DoF(
    n=31, kxx=kxx2, kyy=kyy2, cxx=cxx2, cyy=cyy2, kzz=kzz, czz=czz
)

rotor = rs.Rotor(shaft_elem, [disk0, disk1], [bearing0, bearing1])


@pytest.fixture
def mis_comb():

    unbalance_magnitudet = np.array([5e-4, 0])
    unbalance_phaset = np.array([-np.pi / 2, 0])

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),
        ks=38 * 10 ** (3),
        eCOUPx=2 * 10 ** (-4),
        eCOUPy=2 * 10 ** (-4),
        misalignment_angle=5 * np.pi / 180,
        TD=0,
        TL=0,
        n1=0,
        speed=125.66370614359172,
        unbalance_magnitude=unbalance_magnitudet,
        unbalance_phase=unbalance_phaset,
        mis_type="combined",
        print_progress=False,
    )

    return misalignment


@pytest.fixture
def mis_comb_units():

    unbalance_magnitudet = Q_(np.array([0.043398083107259365, 0]), "lb*in")
    unbalance_phaset = Q_(np.array([-90.0, 0.0]), "degrees")

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),
        ks=38 * 10 ** (3),
        eCOUPx=2 * 10 ** (-4),
        eCOUPy=2 * 10 ** (-4),
        misalignment_angle=5 * np.pi / 180,
        TD=0,
        TL=0,
        n1=0,
        speed=Q_(1200, "RPM"),
        unbalance_magnitude=unbalance_magnitudet,
        unbalance_phase=unbalance_phaset,
        mis_type="combined",
        print_progress=False,
    )

    return misalignment


def test_mis_comb_parameters(mis_comb):
    assert mis_comb.dt == 0.1
    assert mis_comb.tI == 0
    assert mis_comb.tF == 5
    assert mis_comb.kd == 40 * 10 ** (3)
    assert mis_comb.ks == 38 * 10 ** (3)
    assert mis_comb.eCOUPx == 2 * 10 ** (-4)
    assert mis_comb.eCOUPy == 2 * 10 ** (-4)
    assert mis_comb.misalignment_angle == 5 * np.pi / 180
    assert mis_comb.TD == 0
    assert mis_comb.TL == 0
    assert mis_comb.n1 == 0
    assert mis_comb.speed == 125.66370614359172


def test_mis_comb_parameters_units(mis_comb_units):
    assert mis_comb_units.dt == 0.1
    assert mis_comb_units.tI == 0
    assert mis_comb_units.tF == 5
    assert mis_comb_units.kd == 40 * 10 ** (3)
    assert mis_comb_units.ks == 38 * 10 ** (3)
    assert mis_comb_units.eCOUPx == 2 * 10 ** (-4)
    assert mis_comb_units.eCOUPy == 2 * 10 ** (-4)
    assert mis_comb_units.misalignment_angle == 5 * np.pi / 180
    assert mis_comb_units.TD == 0
    assert mis_comb_units.TL == 0
    assert mis_comb_units.n1 == 0
    assert mis_comb_units.speed == 125.66370614359172


def test_mis_comb_forces(mis_comb):
    assert mis_comb.forces[mis_comb.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,
    ]
    )
        # fmt: on
    )

    assert mis_comb.forces[mis_comb.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,
    ]
    )
        # fmt: on
    )

    assert mis_comb.forces[mis_comb.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,
    ]
    )
        # fmt: on
    )

    assert mis_comb.forces[mis_comb.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,
    ]
    )
        # fmt: on
    )


def test_mis_comb_forces_units(mis_comb_units):
    assert mis_comb_units.forces[mis_comb_units.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,
    ]
    )
        # fmt: on
    )

    assert mis_comb_units.forces[mis_comb_units.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,
    ]
    )
        # fmt: on
    )

    assert mis_comb_units.forces[mis_comb_units.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,
    ]
    )
        # fmt: on
    )

    assert mis_comb_units.forces[mis_comb_units.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,
    ]
    )
        # fmt: on
    )


@pytest.fixture
def mis_parallel():

    unbalance_magnitudet = np.array([5e-4, 0])
    unbalance_phaset = np.array([-np.pi / 2, 0])

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),
        ks=38 * 10 ** (3),
        eCOUPx=2 * 10 ** (-4),
        eCOUPy=2 * 10 ** (-4),
        misalignment_angle=5 * np.pi / 180,
        TD=0,
        TL=0,
        n1=0,
        speed=125.66370614359172,
        unbalance_magnitude=unbalance_magnitudet,
        unbalance_phase=unbalance_phaset,
        mis_type="parallel",
        print_progress=False,
    )

    return misalignment


@pytest.fixture
def mis_parallel_units():

    unbalance_magnitudet = Q_(np.array([0.043398083107259365, 0]), "lb*in")
    unbalance_phaset = Q_(np.array([-90.0, 0.0]), "degrees")

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),
        ks=38 * 10 ** (3),
        eCOUPx=2 * 10 ** (-4),
        eCOUPy=2 * 10 ** (-4),
        misalignment_angle=5 * np.pi / 180,
        TD=0,
        TL=0,
        n1=0,
        speed=Q_(1200, "RPM"),
        unbalance_magnitude=unbalance_magnitudet,
        unbalance_phase=unbalance_phaset,
        mis_type="parallel",
        print_progress=False,
    )

    return misalignment


def test_mis_parallel_parameters(mis_parallel):
    assert mis_parallel.dt == 0.1
    assert mis_parallel.tI == 0
    assert mis_parallel.tF == 5
    assert mis_parallel.kd == 40 * 10 ** (3)
    assert mis_parallel.ks == 38 * 10 ** (3)
    assert mis_parallel.eCOUPx == 2 * 10 ** (-4)
    assert mis_parallel.eCOUPy == 2 * 10 ** (-4)
    assert mis_parallel.misalignment_angle == 5 * np.pi / 180
    assert mis_parallel.TD == 0
    assert mis_parallel.TL == 0
    assert mis_parallel.n1 == 0
    assert mis_parallel.speed == 125.66370614359172


def test_mis_parallel_parameters_units(mis_parallel_units):
    assert mis_parallel_units.dt == 0.1
    assert mis_parallel_units.tI == 0
    assert mis_parallel_units.tF == 5
    assert mis_parallel_units.kd == 40 * 10 ** (3)
    assert mis_parallel_units.ks == 38 * 10 ** (3)
    assert mis_parallel_units.eCOUPx == 2 * 10 ** (-4)
    assert mis_parallel_units.eCOUPy == 2 * 10 ** (-4)
    assert mis_parallel_units.misalignment_angle == 5 * np.pi / 180
    assert mis_parallel_units.TD == 0
    assert mis_parallel_units.TL == 0
    assert mis_parallel_units.n1 == 0
    assert mis_parallel_units.speed == 125.66370614359172


def test_mis_parallel_forces(mis_parallel):
    assert mis_parallel.forces[mis_parallel.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529
    ]
    )
        # fmt: on
    )

    assert mis_parallel.forces[mis_parallel.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174
    ]
    )
        # fmt: on
    )

    assert mis_parallel.forces[mis_parallel.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529
    ]
    )
        # fmt: on
    )

    assert mis_parallel.forces[mis_parallel.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174
    ]
    )
        # fmt: on
    )


def test_mis_parallel_forces_units(mis_parallel_units):
    assert mis_parallel_units.forces[mis_parallel_units.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529
    ]
    )
        # fmt: on
    )

    assert mis_parallel_units.forces[mis_parallel_units.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174
    ]
    )
        # fmt: on
    )

    assert mis_parallel_units.forces[mis_parallel_units.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529
    ]
    )
        # fmt: on
    )

    assert mis_parallel_units.forces[mis_parallel_units.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174
    ]
    )
        # fmt: on
    )


@pytest.fixture
def mis_angular():

    unbalance_magnitudet = np.array([5e-4, 0])
    unbalance_phaset = np.array([-np.pi / 2, 0])

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),
        ks=38 * 10 ** (3),
        eCOUPx=2 * 10 ** (-4),
        eCOUPy=2 * 10 ** (-4),
        misalignment_angle=5 * np.pi / 180,
        TD=0,
        TL=0,
        n1=0,
        speed=125.66370614359172,
        unbalance_magnitude=unbalance_magnitudet,
        unbalance_phase=unbalance_phaset,
        mis_type="angular",
        print_progress=False,
    )

    return misalignment


@pytest.fixture
def mis_angular_units():

    unbalance_magnitudet = Q_(np.array([0.043398083107259365, 0]), "lb*in")
    unbalance_phaset = Q_(np.array([-90.0, 0.0]), "degrees")

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),
        ks=38 * 10 ** (3),
        eCOUPx=2 * 10 ** (-4),
        eCOUPy=2 * 10 ** (-4),
        misalignment_angle=5 * np.pi / 180,
        TD=0,
        TL=0,
        n1=0,
        speed=Q_(1200, "RPM"),
        unbalance_magnitude=unbalance_magnitudet,
        unbalance_phase=unbalance_phaset,
        mis_type="angular",
        print_progress=False,
    )

    return misalignment


def test_mis_angular_parameters(mis_angular):
    assert mis_angular.dt == 0.1
    assert mis_angular.tI == 0
    assert mis_angular.tF == 5
    assert mis_angular.kd == 40 * 10 ** (3)
    assert mis_angular.ks == 38 * 10 ** (3)
    assert mis_angular.eCOUPx == 2 * 10 ** (-4)
    assert mis_angular.eCOUPy == 2 * 10 ** (-4)
    assert mis_angular.misalignment_angle == 5 * np.pi / 180
    assert mis_angular.TD == 0
    assert mis_angular.TL == 0
    assert mis_angular.n1 == 0
    assert mis_angular.speed == 125.66370614359172


def test_mis_angular_parameters_units(mis_angular_units):
    assert mis_angular_units.dt == 0.1
    assert mis_angular_units.tI == 0
    assert mis_angular_units.tF == 5
    assert mis_angular_units.kd == 40 * 10 ** (3)
    assert mis_angular_units.ks == 38 * 10 ** (3)
    assert mis_angular_units.eCOUPx == 2 * 10 ** (-4)
    assert mis_angular_units.eCOUPy == 2 * 10 ** (-4)
    assert mis_angular_units.misalignment_angle == 5 * np.pi / 180
    assert mis_angular_units.TD == 0
    assert mis_angular_units.TL == 0
    assert mis_angular_units.n1 == 0
    assert mis_angular_units.speed == 125.66370614359172


def test_mis_angular_forces(mis_angular):
    assert mis_angular.forces[mis_angular.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782
    ]
    )
        # fmt: on
    )

    assert mis_angular.forces[mis_angular.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-2.66453526e-15,  1.66147096e-11,  3.32343042e-11,  4.98774355e-11,
    6.64779343e-11,  8.30784330e-11,  9.97633087e-11,  1.16381571e-10,
    1.32931444e-10,  1.49549262e-10,  1.66149317e-10,  1.82851956e-10,
    1.99536387e-10,  2.16086704e-10,  2.32772024e-10,  2.49321896e-10,
    2.65872213e-10,  2.82556645e-10,  2.99107850e-10,  3.15792725e-10,
    3.32375905e-10,  3.48960416e-10,  3.65779851e-10,  3.82330612e-10,
    3.99150490e-10,  4.15429913e-10,  4.32250680e-10,  4.48800552e-10,
    4.65620431e-10,  4.82170748e-10,  4.98721064e-10,  5.15271381e-10,
    5.31820366e-10,  5.48641577e-10,  5.65191449e-10,  5.81740878e-10,
    5.98291194e-10,  6.15111961e-10,  6.31661390e-10,  6.48481713e-10,
    6.64762023e-10,  6.81716905e-10,  6.97726765e-10,  7.14276194e-10,
    7.31366523e-10,  7.47917284e-10,  7.64467156e-10,  7.81017029e-10,
    7.98106914e-10,  8.14657675e-10,  8.30667091e-10
    ]
    )
        # fmt: on
    )

    assert mis_angular.forces[mis_angular.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782
    ]
    )
        # fmt: on
    )

    assert mis_angular.forces[mis_angular.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [ 2.66453526e-15, -1.66147096e-11, -3.32343042e-11, -4.98774355e-11,
    -6.64779343e-11, -8.30784330e-11, -9.97633087e-11, -1.16381571e-10,
    -1.32931444e-10, -1.49549262e-10, -1.66149317e-10, -1.82851956e-10,
    -1.99536387e-10, -2.16086704e-10, -2.32772024e-10, -2.49321896e-10,
    -2.65872213e-10, -2.82556645e-10, -2.99107850e-10, -3.15792725e-10,
    -3.32375905e-10, -3.48960416e-10, -3.65779851e-10, -3.82330612e-10,
    -3.99150490e-10, -4.15429913e-10, -4.32250680e-10, -4.48800552e-10,
    -4.65620431e-10, -4.82170748e-10, -4.98721064e-10, -5.15271381e-10,
    -5.31820366e-10, -5.48641577e-10, -5.65191449e-10, -5.81740878e-10,
    -5.98291194e-10, -6.15111961e-10, -6.31661390e-10, -6.48481713e-10,
    -6.64762023e-10, -6.81716905e-10, -6.97726765e-10, -7.14276194e-10,
    -7.31366523e-10, -7.47917284e-10, -7.64467156e-10, -7.81017029e-10,
    -7.98106914e-10, -8.14657675e-10, -8.30667091e-10
    ]
    )
        # fmt: on
    )


def test_mis_angular_forces_units(mis_angular_units):
    assert mis_angular_units.forces[mis_angular_units.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782
    ]
    )
        # fmt: on
    )

    assert mis_angular_units.forces[mis_angular_units.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-2.66453526e-15,  1.66147096e-11,  3.32343042e-11,  4.98774355e-11,
    6.64779343e-11,  8.30784330e-11,  9.97633087e-11,  1.16381571e-10,
    1.32931444e-10,  1.49549262e-10,  1.66149317e-10,  1.82851956e-10,
    1.99536387e-10,  2.16086704e-10,  2.32772024e-10,  2.49321896e-10,
    2.65872213e-10,  2.82556645e-10,  2.99107850e-10,  3.15792725e-10,
    3.32375905e-10,  3.48960416e-10,  3.65779851e-10,  3.82330612e-10,
    3.99150490e-10,  4.15429913e-10,  4.32250680e-10,  4.48800552e-10,
    4.65620431e-10,  4.82170748e-10,  4.98721064e-10,  5.15271381e-10,
    5.31820366e-10,  5.48641577e-10,  5.65191449e-10,  5.81740878e-10,
    5.98291194e-10,  6.15111961e-10,  6.31661390e-10,  6.48481713e-10,
    6.64762023e-10,  6.81716905e-10,  6.97726765e-10,  7.14276194e-10,
    7.31366523e-10,  7.47917284e-10,  7.64467156e-10,  7.81017029e-10,
    7.98106914e-10,  8.14657675e-10,  8.30667091e-10
    ]
    )
        # fmt: on
    )

    assert mis_angular_units.forces[mis_angular_units.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782
    ]
    )
        # fmt: on
    )

    assert mis_angular_units.forces[mis_angular_units.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [ 2.66453526e-15, -1.66147096e-11, -3.32343042e-11, -4.98774355e-11,
    -6.64779343e-11, -8.30784330e-11, -9.97633087e-11, -1.16381571e-10,
    -1.32931444e-10, -1.49549262e-10, -1.66149317e-10, -1.82851956e-10,
    -1.99536387e-10, -2.16086704e-10, -2.32772024e-10, -2.49321896e-10,
    -2.65872213e-10, -2.82556645e-10, -2.99107850e-10, -3.15792725e-10,
    -3.32375905e-10, -3.48960416e-10, -3.65779851e-10, -3.82330612e-10,
    -3.99150490e-10, -4.15429913e-10, -4.32250680e-10, -4.48800552e-10,
    -4.65620431e-10, -4.82170748e-10, -4.98721064e-10, -5.15271381e-10,
    -5.31820366e-10, -5.48641577e-10, -5.65191449e-10, -5.81740878e-10,
    -5.98291194e-10, -6.15111961e-10, -6.31661390e-10, -6.48481713e-10,
    -6.64762023e-10, -6.81716905e-10, -6.97726765e-10, -7.14276194e-10,
    -7.31366523e-10, -7.47917284e-10, -7.64467156e-10, -7.81017029e-10,
    -7.98106914e-10, -8.14657675e-10, -8.30667091e-10
    ]
    )
        # fmt: on
    )


@pytest.fixture
def mis_rigid():

    unbalance_magnitudet = np.array([5e-4, 0])
    unbalance_phaset = np.array([-np.pi / 2, 0])

    misalignment = rotor.run_misalignment(
        coupling="rigid",
        dt=0.0001,
        tI=0,
        tF=0.005,
        eCOUP=2e-4,
        TD=0,
        TL=0,
        n1=0,
        speed=125.66370614359172,
        unbalance_magnitude=unbalance_magnitudet,
        unbalance_phase=unbalance_phaset,
        print_progress=False,
    )

    return misalignment


@pytest.fixture
def mis_rigid_units():

    unbalance_magnitudet = Q_(np.array([0.043398083107259365, 0]), "lb*in")
    unbalance_phaset = Q_(np.array([-90.0, 0.0]), "degrees")

    misalignment = rotor.run_misalignment(
        coupling="rigid",
        dt=0.0001,
        tI=0,
        tF=0.005,
        eCOUP=2e-4,
        TD=0,
        TL=0,
        n1=0,
        speed=Q_(1200, "RPM"),
        unbalance_magnitude=unbalance_magnitudet,
        unbalance_phase=unbalance_phaset,
        print_progress=False,
    )

    return misalignment


def test_mis_rigid_parameters(mis_rigid):
    assert mis_rigid.dt == 0.0001
    assert mis_rigid.tI == 0
    assert mis_rigid.tF == 0.005
    assert mis_rigid.eCOUP == 2e-4
    assert mis_rigid.TD == 0
    assert mis_rigid.TL == 0
    assert mis_rigid.n1 == 0
    assert mis_rigid.speed == 125.66370614359172


def test_mis_rigid_parameters_units(mis_rigid_units):
    assert mis_rigid_units.dt == 0.0001
    assert mis_rigid_units.tI == 0
    assert mis_rigid_units.tF == 0.005
    assert mis_rigid_units.eCOUP == 2e-4
    assert mis_rigid_units.TD == 0
    assert mis_rigid_units.TL == 0
    assert mis_rigid_units.n1 == 0
    assert mis_rigid_units.speed == 125.66370614359172


def test_mis_rigid_forces(mis_rigid):
    assert mis_rigid.forces[mis_rigid.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [0.00000000e+00, 4.36964689e+00, 1.74771689e+01, 3.93186457e+01,
       6.98878473e+01, 1.09176370e+02, 1.57173806e+02, 2.13867938e+02,
       2.79244943e+02, 3.53289607e+02, 4.35985520e+02, 5.27315254e+02,
       6.27260511e+02, 7.35802235e+02, 8.52920676e+02, 9.78595415e+02,
       1.11280534e+03, 1.25552860e+03, 1.40674247e+03, 1.56642326e+03,
       1.73454619e+03, 1.91108521e+03, 2.09601285e+03, 2.28930016e+03,
       2.49091658e+03, 2.70082986e+03, 2.91900610e+03, 3.14540972e+03,
       3.38000359e+03, 3.62274912e+03, 3.87360643e+03, 4.13253452e+03,
       4.39949148e+03, 4.67443471e+03, 4.95732112e+03, 5.24810728e+03,
       5.54674961e+03, 5.85320444e+03, 6.16742807e+03, 6.48937676e+03,
       6.81900661e+03, 7.15627347e+03, 7.50113266e+03, 7.85353879e+03,
       8.21344538e+03, 8.58080462e+03, 8.95556694e+03, 9.33768077e+03,
       9.72709218e+03, 1.01237446e+04, 1.05275788e+04
    ]
    )
        # fmt: on
    )

    assert mis_rigid.forces[mis_rigid.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [     0.        ,   -695.44989191,  -1390.76098145,  -2085.80340207,
        -2780.44896672,  -3474.57174737,  -4168.04855579,  -4860.75930785,
        -5552.58725831,  -6243.41909941,  -6933.14492308,  -7621.65805293,
        -8308.85475863,  -8994.63387028,  -9678.89631528, -10361.54460307,
       -11042.48228557, -11721.61342139, -12398.84207127, -13074.07184973,
       -13747.20555483, -14418.14489306, -15086.79031112, -15753.04094068,
       -16416.79465562, -17077.94823571, -17736.39762468, -18392.03826576,
       -19044.76549395, -19694.47496121, -20341.06306924, -20984.42738466,
       -21624.46701205, -22261.08290347, -22894.17808613, -23523.65779508,
       -24149.42950266, -24771.40284243, -25389.48943124, -26003.60259834,
       -26613.65703604, -27219.56839029, -27821.25281318, -28418.62650121,
       -29011.60524412, -29600.10400851, -30184.03657848, -30763.31527277,
       -31337.85075352, -31907.55193714, -32472.32601231
    ]
    )
        # fmt: on
    )

    assert mis_rigid.forces[mis_rigid.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [ 0.00000000e+00, -4.36964689e+00, -1.74771689e+01, -3.93186457e+01,
       -6.98878473e+01, -1.09176370e+02, -1.57173806e+02, -2.13867938e+02,
       -2.79244943e+02, -3.53289607e+02, -4.35985520e+02, -5.27315254e+02,
       -6.27260511e+02, -7.35802235e+02, -8.52920676e+02, -9.78595415e+02,
       -1.11280534e+03, -1.25552860e+03, -1.40674247e+03, -1.56642326e+03,
       -1.73454619e+03, -1.91108521e+03, -2.09601285e+03, -2.28930016e+03,
       -2.49091658e+03, -2.70082986e+03, -2.91900610e+03, -3.14540972e+03,
       -3.38000359e+03, -3.62274912e+03, -3.87360643e+03, -4.13253452e+03,
       -4.39949148e+03, -4.67443471e+03, -4.95732112e+03, -5.24810728e+03,
       -5.54674961e+03, -5.85320444e+03, -6.16742807e+03, -6.48937676e+03,
       -6.81900661e+03, -7.15627347e+03, -7.50113266e+03, -7.85353879e+03,
       -8.21344538e+03, -8.58080462e+03, -8.95556694e+03, -9.33768077e+03,
       -9.72709218e+03, -1.01237446e+04, -1.05275788e+04
    ]
    )
        # fmt: on
    )

    assert mis_rigid.forces[mis_rigid.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [    0.        ,   695.44989191,  1390.76098145,  2085.80340207,
        2780.44896672,  3474.57174737,  4168.04855579,  4860.75930785,
        5552.58725831,  6243.41909941,  6933.14492308,  7621.65805293,
        8308.85475863,  8994.63387028,  9678.89631528, 10361.54460307,
       11042.48228557, 11721.61342139, 12398.84207127, 13074.07184973,
       13747.20555483, 14418.14489306, 15086.79031112, 15753.04094068,
       16416.79465562, 17077.94823571, 17736.39762468, 18392.03826576,
       19044.76549395, 19694.47496121, 20341.06306924, 20984.42738466,
       21624.46701205, 22261.08290347, 22894.17808613, 23523.65779508,
       24149.42950266, 24771.40284243, 25389.48943124, 26003.60259834,
       26613.65703604, 27219.56839029, 27821.25281318, 28418.62650121,
       29011.60524412, 29600.10400851, 30184.03657848, 30763.31527277,
       31337.85075352, 31907.55193714, 32472.32601231
    ]
    )
        # fmt: on
    )


def test_mis_rigid_forces_units(mis_rigid_units):
    assert mis_rigid_units.forces[mis_rigid_units.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [0.00000000e+00, 4.36964689e+00, 1.74771689e+01, 3.93186457e+01,
       6.98878473e+01, 1.09176370e+02, 1.57173806e+02, 2.13867938e+02,
       2.79244943e+02, 3.53289607e+02, 4.35985520e+02, 5.27315254e+02,
       6.27260511e+02, 7.35802235e+02, 8.52920676e+02, 9.78595415e+02,
       1.11280534e+03, 1.25552860e+03, 1.40674247e+03, 1.56642326e+03,
       1.73454619e+03, 1.91108521e+03, 2.09601285e+03, 2.28930016e+03,
       2.49091658e+03, 2.70082986e+03, 2.91900610e+03, 3.14540972e+03,
       3.38000359e+03, 3.62274912e+03, 3.87360643e+03, 4.13253452e+03,
       4.39949148e+03, 4.67443471e+03, 4.95732112e+03, 5.24810728e+03,
       5.54674961e+03, 5.85320444e+03, 6.16742807e+03, 6.48937676e+03,
       6.81900661e+03, 7.15627347e+03, 7.50113266e+03, 7.85353879e+03,
       8.21344538e+03, 8.58080462e+03, 8.95556694e+03, 9.33768077e+03,
       9.72709218e+03, 1.01237446e+04, 1.05275788e+04
    ]
    )
        # fmt: on
    )

    assert mis_rigid_units.forces[mis_rigid_units.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [     0.        ,   -695.44989191,  -1390.76098145,  -2085.80340207,
        -2780.44896672,  -3474.57174737,  -4168.04855579,  -4860.75930785,
        -5552.58725831,  -6243.41909941,  -6933.14492308,  -7621.65805293,
        -8308.85475863,  -8994.63387028,  -9678.89631528, -10361.54460307,
       -11042.48228557, -11721.61342139, -12398.84207127, -13074.07184973,
       -13747.20555483, -14418.14489306, -15086.79031112, -15753.04094068,
       -16416.79465562, -17077.94823571, -17736.39762468, -18392.03826576,
       -19044.76549395, -19694.47496121, -20341.06306924, -20984.42738466,
       -21624.46701205, -22261.08290347, -22894.17808613, -23523.65779508,
       -24149.42950266, -24771.40284243, -25389.48943124, -26003.60259834,
       -26613.65703604, -27219.56839029, -27821.25281318, -28418.62650121,
       -29011.60524412, -29600.10400851, -30184.03657848, -30763.31527277,
       -31337.85075352, -31907.55193714, -32472.32601231
    ]
    )
        # fmt: on
    )

    assert mis_rigid_units.forces[mis_rigid_units.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [ 0.00000000e+00, -4.36964689e+00, -1.74771689e+01, -3.93186457e+01,
       -6.98878473e+01, -1.09176370e+02, -1.57173806e+02, -2.13867938e+02,
       -2.79244943e+02, -3.53289607e+02, -4.35985520e+02, -5.27315254e+02,
       -6.27260511e+02, -7.35802235e+02, -8.52920676e+02, -9.78595415e+02,
       -1.11280534e+03, -1.25552860e+03, -1.40674247e+03, -1.56642326e+03,
       -1.73454619e+03, -1.91108521e+03, -2.09601285e+03, -2.28930016e+03,
       -2.49091658e+03, -2.70082986e+03, -2.91900610e+03, -3.14540972e+03,
       -3.38000359e+03, -3.62274912e+03, -3.87360643e+03, -4.13253452e+03,
       -4.39949148e+03, -4.67443471e+03, -4.95732112e+03, -5.24810728e+03,
       -5.54674961e+03, -5.85320444e+03, -6.16742807e+03, -6.48937676e+03,
       -6.81900661e+03, -7.15627347e+03, -7.50113266e+03, -7.85353879e+03,
       -8.21344538e+03, -8.58080462e+03, -8.95556694e+03, -9.33768077e+03,
       -9.72709218e+03, -1.01237446e+04, -1.05275788e+04
    ]
    )
        # fmt: on
    )

    assert mis_rigid_units.forces[mis_rigid_units.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [    0.        ,   695.44989191,  1390.76098145,  2085.80340207,
        2780.44896672,  3474.57174737,  4168.04855579,  4860.75930785,
        5552.58725831,  6243.41909941,  6933.14492308,  7621.65805293,
        8308.85475863,  8994.63387028,  9678.89631528, 10361.54460307,
       11042.48228557, 11721.61342139, 12398.84207127, 13074.07184973,
       13747.20555483, 14418.14489306, 15086.79031112, 15753.04094068,
       16416.79465562, 17077.94823571, 17736.39762468, 18392.03826576,
       19044.76549395, 19694.47496121, 20341.06306924, 20984.42738466,
       21624.46701205, 22261.08290347, 22894.17808613, 23523.65779508,
       24149.42950266, 24771.40284243, 25389.48943124, 26003.60259834,
       26613.65703604, 27219.56839029, 27821.25281318, 28418.62650121,
       29011.60524412, 29600.10400851, 30184.03657848, 30763.31527277,
       31337.85075352, 31907.55193714, 32472.32601231
    ]
    )
        # fmt: on
    )
