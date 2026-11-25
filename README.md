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

```
---
## Component Breakdown
*Data Extraction & Transformation (export_to_json.py)*: Pulls raw financial/operational figures, normalizes numeric/date types, computes baseline or scenario metrics, and serializes clean JSON output into data.json.

*Data Payload (data.json)*: Acts as the single static data contract between the data layer and the frontend dashboard, keeping page loads fast without exposing live database credentials.

*Presentation & Projection Engine (index.html)*: Loads data.json, renders interactive charts/KPIs/projection tables in the browser, and allows dynamic parameter/scenario adjustments on the client side.

*Hosting & Delivery (GitHub Pages)*: Serves index.html and data.json over HTTPS directly from the repository with zero backend server maintenance.

## 2. Data Model & Projection Logic
**Core Data Fields (data.json)**
*Revenue / Sales Drivers*: Baseline revenue, volume/unit assumptions, pricing, or growth rates across periods/entities.

**Cost Structure**:

*Fixed Costs*: Overhead, salaries, rent, and recurring operational expenses that remain constant across output levels.

*Variable Costs*: Cost of goods sold (COGS), fulfillment/delivery costs, or direct unit costs that scale with volume/revenue.

**Profitability & Break-Even Metrics**:

*Contribution Margin*: Revenue minus variable costs (and contribution margin ratio).

*Break-Even Point (BEP)*: The revenue or unit threshold where total contribution margin equals total fixed costs (Operating Profit / Net Margin = 0).

*Projected Cash / Profit Trajectory*: Period-by-period projections comparing baseline vs. target/scenario performance.