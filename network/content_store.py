class ContentStore():
    def __init__(self, topology):
        self.topology = topology

    def find(self, content_name):
        return {
            'content': content_name,
            'base': ['h1', 'h3', 'h8'],
            'enhancement': ['h8', 'h9', 'h12']
        }
