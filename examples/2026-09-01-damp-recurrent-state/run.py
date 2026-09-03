import json, pathlib
c = json.loads((pathlib.Path(__file__).parent / "config_flash_next.json").read_text())["text_config"]

linear = c["layer_types"].count("linear_attention")          # layers with a fixed-size state
per_layer = c["linear_num_value_heads"] * c["linear_key_head_dim"] * c["linear_value_head_dim"]
values = linear * per_layer                                   # state values per sequence
BATCH = 64

for label, bits in (("FP32, as stored today", 32.0), ("DAMP, 9.9 bit/value", 9.9)):
    per_seq = values * bits / 8
    print(f"{label:24} {per_seq/2**20:7.1f} MiB/seq   {per_seq*BATCH/2**30:5.2f} GiB at batch {BATCH}")

print(f"state values per seq     {values:,}  ({linear} linear-attention layers)")
print(f"storage reduction        {100*(1-9.9/32):.1f}%   <- the paper's headline number, from its own bit budget")
