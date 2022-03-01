import tabulate as tb

def get_lx_table(caption, data, headers, precision = ".2f"):
    tbl = []
    tbl.append("\\begin{table}[H]")
    tbl.append("\\centering")    
    tbl.append(tb.tabulate(data, headers=headers, floatfmt= precision, tablefmt="latex_booktabs"))
    tbl.append("\\caption{{ {:s} }}".format(caption))
    tbl.append("\\vspace{10pt}")
    tbl.append("\\end{table}")
    tbl.append("")
    return "\n".join(tbl)

def save_lx_table(filename, caption, data, headers, precision = ".2f"):
    with open(filename, "w") as f:
        f.write(get_lx_table(caption, data, headers, precision))


