# R2 protocol — required factual and numerical precision

## Scientific question

Does factual reliability degrade when the same stored information is requested at stricter precision, and do confidence estimators recognize that degradation?

## Testcase file and sample size

File: ../../testcases/r2_precision.jsonl

- 16,000 records.
- 2,000 paired worlds.
- Eight precision tasks per world:
  - categorical;
  - year;
  - month and year;
  - exact date;
  - integer;
  - one decimal place;
  - three decimal places;
  - five decimal places.
- Every world stays within one split.
- Locked test: 500 worlds × eight queries = 4,000 records.

The within-world design removes much of the variance from entity familiarity and injection success. With 500 locked test worlds and 400 calibration worlds, every precision level meets the preferred independent-unit minimum and all eight conditions have direct within-world contrasts.

## Knowledge injection

Each world contains:

- one categorical fact;
- one exact ISO date;
- one exact numerical value with five decimal places.

Inject exact values at 16 exposures through balanced templates. Do not train on the evaluation wording or rounded answers alone.

## Grading

Use the method encoded in grading:

- canonical exact for category;
- date component for year/month;
- ISO exact for exact date;
- numeric parser with the stored rounding rule and absolute tolerance.

Reject:

- correct magnitude with insufficient requested digits;
- malformed dates;
- extra incompatible values;
- ranges when one exact value is required.

Manually review 100 numerical/date cases and all parser disagreements.

## Procedure

1. Confirm direct exact-value cloze recall after injection.
2. Run all eight variants for every world.
3. Cache greedy answer, five samples, and log probabilities.
4. Parse numeric values without using model confidence.
5. Score correctness at the required precision.
6. Fit uncertainty scorers on fit only.
7. Choose policies on tune.
8. calibrate on calibrate.
9. Open locked test once.

## Outcomes

Primary:

- accuracy at each precision level;
- within-world loss as precision tightens;
- answer coverage under the primary false-commit contract;
- group coverage gap at exact date and five decimals.

Secondary:

- absolute numerical error;
- number of correct significant digits;
- date-component error taxonomy;
- overconfidence among near-miss answers;
- semantic/sample agreement despite consistent wrong digits.

## Statistical analysis

- Conditional logistic or mixed-effects logistic regression with world intercept.
- Planned contrasts:
  - year versus exact date;
  - integer versus one decimal;
  - one versus three decimals;
  - three versus five decimals.
- Holm adjustment over the four contrasts.
- Model × precision interaction.
- Paired bootstrap by world for accuracy, Brier, and coverage-at-risk differences.

Do not pool categorical, date, and numeric results without type indicators.

## Specific reliability tests

- Does token likelihood fall as required precision rises?
- Do optional P(True)/token scores remain high on near misses?
- Does exact answer entropy fail when all samples repeat the same wrong number?
- Does adding precision metadata to the scorer improve worst-group calibration?
- Does a global threshold under-cover exact-date/five-decimal groups?

## Required output

- Figure: paired accuracy curve by precision.
- Figure: confidence minus empirical accuracy by precision.
- Plot: distribution of numerical absolute errors.
- Table: planned contrasts.
- Table: global versus precision-conditioned contract results.
