# Exception, errors, and warnings

# errors and exceptions ----------------------

# General
class MissingDataError(Exception): pass
class NotImplementedError(Exception): pass
class MergeError(Exception): pass

# Data problems
class DataError(Exception): pass

class BeamError(DataError): pass
class CycleError(DataError): pass
class DetectorError(DataError): pass
class ValveError(DataError): pass

# warnings -----------------------------------
class CycleWarning(Warning): pass
class MissingDataWarning(Warning): pass
class MergeWarning(Warning): pass