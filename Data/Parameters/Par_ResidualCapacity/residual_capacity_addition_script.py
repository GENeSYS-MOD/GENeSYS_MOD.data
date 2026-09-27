import pandas as pd

# -----------------------------
# User settings
# -----------------------------
BASE_YEAR = 2018

# Input files
RESIDUAL_IN = "./Parameters/Par_ResidualCapacity/residual_rescaled.csv"
MISSING_PROD_IN = "./Parameters/Par_ResidualCapacity/missing_production.csv"

# Output file
OUT_FILE = "./Parameters/Par_ResidualCapacity/residual_with_missing_capacity_added.csv"


def main():
    residual = pd.read_csv(RESIDUAL_IN)
    missing_prod = pd.read_csv(MISSING_PROD_IN)

    # Validate columns
    required_residual = {"Region", "Technology", "Year", "Value"}
    required_missing = {"Region", "Technology", "Value"}  # Value = missing production in PJ

    if not required_residual.issubset(residual.columns):
        raise ValueError(
            f"Residual file must contain columns {required_residual}, got: {set(residual.columns)}"
        )

    if not required_missing.issubset(missing_prod.columns):
        raise ValueError(
            f"Missing production file must contain columns {required_missing}, got: {set(missing_prod.columns)}"
        )

    # If missing production file has Year, filter to base year
    if "Year" in missing_prod.columns:
        missing_prod = missing_prod.loc[missing_prod["Year"] == BASE_YEAR].copy()

    # Aggregate in case of duplicates
    missing_prod = (
        missing_prod.groupby(["Region", "Technology"], as_index=False)["Value"]
        .sum()
        .rename(columns={"Value": "missing_PJ"})
    )

    # Convert PJ -> GW using your rule: GW = PJ * 1000 / 8760
    #missing_prod["missing_GW"] = missing_prod["missing_PJ"] * 1000.0 / 8760.0
    missing_prod["missing_GW"] = missing_prod["missing_PJ"]


    # Base-year residual per region-tech (for multipliers)
    base_vals = (
        residual.loc[residual["Year"] == BASE_YEAR, ["Region", "Technology", "Value"]]
        .rename(columns={"Value": "base_value"})
    )

    # Add base_value and missing_GW onto each residual row
    df = residual.merge(base_vals, on=["Region", "Technology"], how="left")
    df = df.merge(missing_prod[["Region", "Technology", "missing_GW"]],
                  on=["Region", "Technology"], how="left")
    df["missing_GW"] = df["missing_GW"].fillna(0.0)

    # Compute multipliers: m(y) = Value(y) / Value(base_year)
    # If base_value is 0 or missing, we can't infer shape:
    # - add only to BASE_YEAR (multiplier=1 there, else 0)
    df["multiplier"] = 0.0

    mask_has_base = df["base_value"].notna() & (df["base_value"] != 0)
    df.loc[mask_has_base, "multiplier"] = df.loc[mask_has_base, "Value"] / df.loc[mask_has_base, "base_value"]

    mask_base_year = df["Year"] == BASE_YEAR
    df.loc[~mask_has_base & mask_base_year, "multiplier"] = 1.0

    # Add missing capacity following the same shape
    df["Value"] = df["Value"] + df["missing_GW"] * df["multiplier"]

    # Optional safety: prevent negative capacities
    df.loc[df["Value"] < 0, "Value"] = 0.0

    out = df[["Region", "Technology", "Year", "Value"]].sort_values(["Region", "Technology", "Year"])
    out.to_csv(OUT_FILE, index=False)

    # Diagnostics: which missing pairs didn't match residual file?
    residual_pairs = set(zip(residual["Region"], residual["Technology"]))
    missing_pairs = set(zip(missing_prod["Region"], missing_prod["Technology"]))
    unmatched = sorted(missing_pairs - residual_pairs)
    if unmatched:
        print(f"WARNING: {len(unmatched)} (Region,Technology) pairs in missing production file not found in residual file.")
        print("First 20 unmatched:", unmatched[:20])

    print(f"Saved: {OUT_FILE}")


if __name__ == "__main__":
    main()