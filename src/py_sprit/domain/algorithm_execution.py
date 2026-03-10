from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from random import Random

from py_sprit.domain.extension_contracts import (
    ConstraintEvaluationContext,
    ConstraintRegistration,
    ConstraintRegistrationStatus,
)
from py_sprit.domain.problem_definition import (
    Break,
    Job,
    ProblemDefinitionStatus,
    Service,
    Vehicle,
    VehicleRoutingProblem,
)
from py_sprit.domain.shared import Capacity


class SearchExecutionStatus(str, Enum):
    ACCEPTED = "Accepted"
    COMPLETED = "Completed"


@dataclass(frozen=True, slots=True)
class TerminationCriterion:
    max_iterations: int = 100

    def __post_init__(self) -> None:
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")


@dataclass(frozen=True, slots=True)
class TourActivity:
    job: Service
    arrival_time: float
    service_start_time: float
    service_end_time: float
    position: int


@dataclass(frozen=True, slots=True)
class VehicleRoute:
    vehicle: Vehicle
    jobs: tuple[Service, ...]
    activities: tuple[TourActivity, ...]
    cost: float
    end_time: float


@dataclass(frozen=True, slots=True)
class VehicleRoutingProblemSolution:
    routes: tuple[VehicleRoute, ...]
    unassigned_jobs: tuple[Job, ...]
    cost: float


@dataclass(frozen=True, slots=True)
class SearchIterationLog:
    iteration: int
    candidate_cost: float
    candidate_unassigned_job_count: int
    candidate_route_count: int
    accepted_as_incumbent: bool
    incumbent_cost_after_iteration: float
    incumbent_unassigned_job_count_after_iteration: int
    incumbent_route_count_after_iteration: int


@dataclass(frozen=True, slots=True)
class SearchTechnicalLog:
    job_count: int
    vehicle_count: int
    constraint_registration_count: int
    max_iterations: int
    used_provided_initial_solution: bool
    elapsed_ms: float
    initial_cost: float
    initial_unassigned_job_count: int
    initial_route_count: int
    final_incumbent_cost: float
    final_incumbent_unassigned_job_count: int
    final_incumbent_route_count: int
    iterations: tuple[SearchIterationLog, ...]


@dataclass(frozen=True, slots=True)
class SearchExecutionCompletedEvent:
    name: str = "SearchExecutionCompletedEvent"


@dataclass(frozen=True, slots=True)
class SearchAcceptanceResult:
    is_success: bool
    next_state: "SearchExecution" | None
    accepted_problem: VehicleRoutingProblem | None
    initial_solution: VehicleRoutingProblemSolution | None = None
    termination_criterion: TerminationCriterion | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class SearchCompletionResult:
    is_success: bool
    next_state: "SearchExecution" | None
    best_solution: VehicleRoutingProblemSolution | None
    unassigned_jobs: tuple[Job, ...] = ()
    event: SearchExecutionCompletedEvent | None = None
    technical_log: SearchTechnicalLog | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class SearchExecution:
    problem: VehicleRoutingProblem
    termination_criterion: TerminationCriterion
    initial_solution: VehicleRoutingProblemSolution | None = None
    status: SearchExecutionStatus = SearchExecutionStatus.ACCEPTED

    @classmethod
    def accept(
        cls,
        problem: VehicleRoutingProblem,
        termination_criterion: TerminationCriterion,
        initial_solution: VehicleRoutingProblemSolution | None,
    ) -> SearchAcceptanceResult:
        execution = cls(
            problem=problem,
            termination_criterion=termination_criterion,
            initial_solution=initial_solution,
            status=SearchExecutionStatus.ACCEPTED,
        )
        return SearchAcceptanceResult(
            is_success=True,
            next_state=execution,
            accepted_problem=problem,
            initial_solution=initial_solution,
            termination_criterion=termination_criterion,
        )

    def complete(
        self,
        best_solution: VehicleRoutingProblemSolution,
    ) -> SearchCompletionResult:
        completed_execution = replace(self, status=SearchExecutionStatus.COMPLETED)
        return SearchCompletionResult(
            is_success=True,
            next_state=completed_execution,
            best_solution=best_solution,
            unassigned_jobs=best_solution.unassigned_jobs,
            event=SearchExecutionCompletedEvent(),
        )


@dataclass(frozen=True, slots=True)
class SearchStartPolicy:
    def evaluate(
        self,
        problem: VehicleRoutingProblem,
        initial_solution: VehicleRoutingProblemSolution | None,
        termination_criterion: TerminationCriterion,
    ) -> SearchAcceptanceResult:
        if problem.status is not ProblemDefinitionStatus.DEFINED:
            return SearchAcceptanceResult(
                is_success=False,
                next_state=None,
                accepted_problem=None,
                initial_solution=initial_solution,
                termination_criterion=termination_criterion,
                reason="問題モデルが探索可能状態でない",
            )
        if any(isinstance(job, Break) for job in problem.jobs):
            return SearchAcceptanceResult(
                is_success=False,
                next_state=None,
                accepted_problem=None,
                initial_solution=initial_solution,
                termination_criterion=termination_criterion,
                reason="問題モデルが探索可能状態でない",
            )
        if initial_solution is not None and not _is_initial_solution_consistent(
            problem,
            initial_solution,
        ):
            return SearchAcceptanceResult(
                is_success=False,
                next_state=None,
                accepted_problem=None,
                initial_solution=initial_solution,
                termination_criterion=termination_criterion,
                reason="問題モデルが探索可能状態でない",
            )
        return SearchExecution.accept(
            problem=problem,
            termination_criterion=termination_criterion,
            initial_solution=initial_solution,
        )


@dataclass(frozen=True, slots=True)
class BestSolutionSelectionService:
    def select(
        self,
        candidate_solutions: tuple[VehicleRoutingProblemSolution, ...],
    ) -> VehicleRoutingProblemSolution | None:
        if not candidate_solutions:
            return None
        best = min(candidate_solutions, key=_solution_rank)
        if not best.routes and best.unassigned_jobs:
            return None
        return best


@dataclass(frozen=True, slots=True)
class SearchResultAssemblyPolicy:
    def assemble(
        self,
        completion_result: SearchCompletionResult,
    ) -> SearchCompletionResult:
        return completion_result


@dataclass(slots=True)
class ProblemDefinitionGateway:
    gateway: object

    def confirmSearchable(self, problem: VehicleRoutingProblem) -> bool:
        return bool(self.gateway.confirm_searchable(problem))


@dataclass(slots=True)
class SolutionModelGateway:
    gateway: object

    def returnSolution(self, result: SearchCompletionResult) -> SearchCompletionResult:
        return self.gateway.return_solution(result)


@dataclass(slots=True)
class RandomRuin:
    rng: Random
    share: float = 0.25

    def ruin(
        self,
        solution: VehicleRoutingProblemSolution,
    ) -> tuple[tuple[tuple[Vehicle, tuple[Service, ...]], ...], tuple[Service, ...]]:
        assignments = [(route.vehicle, list(route.jobs)) for route in solution.routes]
        assigned_jobs = [job for _, jobs in assignments for job in jobs]
        if not assigned_jobs:
            return tuple((vehicle, tuple(jobs)) for vehicle, jobs in assignments), ()
        remove_count = max(1, int(len(assigned_jobs) * self.share))
        removed_jobs = tuple(
            self.rng.sample(assigned_jobs, min(remove_count, len(assigned_jobs)))
        )
        removed_ids = {job.id for job in removed_jobs}
        remaining = []
        for vehicle, jobs in assignments:
            remaining_jobs = tuple(job for job in jobs if job.id not in removed_ids)
            remaining.append((vehicle, remaining_jobs))
        return tuple(remaining), removed_jobs


@dataclass(frozen=True, slots=True)
class BestInsertion:
    def insert_jobs(
        self,
        problem: VehicleRoutingProblem,
        seeded_assignments: tuple[tuple[Vehicle, tuple[Service, ...]], ...],
        jobs: tuple[Service, ...],
        registrations: tuple[ConstraintRegistration, ...],
    ) -> VehicleRoutingProblemSolution:
        route_jobs = {vehicle.id: list(route_jobs) for vehicle, route_jobs in seeded_assignments}
        vehicles = [vehicle for vehicle, _ in seeded_assignments] or list(problem.vehicles)
        if not route_jobs:
            route_jobs = {vehicle.id: [] for vehicle in vehicles}
        unassigned: list[Job] = []
        for job in jobs:
            best_choice: tuple[float, Vehicle, int] | None = None
            for vehicle in vehicles:
                current_jobs = route_jobs.setdefault(vehicle.id, [])
                for position in range(len(current_jobs) + 1):
                    candidate_jobs = tuple(current_jobs[:position] + [job] + current_jobs[position:])
                    candidate_route = evaluate_route(problem, vehicle, candidate_jobs, registrations)
                    if candidate_route is None:
                        continue
                    if best_choice is None or candidate_route.cost < best_choice[0]:
                        best_choice = (candidate_route.cost, vehicle, position)
            if best_choice is None:
                unassigned.append(job)
                continue
            _, vehicle, position = best_choice
            route_jobs[vehicle.id].insert(position, job)
        finalized_routes = []
        for vehicle in problem.vehicles:
            jobs_for_vehicle = tuple(route_jobs.get(vehicle.id, []))
            if not jobs_for_vehicle:
                continue
            route = evaluate_route(problem, vehicle, jobs_for_vehicle, registrations)
            if route is None:
                unassigned.extend(jobs_for_vehicle)
                continue
            finalized_routes.append(route)
        return build_solution(tuple(finalized_routes), tuple(unassigned))


@dataclass(frozen=True, slots=True)
class SearchStrategy:
    ruin: RandomRuin
    insertion: BestInsertion

    def improve(
        self,
        problem: VehicleRoutingProblem,
        current_solution: VehicleRoutingProblemSolution,
        registrations: tuple[ConstraintRegistration, ...],
    ) -> VehicleRoutingProblemSolution:
        seeded_assignments, ruined_jobs = self.ruin.ruin(current_solution)
        pending_jobs = tuple(job for job in current_solution.unassigned_jobs if isinstance(job, Service))
        return self.insertion.insert_jobs(
            problem=problem,
            seeded_assignments=seeded_assignments,
            jobs=ruined_jobs + pending_jobs,
            registrations=registrations,
        )


@dataclass(frozen=True, slots=True)
class VehicleRoutingAlgorithm:
    strategy: SearchStrategy

    def solve(
        self,
        problem: VehicleRoutingProblem,
        initial_solution: VehicleRoutingProblemSolution | None,
        termination_criterion: TerminationCriterion,
        registrations: tuple[ConstraintRegistration, ...],
    ) -> tuple[VehicleRoutingProblemSolution, ...]:
        incumbent = initial_solution or build_greedy_initial_solution(problem, registrations)
        candidates = [incumbent]
        current = incumbent
        for _ in range(termination_criterion.max_iterations):
            candidate = self.strategy.improve(problem, current, registrations)
            candidates.append(candidate)
            if _is_better_solution(candidate, current):
                current = candidate
        return tuple(candidates)


@dataclass(slots=True)
class SearchExecutionService:
    rng: Random
    registry_gateway: object

    def count_available_registrations(self) -> int:
        return len(tuple(self.registry_gateway.available_registrations()))

    def run(
        self,
        problem: VehicleRoutingProblem,
        termination_criterion: TerminationCriterion,
        initial_solution: VehicleRoutingProblemSolution | None,
    ) -> tuple[VehicleRoutingProblemSolution, ...]:
        strategy = SearchStrategy(
            ruin=RandomRuin(rng=self.rng),
            insertion=BestInsertion(),
        )
        algorithm = VehicleRoutingAlgorithm(strategy=strategy)
        registrations = tuple(self.registry_gateway.available_registrations())
        return algorithm.solve(
            problem=problem,
            initial_solution=initial_solution,
            termination_criterion=termination_criterion,
            registrations=registrations,
        )


def _is_initial_solution_consistent(
    problem: VehicleRoutingProblem,
    initial_solution: VehicleRoutingProblemSolution,
) -> bool:
    known_vehicle_ids = {vehicle.id for vehicle in problem.vehicles}
    known_job_ids = {job.id for job in problem.jobs}
    route_job_ids: set[str] = set()
    for route in initial_solution.routes:
        if route.vehicle.id not in known_vehicle_ids:
            return False
        for job in route.jobs:
            route_job_ids.add(job.id)
            if job.id not in known_job_ids:
                return False
    unassigned_ids = {job.id for job in initial_solution.unassigned_jobs}
    return route_job_ids.isdisjoint(unassigned_ids)


def build_search_technical_log(
    *,
    problem: VehicleRoutingProblem,
    termination_criterion: TerminationCriterion,
    initial_solution: VehicleRoutingProblemSolution | None,
    candidate_solutions: tuple[VehicleRoutingProblemSolution, ...],
    constraint_registration_count: int,
    elapsed_ms: float,
) -> SearchTechnicalLog | None:
    if not candidate_solutions:
        return None
    initial_candidate = candidate_solutions[0]
    incumbent = initial_candidate
    iterations: list[SearchIterationLog] = []
    for iteration, candidate in enumerate(candidate_solutions[1:], start=1):
        accepted_as_incumbent = _is_better_solution(candidate, incumbent)
        if accepted_as_incumbent:
            incumbent = candidate
        iterations.append(
            SearchIterationLog(
                iteration=iteration,
                candidate_cost=candidate.cost,
                candidate_unassigned_job_count=len(candidate.unassigned_jobs),
                candidate_route_count=len(candidate.routes),
                accepted_as_incumbent=accepted_as_incumbent,
                incumbent_cost_after_iteration=incumbent.cost,
                incumbent_unassigned_job_count_after_iteration=len(incumbent.unassigned_jobs),
                incumbent_route_count_after_iteration=len(incumbent.routes),
            )
        )
    return SearchTechnicalLog(
        job_count=len(problem.jobs),
        vehicle_count=len(problem.vehicles),
        constraint_registration_count=constraint_registration_count,
        max_iterations=termination_criterion.max_iterations,
        used_provided_initial_solution=initial_solution is not None,
        elapsed_ms=elapsed_ms,
        initial_cost=initial_candidate.cost,
        initial_unassigned_job_count=len(initial_candidate.unassigned_jobs),
        initial_route_count=len(initial_candidate.routes),
        final_incumbent_cost=incumbent.cost,
        final_incumbent_unassigned_job_count=len(incumbent.unassigned_jobs),
        final_incumbent_route_count=len(incumbent.routes),
        iterations=tuple(iterations),
    )


def _solution_rank(
    solution: VehicleRoutingProblemSolution,
) -> tuple[int, float]:
    return (len(solution.unassigned_jobs), solution.cost)


def _is_better_solution(
    candidate: VehicleRoutingProblemSolution,
    incumbent: VehicleRoutingProblemSolution,
) -> bool:
    return _solution_rank(candidate) < _solution_rank(incumbent)


def build_greedy_initial_solution(
    problem: VehicleRoutingProblem,
    registrations: tuple[ConstraintRegistration, ...],
) -> VehicleRoutingProblemSolution:
    insertion = BestInsertion()
    jobs = tuple(job for job in problem.jobs if isinstance(job, Service))
    seeded_assignments = tuple((vehicle, tuple()) for vehicle in problem.vehicles)
    return insertion.insert_jobs(problem, seeded_assignments, jobs, registrations)


def evaluate_route(
    problem: VehicleRoutingProblem,
    vehicle: Vehicle,
    jobs: tuple[Service, ...],
    registrations: tuple[ConstraintRegistration, ...],
) -> VehicleRoute | None:
    current_location = vehicle.start_location
    current_time = vehicle.earliest_start
    total_cost = 0.0
    used_capacity = Capacity()
    activities: list[TourActivity] = []
    for position, job in enumerate(jobs):
        if not vehicle.skills.contains(job.required_skills):
            return None
        used_capacity = used_capacity.add(job.demand)
        if not vehicle.vehicle_type.capacity.fits(used_capacity):
            return None
        travel_time = problem.transport_cost.travel_time(current_location, job.location)
        travel_cost = problem.transport_cost.travel_cost(current_location, job.location)
        arrival_time = current_time + travel_time
        service_start_time = max(arrival_time, job.time_window.start)
        if service_start_time > job.time_window.end:
            return None
        service_end_time = service_start_time + job.service_duration
        if service_end_time > vehicle.latest_end:
            return None
        total_cost += travel_cost + problem.activity_costs.activity_cost(
            job.id,
            arrival_time,
            service_start_time,
        )
        activities.append(
            TourActivity(
                job=job,
                arrival_time=arrival_time,
                service_start_time=service_start_time,
                service_end_time=service_end_time,
                position=position,
            )
        )
        current_time = service_end_time
        current_location = job.location
    end_location = vehicle.end_location or vehicle.start_location
    return_travel_time = problem.transport_cost.travel_time(current_location, end_location)
    return_travel_cost = problem.transport_cost.travel_cost(current_location, end_location)
    route_end_time = current_time + return_travel_time
    if route_end_time > vehicle.latest_end:
        return None
    provisional_route = VehicleRoute(
        vehicle=vehicle,
        jobs=jobs,
        activities=tuple(activities),
        cost=total_cost + return_travel_cost + vehicle.vehicle_type.fixed_cost,
        end_time=route_end_time,
    )
    penalty = evaluate_constraints(provisional_route, registrations)
    if penalty is None:
        return None
    return VehicleRoute(
        vehicle=vehicle,
        jobs=jobs,
        activities=tuple(activities),
        cost=provisional_route.cost + penalty,
        end_time=route_end_time,
    )


def evaluate_constraints(
    route: VehicleRoute,
    registrations: tuple[ConstraintRegistration, ...],
) -> float | None:
    total_penalty = 0.0
    for registration in registrations:
        if registration.status is not ConstraintRegistrationStatus.AVAILABLE_FOR_SEARCH:
            continue
        target_kind = registration.target_descriptor.target_kind
        target_id = registration.target_descriptor.target_id
        contexts: list[ConstraintEvaluationContext] = []
        if target_kind == "job":
            for job in route.jobs:
                if target_id is None or job.id == target_id:
                    contexts.append(
                        ConstraintEvaluationContext(
                            job=job,
                            vehicle=route.vehicle,
                            vehicle_route=route,
                        )
                    )
        elif target_kind == "vehicle":
            if target_id is None or route.vehicle.id == target_id:
                contexts.append(
                    ConstraintEvaluationContext(
                        vehicle=route.vehicle,
                        vehicle_route=route,
                    )
                )
        elif target_kind == "vehicle_route":
            contexts.append(
                ConstraintEvaluationContext(
                    vehicle=route.vehicle,
                    vehicle_route=route,
                )
            )
        elif target_kind == "tour_activity":
            for activity in route.activities:
                if target_id is None or activity.job.id == target_id:
                    contexts.append(
                        ConstraintEvaluationContext(
                            job=activity.job,
                            vehicle=route.vehicle,
                            vehicle_route=route,
                            tour_activity=activity,
                        )
                    )
        for context in contexts:
            if not registration.constraint.is_feasible(context):
                return None
            total_penalty += registration.constraint.penalty(context)
    return total_penalty


def build_solution(
    routes: tuple[VehicleRoute, ...],
    unassigned_jobs: tuple[Job, ...],
) -> VehicleRoutingProblemSolution:
    total_cost = sum(route.cost for route in routes) + (10000.0 * len(unassigned_jobs))
    return VehicleRoutingProblemSolution(
        routes=tuple(route for route in routes if route.jobs),
        unassigned_jobs=unassigned_jobs,
        cost=total_cost,
    )
