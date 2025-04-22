def parse_csv_sections(path):
    sections = []
    with open(path, 'r') as f:
        # strip blank lines
        lines = [l.strip() for l in f if l.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # 1) If it's a section header
        if line.startswith('#'):
            header = line
            # decide type by checking keyword
            is_dict = 'dictionary' in header.lower()

            # prepare a new section
            section = {
                'header': header,
                'type': 'dict' if is_dict else 'non-dict',
                'lines': []
            }
            i += 1

            # 2) Collect all following lines until the next header
            while i < len(lines) and not lines[i].startswith('#'):
                section['lines'].append(lines[i])
                i += 1

            sections.append(section)
        else:
            # if file starts without a header, skip or handle as you wish
            i += 1

    return sections

def format_sections(sections):
    output = []
    for sec in sections:
        output.append(sec['header'])
        if sec['type'] == 'non-dict':
            # just key:=value per line
            for ln in sec['lines']:
                key, val = ln.split(',', 1)
                output.append(f"{key}:={val}")
        else:
            # dictionary: first line is label, rest are k,v
            label = sec['lines'][0]
            kvs = [ln.split(',',1) for ln in sec['lines'][1:]]
            body = ",".join(f"{k}:{v}" for k, v in kvs)
            output.append(f"{label}:{{{body}}}")
        # blank line between sections
        output.append('')
    return "\n".join(output).strip()

if __name__ == "__main__":
    path_to_csv = 'data.csv'
    secs = parse_csv_sections(path_to_csv)
    result = format_sections(secs)
    print(result)
