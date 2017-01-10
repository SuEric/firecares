import numbers
from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage


class CachedS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name


def dictfetchall(cursor):
    """
    Returns all rows from a cursor as a dict
    """
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def lenient_summation(*args, **kwargs):
    # Sums across all number-like items (True/False ARE considered numbers, 1/0 respectively),
    # if ALL items are not numbers, then return None
    mapping = kwargs.pop('mapping', None)
    if mapping:
        args = map(mapping, args)
    nums = filter(lambda x: isinstance(x, numbers.Number), args)
    if len(nums):
        return sum(nums)


def lenient_mean(*args, **kwargs):
    # Computes average across all number-like items (True/False ARE considered numbers, 1/0 respectively)
    # returns None if all items are None
    mapping = kwargs.pop('mapping', None)
    if mapping:
        args = map(mapping, args)
    items = filter(lambda x: isinstance(x, numbers.Number), args)
    if len(items):
        return sum(items) / float(max(len(items), 1))


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
