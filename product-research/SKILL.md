---
name: product-research
description: Interview-led best-buy product research for real purchases. Use when the user asks to research, compare, choose, recommend, or find the best-value product from specific stores/sites or marketplaces, especially for personal care, health-adjacent products, appliances, electronics, computers, clothing, household items, or any purchase where requirements, tradeoffs, ingredients/specs/materials, safety, reviews, value, or long-term fit matter. Triggers include "best buy", "recommend a product", "research X on site Y", "compare products", "interview me first", "what should I buy", "is this worth it", and reusable shopping/product prompts.
---

# Product Research

Run an interview-led research workflow that ends in a concrete best-buy recommendation. Optimize for fit, evidence, and value, not premium branding or marketing claims.

## Workflow

1. Interview the user before researching unless the brief is already complete.
2. Summarize the buying brief and proceed when the tradeoffs are clear.
3. Browse target stores/sites and gather candidate products.
4. Read product pages for hard evidence: ingredients, specs, materials, manuals, warnings, policies, and price.
5. Use reputable external sources only when they help interpret safety, claims, standards, reliability, or category science.
6. Score candidates against the confirmed brief.
7. Recommend one best buy, runner-ups, and explicit rejects.

When a browser is available and the user asks to watch or the task benefits from live site inspection, keep the browser visible. State which site, category, query, or page is being inspected and summarize each batch before moving on.

## Interview

Ask concise questions in batches. Do not ask a large intake form at once.

First establish:

- Product category and target stores/sites.
- Country/market/currency.
- Budget, ceiling, and whether paying extra is acceptable for clear gains.
- Intended user and context: who, where, how often, constraints.
- Problem to solve and what a good purchase must do.
- Hard requirements, nice-to-haves, dealbreakers, sensitivities, and maintenance constraints.

For category-specific tradeoffs, read `references/category-question-bank.md` when useful. Use only the relevant section. Explain each non-obvious choice in practical terms before asking for yes/no or preference.

Examples:

- "Aluminum antiperspirant stops sweat better; deodorant mainly controls smell. Which job matters most?"
- "Silicone is not automatically bad, but it can weigh down fine hair and build up for some people. Is light feel or maximum smoothing more important?"
- "Basket air fryers are faster and easier to clean; oven-style units hold more but take more counter space."

After the interview, summarize the buying brief. Ask for confirmation only if a material tradeoff is unresolved. Otherwise proceed.

## Candidate Gathering

Use the site's own categories and likely search terms. Use pagination where practical, but do not claim full-catalog completeness when pagination is huge or the site blocks extraction.

For every relevant candidate, capture:

- Product name.
- Brand.
- URL.
- Current price.
- Size, amount, or key specs.
- Unit price or comparable value metric.
- Claimed target/use.
- Ingredients, specs, materials, components, certifications, or manuals.
- Fit against hard requirements.
- Fit against nice-to-haves.
- Warnings, usage limits, compatibility issues, maintenance, return, or warranty caveats.
- Reasons it may be a bad fit.

Exclude obvious non-matches and duplicate bundle/listing variants unless they change the value calculation.

If scraping is blocked, pagination is too large, reviews are unavailable, ingredients/specs are missing, or prices are unclear, state exactly what is missing and continue with the strongest available sample.

## Evidence Rules

Do not rely on marketing text alone.

Prefer:

- Ingredient lists and INCI names for personal care.
- Product manuals, spec sheets, model numbers, and warranty terms for durable goods.
- Material composition and care instructions for clothing.
- Reputable medical/public-health sources for health-adjacent claims.
- Standards bodies, official docs, repair databases, lab tests, and long-form reviews for technical categories.
- Review patterns only when they are concrete and repeated, such as "basket coating peels" or "fan is loud", not vague star averages.

Treat affiliate-heavy listicles and generic SEO reviews as weak evidence.

For health, safety, legal, electrical, expensive, or persistent medical symptoms, say when a pharmacist, doctor, electrician, mechanic, or other specialist is appropriate.

## Scoring

Build a scoring model from the confirmed brief. Use 5-8 criteria. Weight hard requirements above nice-to-haves.

Common criteria:

- Core functional fit.
- Safety, tolerance, or compatibility.
- Evidence quality.
- Value for money.
- Durability and maintenance.
- Convenience and ergonomics.
- Nice-use factor.
- Environmental fit, weighted by real difference between options.

Penalize:

- Marketing-led products without evidence.
- Premium price without a clear user-relevant advantage.
- Risky ingredients/specs/materials for the user's constraints.
- Heavy, bulky, fragile, hard-to-clean, hard-to-return, or high-maintenance options.
- Products that solve a different problem than the user actually has.

Environmental fit should not take over the recommendation unless the product-level difference is material. Consider the relevant axis for the category:

- Packaging: refillable, reusable, recyclable, excessive, mixed-material, aerosol/propellant, or hard-to-sort packaging.
- Ingredients and materials: problematic chemicals, allergens, microplastics, VOCs, solvents, PFAS, batteries, rare materials, or certified safer alternatives when relevant.
- Durability and BIFL: expected lifespan, repairability, replaceable parts, warranty, spare-part availability, and whether paying more reduces replacement churn.
- Use-phase impact: energy, water, consumables, filters, cartridges, bags, charging, cleaning chemicals, or waste created during normal use.
- End-of-life: recyclability, hazardous waste handling, battery disposal, take-back programs, and resale/donation viability.

Keep separate recommendation lanes when needed, for example:

- Daily/default product vs occasional treatment.
- Budget pick vs premium pick.
- Travel/portable vs home use.
- Sensitive-skin safe pick vs fragranced nice-use pick.

## Output

Start with the top recommendation and why it is the best buy.

Then include:

- 3-5 runner-ups, each with when to choose it instead.
- A compact comparison table with price, size/spec, unit price/value metric, key evidence, fit, and caveats.
- Rejected products with short reasons, especially expensive, marketing-heavy, risky, or poor-value options.
- Source links to retailer pages and external references.
- Clear notes where evidence is weak or the catalog sample is incomplete.

Be direct, skeptical, and practical. Prefer a useful best-buy answer over a long neutral catalog summary.

## Saved Recommendation Log

When the user asks to save or maintain recommendation outputs, use Apple Notes if available.

Default note title: `Best Buy Recommendations`.

Each saved entry should be compact and repeatable:

- Date and product category.
- Top recommendation and where to buy it.
- Small comparison table with product, current/best found price, fit, and caveat.
- Pros.
- Cons and watch-outs.
- What the recommendation was based on: user brief, hard requirements, evidence type, and scoring logic.
- Sources checked with retailer and external evidence links.
- Notes about weak evidence, incomplete catalog coverage, price volatility, or environmental tradeoffs.

If the note already exists, append or rewrite the note with the new entry preserved. Apple Notes rewrites HTML, so prefer rewriting the full body over fragile string replacement.
