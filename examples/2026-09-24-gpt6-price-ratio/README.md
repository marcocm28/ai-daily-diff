# GPT-6 fixed-token price comparison

Source: [OpenAI API changelog, September 22](https://developers.openai.com/api/docs/changelog), checked September 24, 2026. See also the [launch announcement](https://openai.com/index/introducing-gpt-6-sol-and-luna/).

Run `bash run.sh`. Standard-library Decimal arithmetic, offline CPU.

The fixed synthetic workload contains 10,000 uncached input tokens and 2,000 billed output tokens. The only changed variable is the model's published Standard token rates. The headline metric is the Sol/Luna total-cost ratio. Prices are frozen for reproducibility, in USD per million tokens.

This is not cost per successful task: the models can use different token counts and yield different quality. Output includes any billed reasoning in the hypothetical total. Prompt length is below the documented 272,000-input-token threshold. Cached reads, cache writes, long-context pricing, other tiers, retries, tools and taxes are excluded. No inference or latency was measured. Validate quality on the actual workload before routing to a cheaper model.
