import json


def new_game():
    return {"items": {}, "bench": [], "load": 0, "capacity": 2, "stock": 100, "metric": 100, "day": 1, "id": 0, "fault": False, "resource": 10, "rate": 2, "clock": 0, "paused": False, "settled": False}


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    defaults = new_game()
    for key, value in defaults.items():
        state.setdefault(key, value)
    state["items"] = {int(item_id): amount for item_id, amount in state["items"].items()}
    state["bench"] = [int(item_id) for item_id in state["bench"]]
    state["load"] = len(state["bench"])
    return state


def add(state, item_id, amount):
    if state.get("settled"):
        return False
    if item_id in state["items"]:
        return False
    if amount <= 0 or amount > state["stock"]:
        return False
    state["items"][item_id] = amount
    state["stock"] -= amount
    state["id"] = max(state["id"], item_id)
    return True


def receive(state, item_id):
    if state.get("settled"):
        return False
    if item_id not in state["items"]:
        return False
    if item_id in state["bench"]:
        return True
    if state["load"] >= state["capacity"]:
        return False
    state["bench"].append(item_id)
    state["load"] = len(state["bench"])
    return True


def fee(state, item_id, end_day):
    if end_day < state["day"]:
        return 0
    return (end_day - state["day"]) * state["rate"]


def cancel(state, item_id):
    if state.get("settled"):
        return False
    if item_id not in state["items"]:
        return False
    if item_id in state["bench"]:
        state["bench"].remove(item_id)
        state["load"] = len(state["bench"])
    state["stock"] += state["items"].pop(item_id)
    return True


def produce(state, amount):
    if state.get("settled") or state.get("fault"):
        return False
    if amount <= 0:
        return False
    if amount > state["stock"] or amount > state["resource"]:
        return False
    state["stock"] -= amount
    state["resource"] -= amount
    return True


def event(state):
    if state.get("settled"):
        return state["metric"]
    state["metric"] = max(0, state["metric"] - 10)
    return state["metric"]


def guard(state, item_id):
    if state.get("settled"):
        return False
    return item_id in state["items"] and state["resource"] > 0 and state["stock"] > 0


def tick(state):
    if state.get("paused") or state.get("settled"):
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def settle(state):
    if state.get("settled"):
        return False
    state["settled"] = True
    return True


def main():
    print("命令: add/receive/fee/cancel/produce/event/guard/tick/settle/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        try:
            nums = [int(a) for a in args]
            if cmd == "add":
                print("ok" if add(state, nums[0], nums[1]) else "fail")
            elif cmd == "receive":
                print("ok" if receive(state, nums[0]) else "fail")
            elif cmd == "fee":
                print(fee(state, nums[0], nums[1]))
            elif cmd == "cancel":
                print("ok" if cancel(state, nums[0]) else "fail")
            elif cmd == "produce":
                print("ok" if produce(state, nums[0]) else "fail")
            elif cmd == "event":
                print(event(state))
            elif cmd == "guard":
                print("ok" if guard(state, nums[0]) else "fail")
            elif cmd == "tick":
                print(tick(state))
            elif cmd == "settle":
                print("ok" if settle(state) else "fail")
            else:
                print("未知命令")
        except (IndexError, ValueError):
            print("参数错误")


if __name__ == "__main__":
    main()
