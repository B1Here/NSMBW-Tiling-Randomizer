class GenericWidget:
    def reload(self):
        raise NotImplementedError

    def _init_widgets(self):
        raise NotImplementedError

    def _create_layout(self):
        raise NotImplementedError
