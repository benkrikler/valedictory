import six


class ValidatorException(Exception):
    pass


class BaseValidator(object):
    def __init__(self, node=""):
        self.__name = node

    @property
    def node(self):
        return self.__name

    def __call__(self, instance):
        raise NotImplemented

    def _raise(self, instance=None, msg=None):
        raise ValidatorException(msg)


class SimpleType(BaseValidator):
    def __init__(self, class_type, **kwargs):
        super(self, SimpleType).__init__(**kwargs)

    def __call__(self, instance):
        if not isinstance(instance, self.class_type):
            self._raise()
        return instance


class Str(SimpleType):
    class_type = six.string_types


class Int(SimpleType):
    class_type = int


class Bool(SimpleType):
    class_type = bool


class Float(SimpleType):
    class_type = float


class List(BaseValidator):
    def __init__(self, element_type, **kwargs):
        super(self, List).__init__(**kwargs)
        self.element_type = element_type

    def __call__(self, instance):
        if not isinstance(instance, (list, tuple)):
            self._raise()
        return (self.element_type(ele) for ele in instance)


class Dict(BaseValidator):
    def __init__(self, **kwargs):
        node = kwargs.pop("node", "")
        super(self, Dict).__init__(node=node)
        self.key_value_types = kwargs

    def __call__(self, instance):
        if not isinstance(instance, dict):
            self._raise()
        out_dict = {}
        for key, val in instance.items():
            value_type = self.key_value_types.get(key, None)
            if not value_type:
                self._raise(msg="Unknown key")
            out_dict[key] = value_type(val)
        return out_dict


class Choice(BaseValidator):
    def __init__(self, *choices, **kwargs):
        super(self, Choice).__init__(**kwargs)
        self.validator_choices = (c for c in choices if isinstance(c, BaseValidator))
        self.instance_choices = (c for c in choices if not in self.validator_choices)

    def __call__(self, instance):
        if instance in self.instance_choices:
            return instance

        for choice in self.validator_choices:
            try:
                return choice(instance)
            except ValidatorException:
                continue
        self._raise(msg="No valid choice")