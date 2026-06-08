# EHRsuction

EHRsuction downloads all **Compositions** from an **openEHR** platform and exports them into an organized structure:

```text
EHR_UID/composition-name.json
```

It also supports **FLAT format** using the view provided in the `resources` directory for **Better**.

> ⚠️ You need to upload the view first. Contact **Better support** for guidance.

For **EHRbase**, only **CANONICAL export** is currently supported.

---

## Requirements

- A running **openEHR** server
- **Python 3**

---

## Local Usage

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Modify `config.yaml` to your desired settings.

3. Run EHRsuction:

   ```bash
   python3 ehrsuction.py
   ```

---

## Docker Usage

EHRsuction can also be run inside a Docker container.

The Docker image uses `/export/` as the default export base directory via the `EHRSUCTION_OUTPUT_FOLDER` environment variable. This means the `output_folder` value in `config.yaml` does not need to be changed for Docker usage.

### Build the image

```bash
docker build -t ehrsuction:local .
```

### Run with a mounted config file and export directory

```bash
docker run --rm \
  -v "$PWD/config.yaml:/app/config.yaml:ro" \
  -v "$PWD/export:/export" \
  ehrsuction:local
```

The exported Compositions will be written to the local `export` directory.

Inside the container, the export path is:

```text
/export/EHR_export/
```

On the host system, this maps to:

```text
./export/EHR_export/
```

---

## Side Note

The **BETTER** setting for **CANONICAL** format also works with other **openEHR** platforms that correctly implement the **REST API**.

However, **EHRBASE** currently returns a **non-standardized response body** using `rows`, which has already been reported.
