# Channel-Mix & Pricing Recommendation
**Footwear & Apparel Sales Analytics — MIS Business Review**
Prepared from: 9,648 transactions, Jan 2020 – Dec 2021 (Adidas US Sales dataset)

---

## Bottom line

Operating margin variance across the business is driven overwhelmingly by **sales-channel mix**, not region. Outlet transactions run **14.0 percentage points below** the company's 35.1% average operating margin, driven by average discounting near 28% versus roughly 6% in-store. Online runs **2.0pp below** average. Regional discounting differences, by contrast, move margin by less than half a point in either direction. **The single highest-leverage lever available to leadership is rebalancing channel mix and tightening Outlet discount discipline — not renegotiating by region.**

## What the data shows

| Channel | Revenue share | Operating margin | vs. company avg |
|---|---|---|---|
| In-store | 46.3% | 42.7% | +7.6pp |
| Online | 33.5% | 33.1% | −2.0pp |
| Outlet | 20.1% | 21.1% | **−14.0pp** |

| Region | Revenue share | Operating margin | vs. company avg |
|---|---|---|---|
| Southeast | 20.7% | 34.8% | −0.4pp |
| Northeast | 20.4% | 35.0% | −0.1pp |
| West | 20.0% | 35.5% | +0.4pp |
| Midwest | 19.5% | 35.5% | +0.3pp |
| South | 19.4% | 35.0% | −0.2pp |

Weighting each segment's margin gap by its revenue share (the standard way to decompose "what actually moved the company average") confirms the story: Outlet's below-average margin pulls the company average down by **2.8pp** and Online's by **0.7pp**, an effect that In-store's above-average margin exactly offsets (+3.5pp) — that's how the channels net to the 35.1% overall figure. Region, by contrast, moves the average by at most **±0.08pp** in any direction. Channel mix's weighted effect is roughly **40x larger in magnitude than region's**, which is why it — not regional pricing — is the lever worth pulling.

The Region × Channel view shows the effects compound rather than offset: the weakest cells in the business are **Outlet transactions in the South and Southeast** (~21.0% margin), while the strongest are **In-store transactions in the West and Southeast** (~43%). No region "escapes" the Outlet margin penalty — it is a structural channel issue, present in every region at a similar magnitude.

## Recommendations

**1. Rebalance channel mix toward In-store and Online.**
Outlet currently carries 20% of revenue at a margin 14pp below average. A 5-point shift of revenue from Outlet to In-store (holding total revenue flat) lifts blended operating margin by roughly 1.1pp — worth modeling against Outlet's role in inventory clearance before acting, since some Outlet volume exists specifically to move aged stock.

**2. Tighten Outlet discount depth.**
Outlet's average discount (~28%) is roughly 4.5x In-store's (~6%). Even a 5-point reduction in average Outlet discounting — without changing channel mix — would meaningfully close the 14pp gap, since Outlet margin is highly discount-sensitive at these volumes.

**3. Treat regional pricing as secondary, not primary.**
Because regional margin spread is under half a point, region-by-region renegotiation or differentiated regional pricing programs are unlikely to move company-level margin materially. Regional discounting is a real but minor contributor (South and Southeast trend ~0.2–0.4pp below average) and can be addressed through standard regional discount-governance rather than a dedicated pricing initiative.

**4. Protect the Online channel's growth while watching its margin trend.**
Online carries a third of revenue at a moderate 2pp margin discount — healthy relative to Outlet, but worth monitoring monthly (see dashboard trend view) as it scales, since further discount creep here would be the next largest risk to blended margin after Outlet.

## Suggested next steps for leadership review

1. Quantify the Outlet channel's non-margin purpose (clearance, brand reach, new-customer acquisition) before setting a mix-shift target, so the recommendation accounts for trade-offs the margin data alone doesn't capture.
2. Pilot a 3–5pp Outlet discount cap in one region for one quarter and compare margin lift against sell-through, using the same channel/region cuts in this analysis.
3. Set a channel-mix target (e.g., cap Outlet at 15–18% of revenue) and track monthly via the accompanying dashboard.

---

*Methodology: transaction-level data was cleaned and validated in Python/Pandas (type coercion, dedup, referential checks between Total Sales and Price × Units, IQR outlier flagging), aggregated and cross-checked in SQL (SQLite) and in Excel (live SUMIFS pivot-style tables + a channel-mix what-if model), and visualized in the accompanying interactive dashboard. All figures in this document reconcile exactly across all three layers. See `README.md` for the full project structure.*
