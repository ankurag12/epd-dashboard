def pnm_read_header(pnm_file):
    """
    :param pnm_file: This should be a file object so that after reading the header,
     file pointer is at the beginning of image data
    :return:
    """
    hdr = {
        "type": "UNKNOWN",
        "width": None,
        "height": None,
        "max_gray": 1
    }
    tokens = list()
    while len(tokens) < 3:
        line = pnm_file.readline().decode().strip().split("#")
        if not line:
            continue
        tokens += line.split()

    if tokens[0] == "P4":
        hdr["type"] = "PNM_BITMAP"
    elif tokens[0] == "P5":
        hdr["type"] = "PNM_GREYSCALE"
    else:
        raise ValueError(f"Unable to read header in file {pnm_file}")

    hdr["width"] = int(tokens[1])
    hdr["height"] = int(tokens[2])

    if hdr["type"] == "PNM_GREYSCALE":
        try:
            hdr["max_gray"] = int(tokens[3])
        except IndexError:
            max_gray = pnm_file.readline().decode().strip().split("#")
            while not max_gray:
                max_gray = pnm_file.readline().decode().strip().split("#")
            hdr["max_gray"] = max_gray

    return hdr
