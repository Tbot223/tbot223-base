# external modules
import sys
import os
import platform
import time
import traceback
import uuid
from collections.abc import Iterable, Mapping
from typing import Callable, Dict, List, Literal, Optional, ParamSpec, Tuple, TypeAlias, TypeGuard, TypeVar, Union, cast
from functools import wraps
import threading

# internal modules
from tbot223_base.tbot223_Result import Result, ResultStatus

MaskPreset: TypeAlias = Literal["default", "private", "user_input", "params", "traceback", "system_info"]
MaskPath: TypeAlias = Union[str, Tuple[str, ...]]
MaskPresetsInput: TypeAlias = Optional[Union[MaskPreset, Iterable[MaskPreset]]]
MaskPathsInput: TypeAlias = Optional[Union[MaskPath, Iterable[MaskPath]]]
ExceptionParams: TypeAlias = Tuple[Tuple[object, ...], Mapping[str, object]]
PublicTags: TypeAlias = Mapping[object, object]
PublicErrorCode: TypeAlias = Union[str, int]
ContextSequence: TypeAlias = Union[List[object], Tuple[object, ...]]
ContextMapping: TypeAlias = Dict[object, object]

P = ParamSpec("P")
R = TypeVar("R")

class ExceptionTrackerHelper():
    """
    Helper functions for `ExceptionTracker` to build structured exception information.
    
    ### Note
    > - Focuses on constructing detailed error information payloads.
    > - Used internally by `ExceptionTracker` for consistent data formatting.
    > - Not intended for direct use by external code.
    """
    ENVIRONMENT_VARIABLE_MAX_VALUE_LENGTH = 200
    ENVIRONMENT_VARIABLE_MAX_COUNT = 50

    @classmethod
    def _copy_small_environment_primitive(cls, value: object) -> Tuple[bool, object]:
        """Return whether a value is a small primitive safe to copy."""
        if value is None or isinstance(value, (bool, int, float)):
            return True, value
        if isinstance(value, str) and len(value) <= cls.ENVIRONMENT_VARIABLE_MAX_VALUE_LENGTH:
            return True, value
        return False, None

    @classmethod
    def _copy_small_environment_value(cls, value: object) -> Tuple[bool, object]:
        """Return whether an environment value is safe to copy."""
        is_small, copied_value = cls._copy_small_environment_primitive(value)
        if is_small:
            return True, copied_value

        if not isinstance(value, (tuple, list)):
            return False, None
        if len(value) > cls.ENVIRONMENT_VARIABLE_MAX_COUNT:
            return False, None

        copied_items: List[object] = []
        for item in value:
            is_small_item, copied_item = cls._copy_small_environment_primitive(item)
            if not is_small_item:
                return False, None
            copied_items.append(copied_item)

        if isinstance(value, tuple):
            return True, tuple(copied_items)
        return True, copied_items

    @classmethod
    def _get_small_environment_variables(cls) -> Dict[str, object]:
        """Return small environment variables without truncating or snapshotting large values."""
        variables: Dict[str, object] = {}
        environment = os.environ

        if not isinstance(environment, Mapping):
            return variables

        for key, value in environment.items():
            if not isinstance(key, str) or len(key) > cls.ENVIRONMENT_VARIABLE_MAX_VALUE_LENGTH:
                continue
            is_small, copied_value = cls._copy_small_environment_value(value)
            if not is_small:
                continue
            variables[key] = copied_value
            if len(variables) >= cls.ENVIRONMENT_VARIABLE_MAX_COUNT:
                break

        return variables

    @classmethod
    def get_system_info(cls) -> dict:
        """
        Return a system information snapshot.

        ### Arguments
        None

        ### Returns
        `dict` — Contains OS, Python, process, thread, path, small environment variables, and timestamp information.

        ### Warning
        > **Security:**
        > - The returned snapshot may include sensitive process context such as `Command_Args`, `Python_Path`, `Hostname`, `Current_Working_Directory`, and small environment variables.
        > - Environment variables are only copied when they are small primitives or shallow tuple/list values with small primitive items, up to `ENVIRONMENT_VARIABLE_MAX_COUNT` entries.
        > - Mask or omit this payload before exposing it to untrusted users or external systems.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTrackerHelper
        >>> helper = ExceptionTrackerHelper()
        >>> info = helper.get_system_info()
        >>> print(info)
        """
        try:
            cwd = os.getcwd()
            if not os.access(cwd, os.R_OK):
                cwd = "<Permission Denied or Unavailable>"
        except Exception:
            cwd = "<Permission Denied or Unavailable>"

        environment_variables = cls._get_small_environment_variables()

        # This method can be expanded to include more dynamic system information if needed.
        return {
            "OS": platform.system(),
            "OS_version": platform.version(),
            "Release": platform.release(),
            "Architecture": platform.machine(),
            "Processor": platform.processor(),
            "Python_Version": platform.python_version(),
            "Python_Executable": sys.executable,
            "Current_Working_Directory": cwd,
            "Hostname": platform.node(),
            "PID": os.getpid(),
            "Thread_Name": threading.current_thread().name,

            "Command_Args": sys.argv,
            "Virtual_Env": (
                environment_variables["VIRTUAL_ENV"]
                if isinstance(environment_variables.get("VIRTUAL_ENV"), str)
                else "None"
            ),
            "Environment_Variables": environment_variables,
            "Python_Path": sys.path,

            "Timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    
    @staticmethod
    def get_error_info_structure():
        """
        Return the base structure for detailed error information.

        ### Arguments
        None

        ### Returns
        `dict` — A template dictionary for structured error information.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTrackerHelper
        >>> helper = ExceptionTrackerHelper()
        >>> error_info = helper.get_error_info_structure()
        >>> print(error_info)
        """
        return {
            "id": None,
            "status": None,
            "success": None,
            "timestamp": None,
            "quick_info": None,

            "error": {
                "type": None,
                "message": None,
            },
            "location": {
                "entry": {
                    "file": None,
                    "line": None,
                    "function": None
                },
                "origin": {
                    "file": None,
                    "line": None,
                    "function": None
                }
            },

            "tags": {},

            "input_context": {
                "user_input": None,
                "params": {
                    "args": None,
                    "kwargs": None
                },
                "local_variables": {}
            },

            "causes": [],

            "traceback": None,
            "traceback_frames": [],

            "system_info": {
                "started_at": None,
                "now": None
            }
        }

    @staticmethod
    def get_public_error_info_structure():
        """
        Return the base structure for lightweight public error information.

        ### Arguments
        None

        ### Returns
        `dict` — A template dictionary safe for public-facing error payloads.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTrackerHelper
        >>> helper = ExceptionTrackerHelper()
        >>> public_error_info = helper.get_public_error_info_structure()
        >>> print(public_error_info)
        """
        return {
            "id": None,
            "status": None,
            "success": None,
            "timestamp": None,
            "error": {
                "code": None,
                "message": None,
            },
            "tags": {},
            "retryable": None
        }


class ExceptionTracker():
    """
    Collect structured exception information and return it in `Result` format.
    
    ### Note
    > - Locates where an exception occurred.
    > - Builds a detailed error information payload.
    > - Standardizes exception returns for callers.
    """

    MASKED_VALUE = "<MASKED>"
    BLOCKED_VALUE = "<BLOCKED>"
    DEFAULT_TRACEBACK_LIMIT = 5
    MAX_TRACEBACK_LIMIT = 10000
    DEFAULT_PUBLIC_ERROR_CODE = "UNEXPECTED_ERROR"
    DEFAULT_PUBLIC_MESSAGE = "The operation could not be completed."
    DEFAULT_MASK_PRESETS: Tuple[MaskPreset, ...] = ("default",)
    CONTEXT_MAX_VALUE_LENGTH = 200
    CONTEXT_MAX_ITEMS = 20
    MASK_PRESETS: Dict[MaskPreset, Tuple[Tuple[str, ...], ...]] = {
        "default": (
            ("input_context", "local_variables"),
        ),
        "private": (
            ("input_context", "user_input"),
            ("input_context", "params"),
            ("input_context", "local_variables"),
        ),
        "user_input": (
            ("input_context", "user_input"),
        ),
        "params": (
            ("input_context", "params"),
            ("input_context", "local_variables"),
        ),
        "traceback": (
            ("causes",),
            ("traceback",),
            ("traceback_frames",),
        ),
        "system_info": (
            ("system_info",),
        ),
    }

    def __init__(self):
        """
        Initialize an `ExceptionTracker` with a startup system snapshot.

        - **(R)** = Required argument
        - **(O)** = Optional argument (has a default value)
        - **(D)** = Dependency Injection (advanced usage)

        ### Arguments
        None

        ### Returns
        `None` — Initializes the tracker and caches startup system information.
        """
        self._system_info = ExceptionTrackerHelper.get_system_info()

    @staticmethod
    def _format_location(location: dict) -> str:
        if not location.get("file"):
            return "<unknown>"
        return f"'{location['file']}', line {location['line']}, in {location['function']}"

    @staticmethod
    def _normalize_public_context(public_context: object) -> Optional[str]:
        """Normalize public context into a safe optional string."""
        if isinstance(public_context, str) and public_context:
            return public_context
        return None

    @classmethod
    def _build_public_error_info(
        cls,
        error_code: Optional[PublicErrorCode]=None,
        public_message: Optional[str]=None,
        tags: Optional[PublicTags]=None,
        retryable: Optional[bool]=None,
    ) -> dict:
        """Build a lightweight public-safe error payload."""
        public_error_info = ExceptionTrackerHelper.get_public_error_info_structure()
        public_error_info["id"] = str(uuid.uuid4())
        public_error_info["status"] = ResultStatus.FAILURE.value
        public_error_info["success"] = False
        public_error_info["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        public_error_info["error"]["code"] = (
            cls.DEFAULT_PUBLIC_ERROR_CODE
            if error_code is None else error_code
        )
        public_error_info["error"]["message"] = (
            public_message
            if isinstance(public_message, str) and public_message
            else cls.DEFAULT_PUBLIC_MESSAGE
        )
        public_error_info["tags"] = (
            {str(key): value for key, value in tags.items()}
            if isinstance(tags, Mapping)
            else {}
        )
        public_error_info["retryable"] = retryable if isinstance(retryable, bool) else None
        return public_error_info

    @classmethod
    def _normalize_limit(cls, limit: int) -> int:
        if not isinstance(limit, int) or limit < 0:
            return cls.DEFAULT_TRACEBACK_LIMIT
        return min(limit, cls.MAX_TRACEBACK_LIMIT)

    @staticmethod
    def _frame_to_location(frame) -> dict:
        if frame is None:
            return {
                "file": None,
                "line": None,
                "function": None
            }
        return {
            "file": frame.filename,
            "line": frame.lineno,
            "function": frame.name
        }

    @classmethod
    def _frame_to_traceback_frame(cls, frame) -> dict:
        frame_info = cls._frame_to_location(frame)
        frame_info["code"] = frame.line if frame is not None else None
        return frame_info

    @staticmethod
    def _get_origin_traceback(error: Exception):
        tb = error.__traceback__
        if tb is None:
            return None
        while tb.tb_next is not None:
            tb = tb.tb_next
        return tb

    @staticmethod
    def _get_local_variables(error: Exception) -> dict:
        origin_tb = ExceptionTracker._get_origin_traceback(error)
        if origin_tb is None:
            return {}
        return dict(origin_tb.tb_frame.f_locals)

    @classmethod
    def _copy_safe_context_primitive(cls, value: object) -> Tuple[bool, object]:
        if value is None or isinstance(value, (bool, int, float)):
            return True, value

        if isinstance(value, str) and len(value) <= cls.CONTEXT_MAX_VALUE_LENGTH:
            return True, value

        return False, cls.BLOCKED_VALUE

    @staticmethod
    def _is_plain_context_sequence(value: object) -> TypeGuard[ContextSequence]:
        return type(value) in (list, tuple)

    @staticmethod
    def _is_plain_context_mapping(value: object) -> TypeGuard[ContextMapping]:
        return type(value) is dict

    @classmethod
    def _copy_safe_context_sequence(cls, value: ContextSequence) -> object:
        if len(value) > cls.CONTEXT_MAX_ITEMS:
            return cls.BLOCKED_VALUE

        copied_items: List[object] = []
        for item in value:
            is_small, copied_item = cls._copy_safe_context_primitive(item)
            if is_small:
                copied_items.append(copied_item)
            elif cls._is_plain_context_sequence(item):
                copied_items.append(cls._copy_safe_context_inner_sequence(item))
            else:
                copied_items.append(cls.BLOCKED_VALUE)

        if isinstance(value, tuple):
            return tuple(copied_items)
        return copied_items

    @classmethod
    def _copy_safe_context_inner_sequence(cls, value: ContextSequence) -> object:
        if len(value) > cls.CONTEXT_MAX_ITEMS:
            return cls.BLOCKED_VALUE

        copied_items: List[object] = []
        for item in value:
            is_small, copied_item = cls._copy_safe_context_primitive(item)
            if not is_small:
                return cls.BLOCKED_VALUE
            copied_items.append(copied_item)

        if isinstance(value, tuple):
            return tuple(copied_items)
        return copied_items

    @classmethod
    def _copy_safe_context_mapping(cls, value: ContextMapping) -> object:
        if len(value) > cls.CONTEXT_MAX_ITEMS:
            return cls.BLOCKED_VALUE

        copied_items: Dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str) or len(key) > cls.CONTEXT_MAX_VALUE_LENGTH:
                continue
            is_small, copied_item = cls._copy_safe_context_primitive(item)
            if is_small:
                copied_items[key] = copied_item
            elif cls._is_plain_context_sequence(item):
                copied_items[key] = cls._copy_safe_context_sequence(item)
            else:
                copied_items[key] = cls.BLOCKED_VALUE
        return copied_items

    @classmethod
    def _copy_safe_context(cls, value: object) -> object:
        is_small, copied_value = cls._copy_safe_context_primitive(value)
        if is_small:
            return copied_value

        if cls._is_plain_context_sequence(value):
            return cls._copy_safe_context_sequence(value)

        if cls._is_plain_context_mapping(value):
            return cls._copy_safe_context_mapping(value)

        return cls.BLOCKED_VALUE

    @staticmethod
    def _normalize_mask_path(path: MaskPath) -> Tuple[str, ...]:
        """Normalize a single mask path into tuple form."""
        if isinstance(path, str):
            return tuple(part for part in path.split(".") if part)
        if isinstance(path, tuple) and all(isinstance(part, str) for part in path):
            return tuple(part for part in path if part)
        return ()

    @staticmethod
    def _is_tuple_path(path: object) -> TypeGuard[Tuple[str, ...]]:
        """Return whether `path` is a tuple path made only of `str` parts."""
        return isinstance(path, tuple) and all(isinstance(part, str) for part in path)

    @staticmethod
    def _dedupe_mask_paths(paths: Tuple[Tuple[str, ...], ...]) -> Tuple[Tuple[str, ...], ...]:
        """Return mask paths with duplicates removed while preserving order."""
        deduped_paths: List[Tuple[str, ...]] = []
        seen_paths = set()

        for path in paths:
            if path in seen_paths:
                continue
            deduped_paths.append(path)
            seen_paths.add(path)

        return tuple(deduped_paths)

    @classmethod
    def _normalize_mask_paths(cls, paths: MaskPathsInput) -> Tuple[Tuple[str, ...], ...]:
        """
        Normalize mask path input into internal tuple-path form.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `paths` | `MaskPathsInput` | Mask path input. Accepts `None`, `str`, `Tuple[str, ...]`, or an iterable of those values. |

        ### Returns
        `Tuple[Tuple[str, ...], ...]` — Contains normalized mask paths.

        ### Note
        > - `str` values are dot paths such as `"location.origin"` or `"id"`.
        > - `Tuple[str, ...]` values are always treated as one path, such as `("location", "origin")`.
        > - Use a list for multiple paths, such as `["id", "quick_info", ("error", "message")]`.
        > - Invalid path entries are ignored.
        """
        if paths is None:
            return ()
        if isinstance(paths, str):
            normalized_path = cls._normalize_mask_path(paths)
            return (normalized_path,) if normalized_path else ()
        if cls._is_tuple_path(paths):
            normalized_path = cls._normalize_mask_path(paths)
            return (normalized_path,) if normalized_path else ()

        normalized_paths: List[Tuple[str, ...]] = []
        path_items = cast(Iterable[MaskPath], paths)
        try:
            path_iterator = iter(path_items)
        except TypeError:
            return ()

        for path in path_iterator:
            normalized_path = cls._normalize_mask_path(path)
            if normalized_path:
                normalized_paths.append(normalized_path)
        return cls._dedupe_mask_paths(tuple(normalized_paths))

    @classmethod
    def _normalize_mask_presets(cls, presets: MaskPresetsInput) -> Tuple[MaskPreset, ...]:
        """
        Normalize mask preset input into known preset names.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `presets` | `MaskPresetsInput` | Preset name or iterable of preset names. Accepts `None`, `str`, or iterable input. |

        ### Returns
        `Tuple[MaskPreset, ...]` — Contains known preset names without duplicates.

        ### Note
        > Unknown preset names and non-string entries are ignored.
        """
        if presets is None:
            return ()
        if isinstance(presets, str):
            presets = (presets,)

        normalized_presets: List[MaskPreset] = []
        seen_presets = set()

        try:
            preset_iterator = iter(presets)
        except TypeError:
            return ()

        for preset in preset_iterator:
            if not isinstance(preset, str):
                continue
            if preset not in cls.MASK_PRESETS or preset in seen_presets:
                continue
            normalized_presets.append(cast(MaskPreset, preset))
            seen_presets.add(preset)

        return tuple(normalized_presets)

    @classmethod
    def _get_preset_mask_paths(cls, presets: MaskPresetsInput) -> Tuple[Tuple[str, ...], ...]:
        """
        Return mask paths selected by named presets.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `presets` | `MaskPresetsInput` | Preset name or iterable of preset names. Accepts `None`, `str`, or iterable input. |

        ### Returns
        `Tuple[Tuple[str, ...], ...]` — Contains deduplicated mask paths for the selected presets.
        """
        mask_paths: List[Tuple[str, ...]] = []

        for preset in cls._normalize_mask_presets(presets):
            mask_paths.extend(cls.MASK_PRESETS[preset])

        return cls._dedupe_mask_paths(tuple(mask_paths))

    @classmethod
    def _mask_path(cls, error_info: dict, path: Tuple[str, ...]) -> None:
        """
        Mask one path in an error information dictionary.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error_info` | `dict` | Structured error information to mutate. |
        | **(R)** | `path` | `Tuple[str, ...]` | Tuple path to mask. |

        ### Returns
        `None` — Mutates `error_info` in place when `path` exists.

        ### Note
        > Missing paths are ignored.
        """
        current = error_info

        for key in path[:-1]:
            if not isinstance(current, dict) or key not in current:
                return
            current = current[key]

        last_key = path[-1]
        if isinstance(current, dict) and last_key in current:
            current[last_key] = cls.MASKED_VALUE

    @classmethod
    def _mask_paths(cls, error_info: dict, paths: Tuple[Tuple[str, ...], ...]) -> None:
        """Mask multiple tuple paths in an error information dictionary."""
        for path in paths:
            cls._mask_path(error_info, path)

    def _get_exception_causes(self, error: Exception, limit: int) -> List[Dict[str, object]]:
        causes: List[Dict[str, object]] = []
        seen = set()
        current_error = error.__cause__ or error.__context__

        while current_error is not None and len(causes) < limit:
            if id(current_error) in seen:
                break
            seen.add(id(current_error))

            tb = traceback.extract_tb(current_error.__traceback__)
            origin_frame = tb[-1] if tb else None
            causes.append({
                "type": type(current_error).__name__,
                "message": str(current_error),
                "location": self._frame_to_location(origin_frame)
            })

            current_error = current_error.__cause__ or current_error.__context__

        return causes

    # L1 Methods
    def get_exception_location(self, error: Exception) -> Result[str]:
        """
        Return the source location for an exception.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error` | `Exception` | The exception object to track. |

        ### Returns
        `Result` — Contains a formatted string: `'{file}', line {line}, in {function}`.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTracker
        >>> tracker = ExceptionTracker()
        >>> try:
        ...     1 / 0
        ... except Exception as e:
        ...     location_result = tracker.get_exception_location(e)
        >>> print(location_result.data)
        """
        try:
            tb = traceback.extract_tb(error.__traceback__)
            origin_frame = tb[-1] if tb else None
            origin_location = self._frame_to_location(origin_frame)
            return Result(ResultStatus.SUCCESS, None, None, self._format_location(origin_location))
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(ResultStatus.FAILURE, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_location, L1", tb_str)

    def get_exception_info(
        self,
        error: Exception,
        user_input: object=None,
        params: ExceptionParams=((), {}),
        mask_presets: MaskPresetsInput=DEFAULT_MASK_PRESETS,
        mask_paths: MaskPathsInput=(),
        traceback_frame_limit: int=DEFAULT_TRACEBACK_LIMIT,
        cause_limit: int=DEFAULT_TRACEBACK_LIMIT
    ) -> Result[object]:
        """
        Build detailed internal exception information.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error` | `Exception` | The exception object to describe. |
        | **(O)** | `user_input` | `object` | User input context. Small safe values are copied; heavy values are blocked. Default: `None`. |
        | **(O)** | `params` | `ExceptionParams` | Additional call context `(args, kwargs)`. Small safe values are copied; heavy values are blocked. Default: `((), {})`. |
        | **(O)** | `mask_presets` | `MaskPresetsInput` | Named mask presets. Default: `("default",)`. |
        | **(O)** | `mask_paths` | `MaskPathsInput` | Extra paths to mask, such as `"id"`, `"location.origin"`, or `("error", "message")`. |
        | **(O)** | `traceback_frame_limit` | `int` | Max traceback frame entries. Default: `5`, max: `10000`. |
        | **(O)** | `cause_limit` | `int` | Max chained cause entries. Default: `5`, max: `10000`. |

        ### Enum
        > `mask_presets` — type: `str`
        > | Value | Description |
        > |-------|-------------|
        > | `'default'` | Masks `input_context.local_variables`. |
        > | `'private'` | Masks `input_context.user_input`, `input_context.params`, and `input_context.local_variables`. |
        > | `'user_input'` | Masks `input_context.user_input`. |
        > | `'params'` | Masks `input_context.params` and `input_context.local_variables`. |
        > | `'traceback'` | Masks `causes`, `traceback`, and `traceback_frames`. |
        > | `'system_info'` | Masks `system_info`. |

        ### Returns
        `Result` — Contains the structured error information in `data`.

        ### Warning
        > **Security:**
        > - `user_input`, `params`, and `local_variables` never store raw object references.
        > - Heavy or unsupported context values are replaced with `"<BLOCKED>"` rather than summarized with metadata.
        > - Small copied context values, `traceback`, and `system_info` may still contain sensitive data.
        > - Use `mask_presets=("private", "traceback", "system_info")` or explicit `mask_paths` before exposing error information outside a trusted boundary.

        ### Note
        > - This is the debug-heavy path for internal diagnostics.
        > - For safe external payloads, use `get_public_exception_info()` instead.
        > - Context capture preserves small primitives and primitive-only `list`/`tuple` values; `dict` values are copied only at the top level.
        > - `mask_paths` accepts a single dot path such as `"location.origin"`.
        > - `mask_paths` accepts a single tuple path such as `("location", "origin")`.
        > - Use a list for multiple paths, such as `["id", "quick_info", ("error", "message")]`.
        > - A tuple of strings is always treated as one path.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTracker
        >>> tracker = ExceptionTracker()
        >>> try:
        >>>     1 / 0
        >>> except Exception as e:
        >>>     result = tracker.get_exception_info(
        >>>         e,
        >>>         mask_presets=("private", "traceback"),
        >>>         mask_paths=["id", ("error", "message")]
        >>>     )
        >>>     print(result.status)
        """
        try:
            preset_mask_paths = self._get_preset_mask_paths(mask_presets)
            extra_mask_paths = self._normalize_mask_paths(mask_paths)
            traceback_frame_limit = self._normalize_limit(traceback_frame_limit)
            cause_limit = self._normalize_limit(cause_limit)
            tb = traceback.extract_tb(error.__traceback__)
            entry_frame = tb[0] if tb else None
            origin_frame = tb[-1] if tb else None
            origin_location = self._frame_to_location(origin_frame)
            limited_frames = tb[-traceback_frame_limit:] if traceback_frame_limit else []

            if isinstance(params, tuple) and len(params) == 2:
                args, kwargs = params
            else:
                args, kwargs = (), {}

            error_info = ExceptionTrackerHelper.get_error_info_structure()
            error_info["id"] = str(uuid.uuid4())
            error_info["status"] = ResultStatus.FAILURE.value
            error_info["success"] = False
            error_info["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            error_info["quick_info"] = f"{type(error).__name__}: {str(error)}"
            error_info["error"]["type"] = type(error).__name__
            error_info["error"]["message"] = str(error)
            error_info["location"]["entry"] = self._frame_to_location(entry_frame)
            error_info["location"]["origin"] = origin_location
            error_info["input_context"]["user_input"] = self._copy_safe_context(user_input)
            error_info["input_context"]["params"]["args"] = self._copy_safe_context(args)
            error_info["input_context"]["params"]["kwargs"] = self._copy_safe_context(kwargs)
            error_info["input_context"]["local_variables"] = self._copy_safe_context(self._get_local_variables(error))
            error_info["causes"] = self._get_exception_causes(error, cause_limit)
            error_info["traceback"] = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            error_info["traceback_frames"] = [
                self._frame_to_traceback_frame(frame)
                for frame in limited_frames
            ]
            error_info["system_info"]["started_at"] = self._system_info
            error_info["system_info"]["now"] = ExceptionTrackerHelper.get_system_info()

            self._mask_paths(error_info, preset_mask_paths)
            self._mask_paths(error_info, extra_mask_paths)

            return Result(ResultStatus.FAILURE, error_info["quick_info"], self._format_location(origin_location), error_info)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(ResultStatus.FAILURE, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_info, L1", tb_str)

    def get_public_exception_info(
        self,
        error: Exception,
        error_code: Optional[PublicErrorCode]=None,
        public_message: Optional[str]=None,
        public_context: Optional[str]=None,
        tags: Optional[PublicTags]=None,
        retryable: Optional[bool]=None
    ) -> Result[Dict[str, object]]:
        """
        Build lightweight public exception information safe to expose externally.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error` | `Exception` | The exception object that triggered the failure. |
        | **(O)** | `error_code` | `Optional[PublicErrorCode]` | Public-facing error code. Default: `"UNEXPECTED_ERROR"`. |
        | **(O)** | `public_message` | `Optional[str]` | Public-facing error message. Default: generic safe message. |
        | **(O)** | `public_context` | `Optional[str]` | Public-facing context string for the returned `Result`. Default: `None`. |
        | **(O)** | `tags` | `Optional[PublicTags]` | Public metadata tags to attach to the payload. Default: `None`. |
        | **(O)** | `retryable` | `Optional[bool]` | Whether the caller may retry the operation. Default: `None`. |

        ### Returns
        `Result` — Contains lightweight public error information in `data`.

        ### Note
        > - This path avoids collecting traceback text, local variables, params, and system information.
        > - The payload is designed for API responses, UI surfaces, or other untrusted boundaries.
        > - `error` is accepted for API symmetry, but its raw message is not exposed unless you pass a safe `public_message`.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTracker
        >>> tracker = ExceptionTracker()
        >>> try:
        >>>     1 / 0
        >>> except Exception as e:
        >>>     result = tracker.get_public_exception_info(
        >>>         e,
        >>>         error_code="DIVIDE_BY_ZERO",
        >>>         public_message="The calculation could not be completed.",
        >>>         tags={"layer": "service"},
        >>>         retryable=False
        >>>     )
        >>>     print(result.data["error"]["code"])
        """
        try:
            normalized_context = self._normalize_public_context(public_context)
            public_error_info = self._build_public_error_info(
                error_code=error_code,
                public_message=public_message,
                tags=tags,
                retryable=retryable,
            )
            return Result(ResultStatus.FAILURE, public_error_info["error"]["message"], normalized_context, public_error_info)
        except Exception:
            print("An error occurred while building public exception information. Falling back to a safe generic payload.")
            normalized_context = self._normalize_public_context(public_context)
            fallback_error_info = self._build_public_error_info(tags={"tracker_failure": True})
            return Result(ResultStatus.FAILURE, fallback_error_info["error"]["message"], normalized_context, fallback_error_info)

    # L2 Methods
    def get_exception_return(
        self,
        error: Exception,
        user_input: object=None,
        params: ExceptionParams=((), {}),
        mask_presets: MaskPresetsInput=DEFAULT_MASK_PRESETS,
        mask_paths: MaskPathsInput=()
    ) -> Result[object]:
        """
        Build a standardized debug-heavy failure `Result` from an exception.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error` | `Exception` | The exception object to track. |
        | **(O)** | `user_input` | `object` | User input context. Small safe values are copied; heavy values are blocked. Default: `None`. |
        | **(O)** | `params` | `ExceptionParams` | Additional call context `(args, kwargs)`. Small safe values are copied; heavy values are blocked. Default: `((), {})`. |
        | **(O)** | `mask_presets` | `MaskPresetsInput` | Named mask presets. Default: `("default",)`. |
        | **(O)** | `mask_paths` | `MaskPathsInput` | Extra paths to mask, such as `"id"`, `"location.origin"`, or `("error", "message")`. |

        ### Enum
        > `mask_presets` — type: `str`
        > | Value | Description |
        > |-------|-------------|
        > | `'default'` | Masks `input_context.local_variables`. |
        > | `'private'` | Masks `input_context.user_input`, `input_context.params`, and `input_context.local_variables`. |
        > | `'user_input'` | Masks `input_context.user_input`. |
        > | `'params'` | Masks `input_context.params` and `input_context.local_variables`. |
        > | `'traceback'` | Masks `causes`, `traceback`, and `traceback_frames`. |
        > | `'system_info'` | Masks `system_info`. |

        ### Returns
        `Result` — Contains a failure result with exception details.

        ### Warning
        > **Security:**
        > - The returned error information copies only small safe context values but may still contain sensitive data unless suitable `mask_presets` or `mask_paths` are used.

        ### Note
        > - This method keeps the existing debug-oriented payload behavior.
        > - For public-safe failure results, use `get_public_exception_return()` instead.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTracker
        >>> tracker = ExceptionTracker()
        >>> try:
        ...     1 / 0
        ... except Exception as e:
        ...     res = tracker.get_exception_return(e, user_input="Divide", params=((), {}), mask_presets=("private",))
        """
        try:
            return Result(ResultStatus.FAILURE, f"{type(error).__name__} :{str(error)}", self.get_exception_location(error).data, self.get_exception_info(error, user_input, params, mask_presets=mask_presets, mask_paths=mask_paths).data)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(ResultStatus.FAILURE, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_return, L2", tb_str)

    def get_public_exception_return(
        self,
        error: Exception,
        error_code: Optional[PublicErrorCode]=None,
        public_message: Optional[str]=None,
        public_context: Optional[str]=None,
        tags: Optional[PublicTags]=None,
        retryable: Optional[bool]=None
    ) -> Result[Dict[str, object]]:
        """
        Build a standardized public-safe failure `Result` from an exception.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error` | `Exception` | The exception object that triggered the failure. |
        | **(O)** | `error_code` | `Optional[PublicErrorCode]` | Public-facing error code. Default: `"UNEXPECTED_ERROR"`. |
        | **(O)** | `public_message` | `Optional[str]` | Public-facing error message. Default: generic safe message. |
        | **(O)** | `public_context` | `Optional[str]` | Public-facing context string for the returned `Result`. Default: `None`. |
        | **(O)** | `tags` | `Optional[PublicTags]` | Public metadata tags to attach to the payload. Default: `None`. |
        | **(O)** | `retryable` | `Optional[bool]` | Whether the caller may retry the operation. Default: `None`. |

        ### Returns
        `Result` — Contains a lightweight public-safe failure result.

        ### Note
        > - This method is a public-safe counterpart to `get_exception_return()`.
        > - It does not collect traceback text, local variables, params, or system information.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTracker
        >>> tracker = ExceptionTracker()
        >>> try:
        ...     1 / 0
        ... except Exception as e:
        ...     res = tracker.get_public_exception_return(
        ...         e,
        ...         error_code="DIVIDE_BY_ZERO",
        ...         public_message="The calculation could not be completed."
        ...     )
        """
        return self.get_public_exception_info(
            error=error,
            error_code=error_code,
            public_message=public_message,
            public_context=public_context,
            tags=tags,
            retryable=retryable,
        )

    def get_error_code(self, error_id_map: Mapping[str, object], error: Exception) -> Result[object]:
        """
        Return a user-defined error code for a given exception type.

        ### Arguments
        | Tag | Name | Type | Description |
        |-----|------|------|-------------|
        | **(R)** | `error_id_map` | `Mapping[str, object]` | A mapping from exception type names to project-defined error codes. |
        | **(R)** | `error` | `Exception` | The exception object to get the error code for. |

        ### Constraint
        > - `type(error).__name__` MUST satisfy `in error_id_map`.

        ### Returns
        `Result` — Contains the mapped error code in `data`.

        ### Note
        > `error_id_map` allows each project to define its own exception codes.
        > Example: `{ "ZeroDivisionError": 1001, "ValueError": 1002 }`.

        ### Example
        >>> from tbot223_base.tbot223_Exception import ExceptionTracker
        >>> tracker = ExceptionTracker()
        >>> error_id_map = {"ZeroDivisionError": 1001, "ValueError": 1002}
        >>> try:
        ...     1 / 0
        ... except Exception as e:
        ...     code_result = tracker.get_error_code(error_id_map, e)
        >>> print(code_result.data)
        """
        try:
            if type(error).__name__ not in error_id_map:
                raise KeyError(f"Error type '{type(error).__name__}' not found in error_id_map.")
            else:
                return Result(ResultStatus.SUCCESS, None, None, error_id_map[type(error).__name__])
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(ResultStatus.FAILURE, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_error_code, L2", tb_str)

class ExceptionTrackerDecorator():
    """
    Decorator that wraps a function with `ExceptionTracker`.

    ### Arguments
    | Tag | Name | Type | Description |
    |-----|------|------|-------------|
    | **(O)** | `mask_presets` | `MaskPresetsInput` | Named mask presets. Default: `("default",)`. |
    | **(O)** | `mask_paths` | `MaskPathsInput` | Extra paths to mask, such as `"id"`, `"location.origin"`, or `("error", "message")`. |
    | **(O)** | `tracker` | `Optional[ExceptionTracker]` | Reused tracker. Default: `None`; creates a new `ExceptionTracker` when omitted. |

    ### Enum
    > `mask_presets` — type: `str`
    > | Value | Description |
    > |-------|-------------|
    > | `'default'` | Masks `input_context.local_variables`. |
    > | `'private'` | Masks `input_context.user_input`, `input_context.params`, and `input_context.local_variables`. |
    > | `'user_input'` | Masks `input_context.user_input`. |
    > | `'params'` | Masks `input_context.params` and `input_context.local_variables`. |
    > | `'traceback'` | Masks `causes`, `traceback`, and `traceback_frames`. |
    > | `'system_info'` | Masks `system_info`. |

    ### Returns
    `Callable[P, Union[R, Result[object]]]` — Wrapped function returning the original result or a failure `Result` on error.

    ### Note
    > - Converts uncaught exceptions into standardized `Result` objects.
    > - Best suited for non-critical convenience wrappers.
    > - Not ideal when the caller depends on side effects.
    > - `mask_presets` supports `default`, `private`, `user_input`, `params`, `traceback`, and `system_info`.
    > - Use a list for multiple `mask_paths` entries. A tuple of strings is treated as one path.

    ### Warning
    > **Security:**
    > - Wrapped function arguments are captured in `input_context.params` when an exception occurs.
    > - Use `mask_presets=("private", "traceback", "system_info")` or explicit `mask_paths` before exposing decorator results outside a trusted boundary.

    ### Example
    >>> from tbot223_base.tbot223_Exception import ExceptionTracker, ExceptionTrackerDecorator
    >>> tracker = ExceptionTracker()
    >>> def risky_function(x, y):
    ...     return x / y
    >>> risky_function = ExceptionTrackerDecorator(mask_presets=("private", "traceback"), mask_paths=["id"], tracker=tracker)(risky_function)
    >>> result = risky_function(10, y=0)
    >>> print(result.status)
    """
    def __init__(self, mask_presets: MaskPresetsInput=ExceptionTracker.DEFAULT_MASK_PRESETS, mask_paths: MaskPathsInput=(), tracker: Optional[ExceptionTracker]=None):
        self.tracker = tracker or ExceptionTracker()
        self.mask_presets = ExceptionTracker._normalize_mask_presets(mask_presets)
        self.mask_paths = ExceptionTracker._normalize_mask_paths(mask_paths)

    def __call__(self, func: Callable[P, R]) -> Callable[P, Union[R, Result[object]]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Union[R, Result[object]]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Use the tracker to get standardized exception return
                return self.tracker.get_exception_return(
                    error=e,
                    params=(cast(Tuple[object, ...], args), cast(Mapping[str, object], kwargs)),
                    mask_presets=self.mask_presets,
                    mask_paths=self.mask_paths
                )
        return wrapper
