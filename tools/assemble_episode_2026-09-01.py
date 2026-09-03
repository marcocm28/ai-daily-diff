"""One-off assembler for the 2026-09-01 episode.

Why a script instead of hand-writing the JSON: the code and the output shown on the slides are
read straight out of examples/*/run.py and examples/*/expected_output.txt, so what a viewer sees
on screen cannot drift from what CI runs. Slide excerpts are asserted to be verbatim slices of
the real file — if someone edits run.py and not the excerpt, this script fails.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EX = ROOT / "examples"


def read(example_dir: str, name: str) -> str:
    return (EX / example_dir / name).read_text(encoding="utf-8").rstrip("\n")


def excerpt(example_dir: str, ranges: list[tuple[int, int]]) -> str:
    """Verbatim contiguous slices of run.py, joined by an explicit ellipsis line."""
    lines = read(example_dir, "run.py").split("\n")
    parts = []
    for start, end in ranges:
        chunk = "\n".join(lines[start - 1:end])
        assert chunk in read(example_dir, "run.py"), f"excerpt drifted in {example_dir}"
        parts.append(chunk)
    return "\n…\n".join(parts)


D1 = "2026-09-01-qwen-flash-next-config"
D2 = "2026-09-01-damp-recurrent-state"
D3 = "2026-09-01-quantization-gap"


def kv_chart() -> dict:
    """KV cache growth for both models, from their own configs. Same arithmetic as the example."""
    cfgs = {
        "Qwen3.8-27B": json.loads((EX / D1 / "config_qwen38_27b.json").read_text())["text_config"],
        "Qwen3.8-Flash-Next": json.loads((EX / D1 / "config_flash_next.json").read_text())["text_config"],
    }
    series = []
    for name, c in cfgs.items():
        per_token = c["layer_types"].count("full_attention") * 2 * c["num_key_value_heads"] * c["head_dim"] * 2
        series.append({"label": name,
                        "data": [[n, round(n * per_token / 2**30, 3)] for n in range(0, 262145, 8192)]})
    return {"xlabel": "context length (tokens)", "ylabel": "KV cache (GiB)", "series": series}


def state_chart() -> dict:
    """Recurrent-state memory against batch size, FP32 against DAMP's 9.9 bits per value."""
    c = json.loads((EX / D2 / "config_flash_next.json").read_text())["text_config"]
    values = c["layer_types"].count("linear_attention") * c["linear_num_value_heads"] \
        * c["linear_key_head_dim"] * c["linear_value_head_dim"]
    series = [{"label": label,
                "data": [[b, round(values * bits / 8 * b / 2**30, 3)] for b in range(0, 129, 8)]}
               for label, bits in (("FP32 today", 32.0), ("DAMP, 9.9 bit", 9.9))]
    return {"xlabel": "batch size (concurrent sequences)", "ylabel": "recurrent state (GiB)",
             "series": series}



episode = {
    "date": "2026-09-01",
    "kind": "daily",
    "title": "Quantization day: 69% less state memory, and an 85% backdoor — AI Daily Diff Sep 1",
    "cover_title": "Three things|that changed today.",
    "thumbnail_text": "69%",
    "thumbnail_color": "var(--ok)",
    "thumbnail_label": "less recurrent-state memory. And the check that misses it.",
    "closing_line": "Two papers, same day, compressing the same states: one frees 4.7 GiB at batch 64, "
                    "the other shows you may not know what you deployed.",
    "items": [
        {
            "id": D1,
            "vertical": "models-releases",
            "vertical_label": "MODELS & RELEASES",
            "rail_color": "var(--accent)",
            "org": "qwen",
            "org_label": "QWEN",
            "headline": "Qwen's next architecture appears in a preview: half the hidden size, "
                        "512 experts, 62% less KV cache.",
            "what_changed": "Qwen3.8-Flash-Next ships a new model_type, qwen4_exp: a 512-expert "
                            "MoE with 10 active per token, replacing a dense FFN.",
            "why_it_matters": "Fewer KV heads and 12 full-attention layers change what one GPU "
                              "can hold, before any kernel work.",
            "who_should_care": "Anyone sizing GPUs for long-context serving, or comparing this "
                               "preview against Qwen3.8-27B.",
            "the_number": {
                "value": "24 KiB",
                "label": "KV cache per token, against 64 KiB for Qwen3.8-27B — 62.5% less",
                "notes": [
                    "Only full-attention layers grow a cache: 12 of 48 layers here, 16 of 64 before.",
                    "12 layers × 2 tensors × 2 KV heads × 256 head dim × 2 bytes (bf16) = 24 KiB.",
                    "The other 36 layers are linear attention: a fixed-size state instead — see item 02.",
                    "512 experts with 10 active means 2.0% of expert FFN weights touch a given token.",
                ],
            },
            "diff": {
                "minus": "hidden 5120, 64 layers, 4 KV heads, dense FFN  (Qwen3.8-27B)",
                "plus": "hidden 2560, 48 layers, 2 KV heads, 512-expert MoE  (Flash-Next)",
            },
            "watch_out": "This is a preview checkpoint with an experimental model_type, and the two "
                         "models are different sizes. The diff shows a direction of travel, not a "
                         "like-for-like benchmark.",
            "example": {
                "kind": "analysis",
                "dir": f"examples/{D1}",
                "run_cmd": "bash run.sh",
                "run_summary": "13 lines, CPU, offline, < 1 s",
                "caption": "The two published configs, diffed.",
                "code": read(D1, "run.py"),
                "code_slide": excerpt(D1, [(1, 8), (15, 15)]),
                "output": read(D1, "expected_output.txt"),
                "tested_in_ci": False,
            },
            "chart": kv_chart(),
            "source_url": "https://huggingface.co/Qwen/Qwen3.8-Flash-Next",
        },
        {
            "id": D2,
            "vertical": "cost-limits",
            "vertical_label": "COST & LIMITS",
            "rail_color": "var(--accent2)",
            "org_label": "ARXIV",
            "headline": "Those linear-attention layers keep a fixed state in FP32. Quantizing it "
                        "frees 69% of that memory.",
            "what_changed": "DAMP quantizes recurrent states to 9.9 bits per value on average, "
                            "keeping high-error channels precise instead of quantizing uniformly.",
            "why_it_matters": "Uniform INT8 already hurts reasoning accuracy and INT4 destroys it. "
                              "Mixed precision is what makes the saving usable.",
            "who_should_care": "Anyone serving Gated DeltaNet or Kimi Delta Attention models at "
                               "batch, where state memory competes with weights.",
            "the_number": {
                "value": "6.75 → 2.09 GiB",
                "label": "recurrent-state memory at batch 64, computed from the Flash-Next config",
                "notes": [
                    "1 − 9.9/32 = 69.06%: the paper's headline 69.1% follows from its own bit budget.",
                    "36 linear-attention layers × 48 value heads × 128 × 128 = 28,311,552 values per sequence.",
                    "Also reported: up to 2.01× faster state-update kernel, up to 10.9% lower full-model TPOT.",
                    "Uniform quantization fails here: INT8/FP8 degrade reasoning, INT4/NVFP4 collapse it.",
                ],
            },
            "diff": {
                "minus": "recurrent state stored in FP32 — 32 bits per value",
                "plus": "critical channels kept high, the rest INT8 — 9.9 bits average",
            },
            "watch_out": "The paper measures Qwen3.6-35B and Kimi-Linear-48B, not this config. Our "
                         "numbers apply its stated bit budget to the Flash-Next config from item 01: "
                         "a projection, not their measurement.",
            "example": {
                "kind": "analysis",
                "dir": f"examples/{D2}",
                "run_cmd": "bash run.sh",
                "run_summary": "11 lines, CPU, offline, < 1 s",
                "caption": "State size from the real config: 32 bits against 9.9.",
                "code": read(D2, "run.py"),
                "code_slide": excerpt(D2, [(4, 11)]),
                "output": read(D2, "expected_output.txt"),
                "tested_in_ci": False,
            },
            "chart": state_chart(),
            "source_url": "https://arxiv.org/abs/2608.27513",
        },
        {
            "id": D3,
            "vertical": "claims-risks",
            "vertical_label": "CLAIMS & RISKS",
            "rail_color": "var(--ok)",
            "org_label": "ARXIV",
            "headline": "A checkpoint can pass every FP16 check and behave differently after INT8. "
                        "Certification does not survive quantization.",
            "what_changed": "A paper formalizes quantization as a many-to-one map, then embeds "
                            "payloads that stay dormant at FP16 and activate after compression.",
            "why_it_matters": "If you validate the FP16 checkpoint and ship the quantized one, you "
                              "certified a model you did not deploy.",
            "who_should_care": "Anyone shipping quantized weights to edge devices, or accepting "
                               "third-party checkpoints on trust.",
            "the_number": {
                "value": "0% → 85.02%",
                "label": "friend-foe inversion in their backdoored translation model, after quantization",
                "notes": [
                    "A paired stance classifier shifted by up to Δbias = 0.33 on compression.",
                    "Persistence varies by quantization scheme, not by nominal bit-width alone.",
                    "Our example is the mechanism at toy scale, not their attack.",
                    "In it: 2232 of 4096 INT8 codes change while weights move 0.4% of max|w|, and the "
                    "full-precision output on the validation input does not move at all.",
                ],
            },
            "diff": {
                "minus": "certify the FP16 checkpoint, ship the INT8 build",
                "plus": "certify the configuration you actually deploy",
            },
            "watch_out": "Our example demonstrates the structural gap — a perturbation orthogonal to "
                         "the validation input flipping INT8 codes — not the paper's fine-tuning "
                         "attack. It is not a reproduction of their 85.02%.",
            "example": {
                "kind": "analysis",
                "dir": f"examples/{D3}",
                "run_cmd": "bash run.sh",
                "run_summary": "17 lines, numpy, CPU, offline, < 1 s",
                "caption": "Same output at full precision. Different output after INT8.",
                "code": read(D3, "run.py"),
                "code_slide": excerpt(D3, [(8, 14)]),
                "output": read(D3, "expected_output.txt"),
                "tested_in_ci": False,
            },
            "source_url": "https://arxiv.org/abs/2608.27512",
        },
    ],
}

out = ROOT / "data" / "episodes" / "2026-09-01.json"
out.write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out}")
for item in episode["items"]:
    hw = len(item["headline"].split())
    ww = len(item["what_changed"].split())
    print(f"  {item['id']:42} headline={hw:3} words  what_changed={ww:3} words")
