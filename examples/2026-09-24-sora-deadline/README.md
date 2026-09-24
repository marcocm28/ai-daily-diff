# Audit the Sora retirement deadline

Source: [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations), checked September 24, 2026. The March 24 announcement schedules retirement of the Videos API and the listed Sora models for September 24.

Run `bash run.sh`. Standard library only, offline CPU.

The fixture freezes the episode date and uses a synthetic job inventory. The baseline queues every listed job. The intervention blocks listed retired model IDs on or after the documented date. The metric is calendar days until retirement, floored at zero. It also prints the job decisions for inspection.

This deliberately conservative date-level guard does not contact OpenAI or prove an endpoint is down. It does not inspect endpoint URLs, nested application configuration, other providers or other deprecations. ALLOW means only that this Sora-specific rule did not match. The source provides no replacement in this table. Review actual integrations before choosing a replacement.
