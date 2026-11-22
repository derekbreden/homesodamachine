"""The cup reader imports find_peaks for its printed-mark tracer, which this replay does not run."""
def find_peaks(*a, **k):
    raise NotImplementedError('find_peaks is not part of the level reader')
