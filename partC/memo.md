# Decision Memo

**Recommendation: Use prompt engineering with curated few-shot exemplars.**

## Assumptions

1. **The base model already understands casual language in all six languages.** The main problem is assumed to be elicitation, not missing capability. If this is wrong, prompting alone will not work.

2. **A 7 to 8B open-source multilingual model can run efficiently on the A100.** At roughly 800 tokens/sec when batched, generating candidates is cheap and not the main constraint.

3. **Self-consistency can act as an automated quality filter.** Multiple candidate responses are generated, and responses with stronger agreement are kept.

4. **Casual style can be achieved through a small number of strong examples.** This is reasonable for tone and style, but not necessarily for factual or safety-critical behavior.

## Explanation

### Generation

6 languages × 500 candidates = **3,000 generations**.

At about 150 tokens per response and 800 tokens/sec, total raw generation takes roughly **9 to 10 minutes** on the A100.

The GPU is therefore not the bottleneck.

### Human review

Reviewers have:

10 hrs/week × 3 weeks = **30 hours = 1,800 minutes**.

At about 3 minutes per example, this gives capacity for roughly **600 examples total**, or about **300 per language** across Hindi and Kannada.

Therefore, automated filtering must reduce the 500 candidates per language before human review.

### Other four languages

Tamil, Telugu, Bengali, and Marathi receive **automated filtering only**, with no human sign-off before launch.

This is the biggest risk in the plan.

### Final prompt

Select **8 gold exemplars per language**, where exemplars are **high-quality examples of casual conversations** included in the final system prompt.
They show the model **how formal text should be naturally rewritten into casual language** for each language,
and place them directly in the system prompt.

This adds roughly:

8 × 60 = **480 tokens per request**

This is a permanent serving cost. The tradeoff is zero training cost and easy reversibility.

## Success Metric

### Hindi and Kannada

Native-speaker naturalness score of **≥ 4/5** on 30 held-out, production-style prompts per language.

### Tamil, Telugu, Bengali, and Marathi

Here, we use an automated quality check instead of human review.

We generate multiple responses for the same input and measure how often they produce similar casual-style outputs. If the agreement is 70% or higher, we consider the result consistent enough to pass the automated check.

**However, 70% agreement does not guarantee that the language sounds natural to a native speaker, so it is only a proxy for quality.**

## Kill Criterion

By **Day 10**, if Hindi or Kannada scores below **3/5** after deploying the exemplars:

**Stop the few-shot approach.**

This would suggest that the problem is deeper than prompt elicitation. Move to a small rewriter model or SFT instead.

Day 10 is important because it leaves enough time to pivot before the 3-week launch review.

## Day-1 Experiment

Start with Hindi:

1. Generate 20 casual-style responses.
2. Apply self-consistency filtering.
3. Select the top 5.
4. Have the native-speaker reviewer score them the same day.

This gives an early test of both the core assumption and the generation pipeline before expanding to all six languages.

## Biggest Caveat

**Four of the six languages have no human validation before launch.**

That risk comes directly from limited reviewer capacity and cannot be solved through better prompting alone.

The advantage of the recommended approach is that it **fails cheaply and reversibly**. If the proxy does not work, the prompts can be changed or the project can move to SFT or a small rewriter without having already invested heavily in training.