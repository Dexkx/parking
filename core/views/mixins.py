from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action


class NewCreatedModelMixin(mixins.CreateModelMixin):
    """
    Crear una lista de instancias del modelo
    """

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            return self.bulk_create(request, *args, **kwargs)

        return super().create(request, *args, **kwargs)

    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        self.perform_bulk_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_bulk_create(self, serializer):
        serializer.save()


class NestedRouterModelMixin:
    """
    Mixin para las vistas con url anidades desde nested router
    Example nested_config:
        [
            {
                'lookup': 'query', <- Debe ser el nombre del lookup del nested router
                'field_name': 'fk', <- Debe ser el nombre de la FK del modelo
                'model_class': models.Model <- Debe ser la clase de la FK
            },
        ]
    """

    nested_instances = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.nested_instances is not None:
            if not isinstance(self.nested_instances, (list, tuple)):
                raise AssertionError(
                    "La instancias de nested debe ser una lista o tupla de diccionarios"
                )

            from django.db.models import Model

            for config_nested in self.nested_instances:
                if not isinstance(config_nested, dict):
                    raise AssertionError("Cada instancia debe ser un diccionario")

                if "lookup" not in config_nested:
                    raise AssertionError(
                        'La clave "lookup" es obligatoria en cada instance'
                    )
                elif "field_name" not in config_nested:
                    raise AssertionError(
                        'La clave "field_name" es obligatoria en cada instance'
                    )
                elif "model_class" not in config_nested:
                    raise AssertionError(
                        'La clave "model_class" es obligatoria en cada instance'
                    )

                if not isinstance(config_nested.get("lookup"), str):
                    raise AssertionError(
                        'La valor de la clave "lookup" debe ser un string'
                    )
                elif not isinstance(config_nested.get("field_name"), str):
                    raise AssertionError(
                        'La valor de la clave "field_name" debe ser un string'
                    )
                elif not issubclass(config_nested.get("model_class"), Model):
                    raise AssertionError(
                        'La valor de la clave "model_class" debe ser un instancia de un "models.Model"'
                    )

    def get_nested_value(self, lookup):
        value = self.kwargs.get(f"{lookup}_pk")
        return value

    def get_param_query(self, instance_model=False):
        params = {}
        for n_instance in self.nested_instances:
            lookup = n_instance.get("lookup")
            value = self.get_nested_value(lookup)
            if value is None:
                continue

            if instance_model:
                value = self.get_instance_nested(
                    value, lookup, n_instance.get("model_class")
                )

            field_name = n_instance.get("field_name")
            params.update({field_name: value})

        return params

    def get_instance_nested(self, nested_value, lookup, model_class):
        try:
            return model_class.objects.get(pk=nested_value)
        except model_class.DoesNotExist:
            raise NotFound(f"Instancia {lookup}: {nested_value} - No encontrada")

    def get_queryset(self):
        if self.nested_instances is None:
            return super().get_queryset()

        return self.queryset.filter(**self.get_param_query())

    def create(self, request, *args, **kwargs):
        for k, v in self.get_param_query().items():
            request.data[k] = v

        return super().create(request, *args, **kwargs)

    def bulk_create(self, request, *args, **kwargs):
        for k, v in self.get_param_query().items():
            request.data[k] = v

        return super().bulk_create(request, *args, **kwargs)

        # if hasattr(serializer, '_data'):
        #     for i, obj in enumerate(created_objects):
        #         serializer._data[i][self.field_name] = getattr(obj, self.field_name)

class CompositeFKMixin:
    """
    Mixin que asegura la existencia de parámetros en la URL para métodos especificos.
    Requiere definir la lista 'url_params_required' en la vista.

    Ejemplo de uso:
        url_params_required = (
            {
                "lookup": "empresa" ,
                "field_name": "empresa_id",
            },
        )
    """
    _prefix = 'new_'
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        obj = get_object_or_404(queryset, **self.get_filters_composite_fk())

        self.check_object_permissions(self.request, obj)

        return obj
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filters = self.get_filters_composite_fk()
        return queryset.filter(**filters)
    
    def get_filters_composite_fk(self):
        params_required = self.url_params_required

        # assert all(param.get("lookup") in self.kwargs for param in params_required), (
        #     "Expected view %s to be called with a URL keyword argument "
        #     'named "%s". Fix your URL conf, or set the `.lookup_field` '
        #     "attribute on the view correctly."
        #     % (self.__class__.__name__, params_required)
        # )
        
        return {
            param.get("field_name"): lookup
            for param in params_required
            if (lookup := self.kwargs.get(param.get("lookup")))
        }

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        if not hasattr(cls, "url_params_required"):
            assert False, "La clase debe tener el atributo 'url_params_required'"

        params = cls.url_params_required
        segments_exists = getattr(cls, "url_existing_params", [])        
        
        path_segments = [
            f"(?P<{param.get('lookup')}>[^/.]+)"
            for param in params
            if param.get('lookup') not in segments_exists
        ]
        extra_path = "/".join(path_segments)
        methods = ("get", "put", "patch", "delete")

        def composite_fk(self, request, *args, **kwargs):
            method = request.method.lower()
            
            match method:
                case "get":
                    if kwargs.get('pk'):
                        return super().retrieve(request, *args, **kwargs)
                    return super().list(request, *args, **kwargs)
                case "put":
                    return super().update(request, *args, **kwargs)
                case "patch":
                    return super().partial_update(request, *args, **kwargs)
                case "delete":
                    return super().destroy(request, *args, **kwargs)

        decorated_method = action(
            detail=False, methods=methods, url_path=extra_path
        )(composite_fk)
        setattr(cls, "composite_fk", decorated_method)

class DataSRMixin:
    def get_data_serializer(self, query, **kwargs):
        if "many" not in kwargs:
            kwargs['many'] = True

        serializer = self.get_serializer(query, **kwargs)
        return serializer.data