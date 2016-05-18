
class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

States = Namespace(
    NO_INFO='no_info',
    NEW='new',
    YOUNG='young',
    OLD='old',
    ERROR='error'
)

