# COMBINE
COMBINE - COst Minimization Bed INvErsion model for glaciers and ice caps

This project is an adaption/extension to [OGGM](https://github.com/OGGM/oggm) and utilizes it's 2D Shallow-Ice-Approximation dynamical model together with backwards functionalities (Automatic/Algorithmic Differentiation) of [PyTorch](https://pytorch.org/) to enable a cost function based inversion of bedrock topography based on surface outlines, surface topography and optionally also existing ice thickness measurements for ice caps and glaciers.
