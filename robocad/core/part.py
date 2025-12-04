from abc import ABC, abstractmethod
import cadquery as cq

class Part(ABC):
    '''
    Base class for all parametric parts.

    Subclasses must implement build() to return a CadQuery solid.
    '''

    @abstractmethod
    def build(self) -> cq.Workplane:
        '''Build and returnt he CadQuery solid representing this part.'''
        raise NotImplementedError
    
    def export_stl(self, path: str) -> None:
        '''Export the built solid as an STL file.'''
        solid = self.build()
        cq.exporters.export(solid, path)