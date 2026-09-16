import csv
import io

FORMATS = {"csv": {"delimiter": ",", "lineterminator": "\n"}}

def export(rows, format="csv"):
    out = io.StringIO(newline="")
    csv.writer(out, **FORMATS[format]).writerows(rows)
    return out.getvalue()
