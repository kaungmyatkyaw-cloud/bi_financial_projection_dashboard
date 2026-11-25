# BI Financial Projection & Break-Even Point (BEP) Dashboard

Interactive financial projection and break-even analysis dashboard published via **GitHub Pages**, powered by automated data extraction (`export_to_json.py`), structured JSON datasets (`data.json`), and a client-side web interface (`index.html`).

---

## 1. System Architecture

The solution follows a lightweight, decoupled **Batch Export -> Static JSON -> Static Web UI** architecture:

```text
+-----------------------+       +---------------------+       +-------------------+
|   Source Data / DB    | ----> |  export_to_json.py  | ----> |     data.json     |
| (Sales, Cost, Margin) |       | (Transform & Calc)  |       | (Versioned Store) |
+-----------------------+       +---------------------+       +---------+---------+
                                                                        |
                                                                        v
+-----------------------+       +---------------------+       +-------------------+
|     GitHub Pages      | <---- |    GitHub Repo      | <---- |    index.html     |
| (Live Static Hosting) |       |  (main / gh-pages)  |       | (Charts & Models) |
+-----------------------+       +---------------------+       +-------------------+