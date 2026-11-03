"""Camera frames and image features for the PGFUN gun positioner's host.

`helper_stream` runs the AVFoundation capture helper and reads its stream,
`imageio` decodes the frames and `features` finds the aiming dot, wire tip and
seam in them. None of these modules can command motion or laser emission.
"""
