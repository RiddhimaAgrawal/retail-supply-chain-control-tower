# Retail and Supply Chain Control Tower — KPI Definitions

## Dataset

- Source: DataCo Smart Supply Chain dataset
- Analysis unit: One unique `Order Id`
- Total unique orders: 65,752
- Canceled orders: 2,855
- Eligible delivery orders: 62,897

## 1. Late Delivery Rate

**Definition:** Percentage of eligible delivery orders whose `Delivery Status` is `Late delivery`.

**Formula:**

Late Delivery Rate = Late Orders / Eligible Delivery Orders × 100

- Late orders: 36,048
- Eligible delivery orders: 62,897
- Result: 57.31%

Canceled orders are excluded from the denominator.

## 2. Non-Late Delivery Rate

**Definition:** Percentage of eligible delivery orders not labeled `Late delivery`.

- Non-late orders: 26,849
- Eligible delivery orders: 62,897
- Result: 42.69%

This includes orders labeled `Advance shipping` and `Shipping on time`.

## 3. Order Cancellation Rate

**Definition:** Percentage of unique orders labeled `Shipping canceled`.

- Canceled orders: 2,855
- Total unique orders: 65,752
- Result: 4.34%

## 4. Shipping-Mode Late Rate

For each shipping mode:

Shipping-Mode Late Rate = Late Orders in Mode / Eligible Orders in Mode × 100

Canceled orders are excluded from each shipping mode's denominator.

## Data-quality checks

- Checked whether shipping fields were consistent across product rows belonging to the same order.
- Found no orders with inconsistent values across the checked fields.
- Found 1,650 discrepancies between duration-based lateness and `Late_delivery_risk`; all belonged to canceled orders.
- Delivery performance calculations therefore use `Delivery Status` and exclude canceled orders.

## Limitations

- These are historical dataset metrics, not live operational measurements.
- The dataset does not provide reliable inventory snapshots for a live stock-out calculation.
- Inventory and shipment updates will need to be simulated or sourced separately for the Control Tower prototype.
- A high late rate is an observation, not evidence of its cause.