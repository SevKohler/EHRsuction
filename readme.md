# EHRsuction

EHRsuction downloads all **Compositions** from an **openEHR** platform and exports them into an organized structure:

**EHR_UID/composition-name.json**

It also supports **FLAT format** using the view provided in the `resources` directory for **Better**.  
(⚠️ You need to upload it first—contact **Better support** for guidance.)

For **EHRbase**, only **CANONICAL export** is currently supported.

---

## Requirements
- A running **openEHR** server
- **Python 3**

---

## Use
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

## Side Note
The **BETTER** setting for **CANONICAL** format also works with other **openEHR** platforms that correctly implement the **REST API**.

However, **EHRBASE** currently returns a **non-standardized response body** (`rows`), which has already been reported.  

