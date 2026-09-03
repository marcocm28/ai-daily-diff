import json, pathlib
H = pathlib.Path(__file__).parent
cfg = lambda n: json.loads((H / n).read_text())["text_config"]
old, new = cfg("config_qwen38_27b.json"), cfg("config_flash_next.json")

def kv_per_token(c):                     # only full-attention layers hold a growing cache
    full = c["layer_types"].count("full_attention")
    return full * 2 * c["num_key_value_heads"] * c["head_dim"] * 2   # K+V, bfloat16

for name, c in (("Qwen3.8-27B", old), ("Qwen3.8-Flash-Next", new)):
    print(f"{name:20} layers={c['num_hidden_layers']:3}  full_attn="
          f"{c['layer_types'].count('full_attention'):3}  kv_heads={c['num_key_value_heads']}"
          f"  kv/token={kv_per_token(c)//1024:3} KiB")

print(f"KV cache per token   {100*(1-kv_per_token(new)/kv_per_token(old)):.1f}% smaller")
print(f"experts              {new['num_experts']} total, {new['num_experts_per_tok']} active "
      f"({100*new['num_experts_per_tok']/new['num_experts']:.1f}% per token)")
