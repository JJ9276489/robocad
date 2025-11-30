class Part:
    def build(self):
        '''Return a CadQuery solid. Must be implemented by subclasses.'''
        raise NotImplementedError
    
    def export_stl(self, path):
        solid = self.build()
        import cadquery as cq
        cq.exporters.export(solid, path)