import requests
import re

def get_types(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower().replace('_', '-')}"
    response = requests.get(url)
    if response.status_code != 200:
        return "Null", "Null"
    data = response.json()
    types = [t["type"]["name"].capitalize() for t in data["types"]]
    return types[0], types[1] if len(types) > 1 else None

def parse_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    sections = {}
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^[A-Za-z]', stripped):
            current_section = stripped
            sections[current_section] = []
        else:
            sections[current_section].append(stripped.split(','))

    return sections

def generate_entry(name, location_type, rate, min_lv, max_lv, type1, type2):
    level_range = f"{min_lv}-{max_lv}"
    if name.upper() in ["SKITTY", "DELCATTY"]:
        if type2 == "Null" or not type2:
            type2 = "Fairy"
    type_str = f"|type1={type1}"
    if type2 and type2 != "Null":
        type_str += f"|type2={type2}"
    display_name = name.capitalize()
    return f"{{{{Catch/entry|{display_name}|{display_name}|{location_type}|{level_range}|all={rate}%{type_str}}}}}"

def convert_to_wiki(sections):
    output = ["{{Encounters/Header}}", "{{Catch/div}}"]
    rod_section_started = False
    rod_map = {
        "OldRod": "Fish Old",
        "GoodRod": "Fish Good",
        "SuperRod": "Fish Super"
    }

    for section, entries in sections.items():
        if section in rod_map and not rod_section_started:
            output.append("{{Catch/div|Fishing|fishing}}")
            rod_section_started = True

        location_type = "Grass" if section == "Land" else rod_map.get(section, "Grass")

        for entry in entries:
            try:
                rate, name, min_lv, max_lv = entry
                type1, type2 = get_types(name)
                output.append(generate_entry(name, location_type, rate, min_lv, max_lv, type1, type2))
            except Exception as e:
                print(f"Erro ao processar {entry}: {e}")
                continue

    output.append("{{Catch/footer|LocationNameHere}}")
    return '\n'.join(output)

if __name__ == "__main__":
    data = parse_file("base.txt")
    wiki_table = convert_to_wiki(data)

    with open("GeneratedTable.txt", "w", encoding="utf-8") as f:
        f.write(wiki_table)

