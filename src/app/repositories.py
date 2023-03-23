import abc

from django.db.models import Model, QuerySet

"""
Repository module

For design pattern of this application, I followed a Repository Patter.
This allows to a simplifying abstraction over data storage, allowing us 
to decouple our model layer from the data layer. 

We present an abstract repository class and a repository model class,
from which specific repositories for different models will be inherited.

In this Base Class we define the common methods that will interact with
out database, for all repositories within the application.

"""


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_attr(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def get_all(self, *args, **kwargs):
        raise NotImplementedError


class BaseRepository(AbstractRepository):
    def __init__(self, model: Model):
        self.model: Model = model

    def get_by_attr(self, **kwargs) -> QuerySet:
        return self.model.objects.filter(**kwargs)

    def get_all(self) -> QuerySet:
        return self.model.objects.all()

    def add_related_related_obj(self, obj, **kwargs) -> QuerySet:
        key = next((k for k in kwargs.keys() if "__id" in k), None)
        if not key:
            raise Exception("Must send id key for search")
        _id = kwargs.get(key)
        key = key.split("__")[0]
        attr = getattr(obj, key)
        attr.add(_id)
        return self.save(obj)

    def _persist(self, obj: Model) -> Model:
        return obj.save()

    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)

    def save(self, obj: Model) -> Model:
        self._persist(obj)
        return obj.refresh_from_db()

    def delete(self, obj: Model) -> Model:
        return obj.delete()
