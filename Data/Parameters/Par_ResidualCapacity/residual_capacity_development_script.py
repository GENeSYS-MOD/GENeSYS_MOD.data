import pandas as pd

base_year = 2018

old = pd.read_csv("./Parameters/Par_ResidualCapacity/old_cap.csv")

# new base: keep only 2018 base-year values and only the value column
new_base = pd.read_csv("./Parameters/Par_ResidualCapacity/new_cap.csv")

# If new_cap has multiple years, filter to base year.
# If it has no Year column, this still works via the if.
if "Year" in new_base.columns:
    new_base = new_base.loc[new_base["Year"] == base_year].copy()

new_base = new_base.rename(columns={"Value": "new_base"})[["Region", "Technology", "new_base"]]

# old 2018 per region-tech
old_base = (
    old.loc[old["Year"] == base_year, ["Region", "Technology", "Value"]]
    .rename(columns={"Value": "old_base"})
)

df = old.merge(old_base, on=["Region", "Technology"], how="left")
df = df.merge(new_base, on=["Region", "Technology"], how="left")

# keep only pairs where both bases exist
df = df[df["old_base"].notna() & df["new_base"].notna()].copy()

# rescale
mask_zero = df["old_base"] == 0
df.loc[~mask_zero, "Value"] = df.loc[~mask_zero, "Value"] * (df.loc[~mask_zero, "new_base"] / df.loc[~mask_zero, "old_base"])
df.loc[mask_zero, "Value"] = 0

# force base year exactly
df.loc[df["Year"] == base_year, "Value"] = df.loc[df["Year"] == base_year, "new_base"]

out = df[["Region", "Technology", "Year", "Value"]].sort_values(["Region", "Technology", "Year"])
out.to_csv("./Parameters/Par_ResidualCapacity/residual_rescaled_hb.csv", index=False)