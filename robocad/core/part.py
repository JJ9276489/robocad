from abc import ABC, abstractmethod
from build123d import Part, export_stl, export_step

class Component(ABC):
    '''
    Base class for all parametric parts.
    '''

    @abstractmethod
    def build(self) -> Part:
        '''
        Build and return the Build123d part representing this component.
        
        Returns:
            Part: A build123d Part object (Topological solid)
        '''
        raise NotImplementedError
    
    def export_stl(self, path: str) -> None:
        '''Export the built solid as an STL file.'''
        solid = self.build()
        export_stl(solid, path)
    
    def export_step(self, path: str) -> None:
        '''Export the built solid as a STEP file.'''
        solid = self.build()
        export_step(solid, path)