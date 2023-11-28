from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from omu.client import Client
    from omu.extension.server.model.extension_info import ExtensionInfo


class Extension(abc.ABC):
    pass


class ExtensionType[T: Extension]():
    def __init__(
        self,
        info: ExtensionInfo,
        create: Callable[[Client], T],
        dependencies: List[ExtensionType],
    ):
        self._info = info
        self._create = create
        self._dependencies = dependencies

    @property
    def key(self) -> str:
        return self._info.key()

    def create(self, client: Client) -> T:
        return self._create(client)

    def dependencies(self) -> List[ExtensionType]:
        return self._dependencies


def define_extension_type[
    T: Extension
](
    info: ExtensionInfo,
    create: Callable[[Client], T],
    dependencies: Callable[[], List[ExtensionType]],
):
    return ExtensionType(info, create, dependencies())
