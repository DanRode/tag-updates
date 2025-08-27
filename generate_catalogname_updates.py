#!/usr/bin/env python3
"""Generate catalog name update report.

This script compares the catalog tag values in ``CatalogNames-by-RG.csv``
with the canonical values defined in ``Total-Products-190-Aug-27.xlsx``.
It outputs ``catalogname_updates.csv`` listing every tag that needs to be
updated and whether the change can be applied at the cloud vendor account
level or must be performed per resource group.
"""

from __future__ import annotations

import pandas as pd

CATALOG_FILE = "Total-Products-190-Aug-27.xlsx"
TAGS_FILE = "CatalogNames-by-RG.csv"
OUTPUT_FILE = "catalogname_updates.csv"


def main() -> None:
    # Load canonical mapping of SalesForce Id to CatalogName
    catalog = pd.read_excel(CATALOG_FILE, usecols=["SalesForce Id", "CatalogName"])
    id_to_name = catalog.set_index("SalesForce Id")

    # Load current tags
    tags = pd.read_csv(
        TAGS_FILE,
        usecols=[
            "Cloud Vendor",
            "Cloud Vendor Account Name",
            "Resource Group",
            "CatalogId",
            "CatalogName",
        ],
    )

    # Attach canonical name and mark mismatches
    tags["CanonicalName"] = tags["CatalogId"].map(id_to_name["CatalogName"])
    tags["NeedsUpdate"] = tags["CatalogName"] != tags["CanonicalName"]

    # Determine update scope: account vs. resource group
    def update_scope(group: pd.DataFrame) -> str:
        if group["NeedsUpdate"].any():
            if group["CatalogName"].nunique() == 1:
                return "Account"
            return "ResourceGroup"
        return "None"

    scope = tags.groupby("Cloud Vendor Account Name").apply(update_scope)
    tags = tags.merge(
        scope.rename("UpdateScope"),
        left_on="Cloud Vendor Account Name",
        right_index=True,
    )

    # Keep only entries needing changes and write output
    updates = tags[tags["NeedsUpdate"]]
    columns = [
        "Cloud Vendor",
        "Cloud Vendor Account Name",
        "Resource Group",
        "CatalogId",
        "CatalogName",
        "CanonicalName",
        "UpdateScope",
    ]
    updates.to_csv(OUTPUT_FILE, columns=columns, index=False)


if __name__ == "__main__":
    main()
