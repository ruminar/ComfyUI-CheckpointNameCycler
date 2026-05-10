import hashlib
import random
import re
import threading

from aiohttp import web

import folder_paths
from server import PromptServer


_STATES = {}
_STATE_LOCK = threading.Lock()


def _get_checkpoints():
    """
    Use ComfyUI's native checkpoint list order.

    Important:
      CheckpointLoaderSimple validates combo/list types against this list.
      If this node sorts the list independently, the list type can differ from
      CheckpointLoaderSimple on first run after loading a workflow, causing:
        Return type mismatch between linked nodes
    """
    try:
        return list(folder_paths.get_filename_list("checkpoints"))
    except Exception:
        return []


def _checkpoint_type():
    checkpoints = _get_checkpoints()
    return checkpoints if checkpoints else [""]


def _checkpoint_hash(checkpoints):
    joined = "\n".join(str(item) for item in checkpoints)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()


def _clamp_index(index, count):
    if count <= 0:
        return 0
    return max(0, min(int(index), count - 1))


def _index_of_checkpoint(checkpoints, checkpoint_name):
    if not checkpoints:
        return 0
    try:
        return checkpoints.index(checkpoint_name)
    except ValueError:
        return 0


def _make_shuffle_order(count, first_index=None, previous_index=None):
    if count <= 0:
        return []

    indices = list(range(count))

    if first_index is not None:
        first_index = _clamp_index(first_index, count)
        rest = [index for index in indices if index != first_index]
        random.shuffle(rest)
        return [first_index] + rest

    random.shuffle(indices)

    # Avoid repeating the last item of the previous cycle as the first item
    # of the next cycle when possible.
    if count > 1 and previous_index is not None and indices and indices[0] == previous_index:
        swap_index = random.randrange(1, count)
        indices[0], indices[swap_index] = indices[swap_index], indices[0]

    return indices


def _safe_checkpoint_name(name):
    value = str(name).replace("\\", "/")
    value = value.replace("/", "_")

    for ext in [".safetensors", ".ckpt", ".pt", ".pth", ".bin"]:
        if value.lower().endswith(ext):
            value = value[:-len(ext)]
            break

    # Windows filename unsafe characters plus control characters.
    value = re.sub(r'[<>:"|?*\x00-\x1f]', "_", value)
    value = value.strip().strip(".")
    return value or "checkpoint"


def _new_state(checkpoints, start_checkpoint, mode, change_every):
    count = len(checkpoints)
    start_index = _index_of_checkpoint(checkpoints, start_checkpoint)

    state = {
        "start_checkpoint": start_checkpoint,
        "start_index": start_index,
        "mode": mode,
        "change_every": max(1, int(change_every)),
        "repeat_count": 0,
        "current_index": start_index,
        "shuffle_order": [],
        "shuffle_position": 0,
        "cycle_count": 0,
        "checkpoint_hash": _checkpoint_hash(checkpoints),
    }

    if count > 0 and mode == "shuffle_once":
        # First run starts with the selected start_checkpoint.
        state["shuffle_order"] = _make_shuffle_order(count, first_index=start_index)
        state["shuffle_position"] = 0
        state["current_index"] = state["shuffle_order"][0]

    return state


def _state_needs_reset(state, checkpoints, start_checkpoint, mode, change_every):
    if state is None:
        return True

    if state.get("checkpoint_hash") != _checkpoint_hash(checkpoints):
        return True

    if state.get("start_checkpoint") != start_checkpoint:
        return True

    if state.get("mode") != mode:
        return True

    if state.get("change_every") != max(1, int(change_every)):
        return True

    return False


def _select_index(state, checkpoints, mode):
    count = len(checkpoints)
    if count <= 0:
        return 0

    if mode == "shuffle_once":
        order = state.get("shuffle_order") or list(range(count))
        position = state.get("shuffle_position", 0)

        if position >= len(order):
            position = 0
            state["shuffle_position"] = 0

        index = order[position]
        return _clamp_index(index, count)

    return _clamp_index(state.get("current_index", 0), count)


def _advance_state(state, checkpoints, mode):
    count = len(checkpoints)
    if count <= 0:
        return

    state["repeat_count"] = int(state.get("repeat_count", 0)) + 1

    if state["repeat_count"] < state["change_every"]:
        return

    state["repeat_count"] = 0

    if mode == "fixed":
        return

    if mode == "increment":
        current = _clamp_index(state.get("current_index", 0), count)
        next_index = current + 1
        if next_index >= count:
            next_index = 0
            state["cycle_count"] = int(state.get("cycle_count", 0)) + 1
        state["current_index"] = next_index
        return

    if mode == "randomize":
        state["current_index"] = random.randrange(count)
        return

    if mode == "shuffle_once":
        current_index = _select_index(state, checkpoints, mode)
        position = int(state.get("shuffle_position", 0)) + 1

        if position >= count:
            state["cycle_count"] = int(state.get("cycle_count", 0)) + 1
            # After the first cycle, every loop gets a fresh random order.
            state["shuffle_order"] = _make_shuffle_order(count, previous_index=current_index)
            state["shuffle_position"] = 0
        else:
            state["shuffle_position"] = position

        state["current_index"] = _select_index(state, checkpoints, mode)
        return


routes = PromptServer.instance.routes


@routes.post("/checkpoint_name_cycler/reset")
async def checkpoint_name_cycler_reset(_request):
    with _STATE_LOCK:
        count = len(_STATES)
        _STATES.clear()

    return web.json_response({
        "ok": True,
        "reset_count": count,
    })


class CheckpointNameCycler:
    @classmethod
    def INPUT_TYPES(cls):
        checkpoints = _checkpoint_type()

        return {
            "required": {
                "start_checkpoint": (checkpoints,),
                "mode": (["fixed", "increment", "randomize", "shuffle_once"], {"default": "increment"}),
                "change_every": ("INT", {"default": 1, "min": 1, "max": 999999}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = (_checkpoint_type(), "STRING", "STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("ckpt_name", "ckpt_name_str", "ckpt_name_safe", "index", "count", "cycle")
    FUNCTION = "cycle"
    CATEGORY = "utils/model"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # This node is stateful and must run every queued execution.
        return float("NaN")

    def cycle(self, start_checkpoint, mode, change_every, unique_id=None):
        checkpoints = _get_checkpoints()
        count = len(checkpoints)
        node_key = str(unique_id) if unique_id is not None else "__default__"

        with _STATE_LOCK:
            state = _STATES.get(node_key)

            if _state_needs_reset(state, checkpoints, start_checkpoint, mode, change_every):
                state = _new_state(checkpoints, start_checkpoint, mode, change_every)
                _STATES[node_key] = state

            if count <= 0:
                return ("", "", "checkpoint", 0, 0, int(state.get("cycle_count", 0)))

            index = _select_index(state, checkpoints, mode)
            ckpt_name = checkpoints[index]
            ckpt_name_str = str(ckpt_name)
            ckpt_name_safe = _safe_checkpoint_name(ckpt_name_str)
            cycle = int(state.get("cycle_count", 0))

            # Advance after deciding this execution's output.
            _advance_state(state, checkpoints, mode)

            return (ckpt_name, ckpt_name_str, ckpt_name_safe, int(index), int(count), cycle)


NODE_CLASS_MAPPINGS = {
    "CheckpointNameCycler": CheckpointNameCycler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CheckpointNameCycler": "Checkpoint Name Cycler",
}
