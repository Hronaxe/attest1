def format_stat(count, total, view):
    percent = count / total * 100 if total else 0
    if view == "abs":
        return f"{count}"
    if view == "rel":
        return f"{percent:.1f}%"
    return f"{count} ({percent:.1f}%)"


def format_endings_stats(counts, endings, view):
    full = {ending: 0 for ending in endings}
    full.update(counts)
    total = sum(full.values())
    ordered = sorted(full.items(), key=lambda item: (-item[1], item[0]))
    return [f"{name}: {format_stat(count, total, view)}" for name, count in ordered]
