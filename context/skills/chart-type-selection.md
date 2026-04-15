# Chart Type Selection

## When To Use This Skill
Before creating any Plotly chart. State the analysis question first.

## Procedure

Step 1 — State the analytical question.
In one sentence: what must the chart help the reader answer?

Step 2 — Identify data shape.
How many series? Ordinal, categorical, or continuous? Is there a time dimension? What is the cardinality of the category axis? Nested hierarchy?

Step 3 — Match task + data shape to a chart family using the table below.

## Task-to-Chart Family Table

| Analysis Task                          | Data Shape                           | Recommended Chart                   |
|----------------------------------------|--------------------------------------|-------------------------------------|
| Trend over time, 1–5 series            | time × value                         | Line chart                          |
| Trend over time, many overlapping      | time × value × N series (N > 5)      | Small multiples (faceted lines)     |
| Category comparison, ranked            | category × value, n ≤ 20             | Horizontal sorted bar               |
| Category comparison, high cardinality  | category × value, n > 20             | Paginated horizontal bar            |
| Part-whole, 2–3 parts only             | category × proportion, n ≤ 3         | Pie (paired with table)             |
| Part-whole, more than 3 parts          | category × proportion, n > 3         | Sorted bar (do not use pie)         |
| Distribution shape                     | continuous values, one dimension     | Histogram                           |
| Distribution + summary stats           | continuous values, one+ groups       | Box plot (paired with histogram)    |
| Correlation / relationship             | two continuous dimensions            | Scatter plot                        |
| Correlation + grouping                 | two continuous + one categorical     | Scatter with color encoding         |
| Matrix / intensity                     | row × column × value                 | Heatmap                             |
| Calendar or time-of-day pattern        | hour/day-of-week × value             | Calendar heatmap                    |
| Process drop-off / funnel              | ordered stages × counts              | Funnel chart                        |
| Hierarchical breakdown, depth ≥ 2      | hierarchy × value                    | Treemap or sunburst (use sparingly) |
| Many small groups compared             | group × value, many groups           | Small multiples                     |

## Guidance Notes
- Time series: annotate anomalies with shapes or vertical lines; include date range filter
- Distributions: pair histogram + box plot; summary card showing mean, median, P95, P99
- Heatmaps: sequential colorscale for intensity; diverging for deviation from midpoint; never rainbow
- Treemap/sunburst: three hierarchy levels is usually the maximum before cognitive overload
- Scatter: verify one variable is not actually categorical — use box plot or bar if so

## Anti-Patterns
- choosing a chart because it looks impressive (3D, radial, animated)
- pie chart when n > 3 or when the question is not part-whole
- one chart answering multiple unrelated questions simultaneously
- line chart with an unordered categorical x-axis (use bar instead)

## Verify Before Proceeding
- "Does this chart answer exactly one stated question?"
- "Is the type justified by task AND data shape?"
- "Will axis titles, hover content, and legend labels make the answer readable?"