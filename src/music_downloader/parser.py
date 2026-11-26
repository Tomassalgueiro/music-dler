# this file opens a txt and parses everylink to send later into the 
def parse_links(lines: list[str]) -> list[str]: 

    links = []

    for line in lines:
        clean = line.strip()
        clean.split("#")[0].strip()

        # if line is empty or starts with # ignore it
        if len(clean) == 0 or clean[0] == "#":
            continue

        links.append(clean)

    return links
