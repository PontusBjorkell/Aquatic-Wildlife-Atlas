# Statistical Analysis Report

## Scope

The analysis uses **101 full scientific-name taxa** as its units. The
200,000 observation records are intentionally not treated as independent
biological replicates because the dataset contains strong template-generated
patterns.

## Methods

- Taxon-level descriptive statistics
- Spearman rank correlations
- Mann–Whitney U tests for threatened versus other taxa
- Kruskal–Wallis tests across adequately represented habitat groups
- Chi-square tests with bias-corrected Cramér's V
- Log-log allometric regression of body weight on body length
- Benjamini–Hochberg false-discovery-rate correction within each test family

## Main numerical results

- Significant Spearman relationships after FDR correction:
  **12**
- Strongest absolute Spearman relationship:
  **Mean_Body_Length_cm × Mean_Body_Weight_kg**
  (rho = 0.925)
- Significant threatened/non-threatened comparisons:
  **3**
- Significant habitat comparisons:
  **3**
- Significant categorical associations:
  **0**
- Allometric slope:
  **2.533**
- Allometric R²:
  **0.888**

## Interpretation boundary

These results describe internal structure in the supplied educational dataset.
They must not be interpreted as population estimates, causal ecological
effects, or independently verified biological findings. Taxonomy may also
create dependence among taxa, which this exploratory analysis does not model
phylogenetically.
