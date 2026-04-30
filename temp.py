import requests

def decode_message(url):
    response = requests.get(url)
    lines = response.text.splitlines()

    grid = {}
    max_x, max_y = 0, 0

    i = 0
    while i < len(lines):
        try:
            x = int(lines[i].strip())
            char = lines[i + 1].strip()
            y = int(lines[i + 2].strip())

            grid[(x, y)] = char
            max_x = max(max_x, x)
            max_y = max(max_y, y)

            i += 3
        except:
            i += 1  # skip invalid lines

    # print grid
    for y in range(max_y + 1):
        for x in range(max_x + 1):
            print(grid.get((x, y), " "), end="")
        print()



decode_message("https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub")