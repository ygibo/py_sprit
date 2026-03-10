from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot, inf
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class Location:
    id: str
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class Capacity:
    dimensions: tuple[int, ...] = (0,)

    def __post_init__(self) -> None:
        if not self.dimensions:
            object.__setattr__(self, "dimensions", (0,))
        if any(value < 0 for value in self.dimensions):
            raise ValueError("capacity dimensions must be non-negative")

    @classmethod
    def single(cls, value: int) -> "Capacity":
        return cls((value,))

    def fits(self, other: "Capacity") -> bool:
        size = max(len(self.dimensions), len(other.dimensions))
        lhs = self._normalized(size)
        rhs = other._normalized(size)
        return all(left >= right for left, right in zip(lhs, rhs, strict=True))

    def add(self, other: "Capacity") -> "Capacity":
        size = max(len(self.dimensions), len(other.dimensions))
        return Capacity(
            tuple(
                left + right
                for left, right in zip(
                    self._normalized(size),
                    other._normalized(size),
                    strict=True,
                )
            )
        )

    def _normalized(self, size: int) -> tuple[int, ...]:
        return self.dimensions + (0,) * (size - len(self.dimensions))


@dataclass(frozen=True, slots=True)
class Skills:
    names: frozenset[str] = field(default_factory=frozenset)

    def contains(self, required: "Skills") -> bool:
        return required.names.issubset(self.names)


@dataclass(frozen=True, slots=True)
class TimeWindow:
    start: float = 0.0
    end: float = inf

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("time window start must not be after end")


@runtime_checkable
class TransportCost(Protocol):
    def travel_cost(self, from_location: Location, to_location: Location) -> float:
        ...

    def travel_time(self, from_location: Location, to_location: Location) -> float:
        ...


@runtime_checkable
class VehicleRoutingActivityCosts(Protocol):
    def activity_cost(
        self,
        job_id: str,
        arrival_time: float,
        service_start_time: float,
    ) -> float:
        ...


@dataclass(frozen=True, slots=True)
class EuclideanTransportCost:
    def travel_cost(self, from_location: Location, to_location: Location) -> float:
        return hypot(from_location.x - to_location.x, from_location.y - to_location.y)

    def travel_time(self, from_location: Location, to_location: Location) -> float:
        return self.travel_cost(from_location, to_location)


@dataclass(frozen=True, slots=True)
class ZeroVehicleRoutingActivityCosts:
    def activity_cost(
        self,
        job_id: str,
        arrival_time: float,
        service_start_time: float,
    ) -> float:
        return 0.0
