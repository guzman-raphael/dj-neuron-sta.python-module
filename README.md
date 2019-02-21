# Summary

Packages a DataJoint solution to a Spatio-Temporal Receptive Field (STRF) using Spike-Triggered Average (STA) from provided experimental data involving retinal ganglion cells.

Provides support for:

  - Pipeline Design
  - STA Computation
  - Computation Visualization


# Instructions

$ pip3 install -i https://test.pypi.org/simple/ dj-neuron-rguzman


# Build

$ rm -r dist && rm -r build && rm -r dj_neuron_rguzman.egg-info

$ python3 setup.py sdist bdist_wheel

$ python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*


# Points for Improvement

- Identify better way of passing argument to import module than using a config file.
- Identify Neuron import files by primary keys associated with table.
- Utilize "SpikeTriggeredAverages" (i.e. the output) as table name instead of presently "STRFCalcs".
- Optimize runtime for STA algorithm.
- Font size in spikes plot.
- Utilize file directories as parameters in dj.Lookup. Is this valid for Import tables?


# Assumptions

- Sample number refers to ID of mouse.
- Subject name refers to specific retina cells.
- Movies can be reused between subjects as stimuli.
