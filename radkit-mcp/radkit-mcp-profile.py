"""
RADKit MCP command-filtering profile.

Wraps execute_cli_commands with a prefix-based allow-list.
Readonly server (RADKIT_ACCESS_MODE=show) blocks everything except 'show ...' commands.
Fullaccess server (RADKIT_ACCESS_MODE=full) allows everything.

update_scope() receives a ProfileContext dataclass (not a dict):
    ProfileContext.client          -> radkit_client.sync.Client
    ProfileContext.connect_service -> Callable[[], Service]
"""

import os
from collections.abc import Callable, Sequence
from typing import Any, Protocol

DEFAULT_ACCESS_MODE = "show"
ACCESS_MODE = os.environ.get("RADKIT_ACCESS_MODE", DEFAULT_ACCESS_MODE).strip().lower()

MODE_PREFIXES: dict[str, list[str]] = {
    "full": [],
    "show": ["show", "display", "ping", "traceroute"],
    "conf": ["conf t", "configure"],
    "debug": ["debug"],
}

ALLOWED_PREFIXES = MODE_PREFIXES.get(ACCESS_MODE, [DEFAULT_ACCESS_MODE])


class _ExecuteCliCallable(Protocol):
    """
    Summary:
        Define the callable shape expected from the RADKit CLI executor.

    Args:
        devices: Device selector or collection accepted by RADKit.
        commands: Ordered CLI commands to run.

    Returns:
        Any: The executor result from RADKit (typically execution responses).
    """

    def __call__(self, devices: Any, commands: Sequence[str]) -> Any:
        """
        Summary:
            Run one or more CLI commands against one or more devices.

        Args:
            devices: Device selector or collection accepted by RADKit.
            commands: Ordered CLI commands to run.

        Returns:
            Any: Raw result returned by the underlying RADKit executor.
        """


class ProfileContext(Protocol):
    """
    Summary:
        Describe the minimal context contract required by update_scope.

    Args:
        client: RADKit synchronous client instance.
        connect_service: Function that returns a connected service object.

    Returns:
        None: Protocol declarations are used for static typing only.
    """

    client: Any
    connect_service: Callable[[], Any]


def _is_command_allowed(command: str) -> tuple[bool, str]:
    """
    Summary:
        Check whether a single CLI command is allowed for the active mode.

    Args:
        command: Raw CLI command string to validate.

    Returns:
        tuple[bool, str]:
            - bool: True when the command is allowed.
            - str: Human-readable reason explaining the decision.
    """

    normalized_command = command.strip().lower() if command else ""
    if not normalized_command:
        return False, "Empty command"

    if ACCESS_MODE == "full":
        return True, "Full access mode"

    for prefix in ALLOWED_PREFIXES:
        if normalized_command.startswith(prefix.lower()):
            return True, f"Matches prefix: '{prefix}'"

    return False, f"Blocked. Mode '{ACCESS_MODE}' allows: {', '.join(ALLOWED_PREFIXES)}"


def get_access_mode() -> str:
    """
    Summary:
        Build a readable description of the current command access mode.

    Args:
        None.

    Returns:
        str: Mode label and allowed command prefixes.
    """

    if ACCESS_MODE == "full":
        return "FULL - all commands allowed (read-write)"

    return f"{ACCESS_MODE.upper()} - only: {', '.join(ALLOWED_PREFIXES)}"


class _FilteredExecuteCliCommands:
    """
    Drop-in replacement for _ExecuteCliCommands that validates commands
    against the allow-list before delegating to the real implementation.

    Instantiated with the real _ExecuteCliCommands from radkit_llm internals.
    Signature matches: __call__(devices, commands) -> list[SingleExecResponse[str]]
    """

    def __init__(self, real_execute: _ExecuteCliCallable) -> None:
        """
        Summary:
            Store the real RADKit executor used after command validation.

        Args:
            real_execute: Callable that runs CLI commands through RADKit.

        Returns:
            None: Initializes the wrapper instance.
        """

        self._real_execute = real_execute

    def __call__(self, devices: Any, commands: Sequence[str]) -> Any:
        """
        Summary:
            Validate all commands and execute only when all are allowed.

        Args:
            devices: Device selector or collection accepted by RADKit.
            commands: CLI commands to validate and execute.

        Returns:
            Any: Result returned by the wrapped RADKit executor.
        """

        for cmd in commands:
            allowed, reason = _is_command_allowed(cmd)
            if not allowed:
                raise ValueError(f"BLOCKED: {reason}")

        return self._real_execute(devices, commands)


def update_scope(ctx: ProfileContext) -> dict[str, Any]:
    """
    Summary:
        Build sandbox bindings and replace execute_cli_commands with a filtered wrapper.

    Args:
        ctx: Profile context with client and connect_service attributes.

    Returns:
        dict[str, Any]: Dictionary merged into the sandbox scope.

    Notes:
        The underlying _ExecuteCliCommands instance is wrapped to enforce
        this profile's command policy while keeping RADKit behavior intact.
    """
    _ = ctx

    from radkit_llm.integrations.radkit.in_sandbox import _ExecuteCliCommands

    real_execute = _ExecuteCliCommands()

    return {
        "execute_cli_commands": _FilteredExecuteCliCommands(real_execute),
        "get_access_mode": get_access_mode,
    }
