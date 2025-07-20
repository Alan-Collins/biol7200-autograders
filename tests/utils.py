class PointCounter():
    def __init__(self, start=0):
        self._setup(start)
    
    def _setup(self, start=0):
        self._counter = start
    
    def reset(self, start=0) -> int:
        self._setup(start)
        return self._counter

    def next(self) -> int:
        self._counter += 1
        return self._counter

    def __hash__(self):
        return hash(self._counter)
    
    def __eq__(self, value):
        return self._counter == value

    def __str__(self):
        return str(self._counter)