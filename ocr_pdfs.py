import pymupdf
import subprocess
import os
import sqlite_utils

import concurrent.futures


def main():

    database = "city_minutes.db"

    db = sqlite_utils.Database(database)
    if not db["pages"].exists():
        db["pages"].create(
            {"body": str, "date": str, "page": int, "text": str},
            pk=("body", "date", "page"),
        )
        db["pages"].enable_fts(["text"], create_triggers=True)

    directories = [
        directory
        for directory in sorted(os.listdir("./data"))
        if directory != ".DS_Store"
    ]

    jobs = []
    for directory in directories:
        if not os.path.exists(f"./out/{directory}"):
            os.makedirs(f"./out/{directory}")
        for minutes in os.listdir(f"./data/{directory}"):
            if not minutes.endswith(".pdf"):
                continue
            out_dir = minutes.replace(".pdf", "")
            if not os.path.exists(f"./out/{directory}/{out_dir}"):
                os.makedirs(f"./out/{directory}/{out_dir}")
            jobs.append((directory, out_dir))

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_job = {executor.submit(do_job, job): job for job in jobs}

        for future in concurrent.futures.as_completed(future_to_job):
            job = future_to_job[future]
            try:
                data = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (job, exc))
            else:
                print("%r page is %d bytes" % (job, len(data)))


def do_job(job):
    zoom_x = 2.0
    zoom_y = 2.0
    mat = pymupdf.Matrix(zoom_x, zoom_y)
    database = "city_minutes.db"
    db = sqlite_utils.Database(database)

    print(f"Processing {job}")
    minutes = f"./data/{job[0]}/{job[1]}.pdf"

    try:
        doc = pymupdf.open(minutes)
    except:
        print(minutes)
        return
    if not os.path.exists(f"./out/{job[0]}/{job[1]}"):
        os.makedirs(f"./out/{job[0]}/{job[1]}")
    for page in doc:
        if os.path.exists(f"./out/{job[0]}/{job[1]}/{page.number + 1}.png"):
            continue
        pix = page.get_pixmap(matrix=mat)
        pix.save(f"./out/{job[0]}/{job[1]}/{page.number + 1}.png")
    for page_image in os.listdir(f"./out/{job[0]}/{job[1]}"):
        txt_filename = page_image.replace(".png", ".txt")
        if not os.path.exists(f"./out/{job[0]}/{job[1]}/{txt_filename}"):
            text = subprocess.check_output(
                [
                    "tesseract",
                    "-l",
                    "eng",
                    f"./out/{job[0]}/{job[1]}/{page_image}",
                    "stdout",
                ],
                stderr=subprocess.DEVNULL,
            )
            with open(f"./out/{job[0]}/{job[1]}/{txt_filename}", "wb") as textfile:
                textfile.write(text)
        if page_image.endswith(".txt"):
            continue

        with open(f"./out/{job[0]}/{job[1]}/{txt_filename}", "r") as textfile:
            text = textfile.read()
        page = page_image.replace(".png", "")
        db["pages"].insert(
            {
                "body": job[0],
                "date": job[1],
                "page": page,
                "text": text,
            },
            replace=True,
        )


if __name__ == "__main__":
    main()
