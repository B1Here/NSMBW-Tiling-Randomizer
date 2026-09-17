class GenericWidget:
    def reload(self) -> None:
        raise NotImplementedError

    def _init_widgets(self) -> None:
        raise NotImplementedError

    def _create_layout(self) -> None:
        raise NotImplementedError
