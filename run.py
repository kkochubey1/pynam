#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   PyNAM -- Python Neural Associative Memory Simulator and Evaluator
#   Copyright (C) 2015 Andreas Stöckel
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# The "run.py" script is the main script of PyNAM. It can operate in two
# different modes:
#
#   * The "experiment mode". In this case the name of the PyNN backend is passed
#     as a single parameter. A configuration file will be read from the
#     "config.json" file. Optionally, the name of the configuration file can
#     be passed as a second parameter. The experiment is splitted into a list
#     of simulations that can run concurrently. Writes the results to a Matlab
#     file "result.mat"
#
#     Examples:
#         ./run.py nest
#         ./run.py nest experiment.json experiment.mat
#
#   * The "simulation mode". Performs a single simulation run. Reads the
#     simulation parameters from stdin, writes the result to stdout. Both stdin
#     and stdout are in JSON format. Simulation mode is activated by passing the
#     single "--simulation" parameter.
#
#     Examples:
#         cat config.json | ./run.py --simulation > result.json

import numpy as np
import pynam
import pynam.entropy
import pynnless as pynl
import scipy.io as scio
import sys

if (len(sys.argv) != 2):
    print("Usage: " + sys.argv[0] + " <SIMULATOR>")
    sys.exit(1)

# Generate test data
print "Generate test data..."

data_params = {
    "n_bits_in": 32,
    "n_bits_out": 32,
    "n_ones_in": 3,
    "n_ones_out": 3
}

topology_params = {
    "w": 0.011,
    "params": {
        "cm": 0.2,
        "e_rev_E": -40,
        "e_rev_I": -60,
        "v_rest": -50,
        "v_reset": -70,
        "v_thresh": -47,
#        "tau_m": 409.0,
#        "tau_refrac": 20.0
    }
}

input_params = {
    "time_window": 500.0,
    "sigma_t": 5.0
}

# Build the network and the metadata
print "Build network..."
builder = pynam.NetworkBuilder(data_params=data_params)
net = builder.build(topology_params=topology_params, input_params=input_params)

# Run the simulation
print "Initialize simulator..."
sim = pynl.PyNNLess(sys.argv[1])
print "Run simulation..."
output = sim.run(net)

# Fetch the output times and output indices from the output data
print "Analyze result..."
analysis = net.build_analysis(output)[0]
I, mat_out, errs = analysis.calculate_storage_capactiy()
I_ref, mat_out_ref, errs_ref = analysis.calculate_max_storage_capacity()
latency = analysis.calculate_latencies()

print "SAMPLES: ", analysis["data_params"]["n_samples"]
print "INFORMATION: ", I, " of a theoretical ", I_ref
print "MAT OUT:\n", np.array(mat_out, dtype=np.uint8)
print "MAT OUT (reference):\n", mat_out_ref
print "MAT OUT EXPECTED:\n", analysis["mat_out"]
print "AVG. LATENCY:\n", np.mean(latency)
print "LATENCIES:\n", latency


