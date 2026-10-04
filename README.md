# SmartVet broiler budget calculator

A single-page calculator for SmartVet Africa and River Poultry Farms field staff to build a broiler production budget for a farmer.

- `index.html` and `logo.webp`: the calculator. No build step; open the file or host it as a static site.
- `pdf/build_budget_pdf.py`: the ReportLab script that builds the branded PDF version of a budget (`pip install reportlab`, then `python build_budget_pdf.py` from the `pdf` folder).

## What the calculator covers

Farmer and batch, one or two selling options side by side, chicks, feed (bought starter plus maize and 25% concentrate mixes costed in whole bags), health and biosecurity, labour, small supplies and manure. Items ticked as already purchased count in total cost and profit but not in the cash still needed.

Entries are saved in the browser on the device only. "Print / save PDF" prints the budget sheet.

## Deployment

Hosted on Vercel as a static site: https://smartvet-broiler-budget.vercel.app

Prices in the example are from October 2026 and should be reconfirmed with suppliers.
