import importlib

q = int(input().strip())
cache = {}

for _ in range(q):
    module_path, attr_name = input().split()

    # импорт с кэшем
    if module_path in cache:
        mod = cache[module_path]
    else:
        try:
            mod = importlib.import_module(module_path)
        except ModuleNotFoundError:
            cache[module_path] = None
            print("MODULE_NOT_FOUND")
            continue
        cache[module_path] = mod

    if mod is None:
        print("MODULE_NOT_FOUND")
        continue

    if not hasattr(mod, attr_name):
        print("ATTRIBUTE_NOT_FOUND")
        continue

    attr = getattr(mod, attr_name)
    print("CALLABLE" if callable(attr) else "VALUE")