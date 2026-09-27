#!/usr/bin/env python3
"""Score one or more session descriptions with TypeSafe (systemone, jev-1.13.0) and
apply the pre-registered v6 rule. Standard library only.

Usage:
  score.py --action "one or two sentences"            one reading, JSON on stdout
  score.py --action-file path.txt                    same, text read from a file
  score.py --batch cases.json                        list of {"label":..., "action":...}
  add --markdown to print the prompt-header lines and the Notion field values as well.

The request body is request-v6.json beside this script's folder. The API credential is
attached by the Glow app environment (the proxy injects it for api.typesafe.ai); this
script sends no Authorization header and never reads environment values.
"""
import argparse, json, math, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

RUNGS = ["low", "medium", "high", "extra high", "max", "ultracode"]
MODELS = {"most_capable_model": "Fable 5.1", "strong_lower_cost_model": "Opus 5.5"}
URL = "https://api.typesafe.ai/v1/systemone"
REQUEST_PATH = Path(__file__).resolve().parent.parent / "request-v6.json"


def send(body: dict, timeout: int = 120):
    data = json.dumps(body).encode()
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
    sent = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, text = resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read().decode(errors="replace")
    return sent, status, round(time.time() - t0, 2), text


def apply_rule(answers: dict) -> dict:
    eff = answers["effort"]
    score = float(eff["score"])
    probs = {RUNGS[int(k)]: float(v) for k, v in eff["probabilities"].items()}
    rung_index = min(5, int(math.floor(score + 0.5)))
    rung = RUNGS[rung_index]
    ordered = sorted(probs.items(), key=lambda kv: -kv[1])
    modal, runner = ordered[0], ordered[1]
    near_cut = any(abs(score - c) < 0.10 for c in (0.5, 1.5, 2.5, 3.5, 4.5))
    boundary = near_cut or (modal[1] - runner[1] < 0.20)
    mp = {MODELS[k]: float(v) for k, v in answers["model"]["probabilities"].items()}
    p_most = mp["Fable 5.1"]
    model = "Fable 5.1" if p_most >= 0.5 else "Opus 5.5"
    return {
        "score": round(score, 2),
        "rung": rung,
        "rung_probabilities": {r: round(probs.get(r, 0.0), 2) for r in RUNGS},
        "effort_confidence": round(float(eff["confidence"]), 2),
        "modal_rung": modal[0],
        "runner_up_rung": runner[0],
        "boundary": boundary,
        "model": model,
        "model_probabilities": {m: round(mp[m], 2) for m in ("Fable 5.1", "Opus 5.5")},
        "model_confidence": round(float(answers["model"]["confidence"]), 2),
        "model_near_tie": 0.40 <= p_most <= 0.60,
        "cell": f"{model}, {rung}",
    }


def score_one(action: str, label: str = "", request_path: Path = REQUEST_PATH) -> dict:
    body = json.loads(request_path.read_text())
    body["state"]["action"] = action
    for attempt in (1, 2):
        sent, status, latency, text = send(body)
        if status == 200:
            break
    if status != 200:
        return {"label": label, "error": f"HTTP {status} after {attempt} attempt(s)", "sent_utc": sent, "body": text[:500]}
    resp = json.loads(text)
    out = {"label": label, "version": "v6", "sent_utc": sent, "latency_s": latency,
           "response_model": resp.get("model"), "usage": resp.get("usage", {})}
    out.update(apply_rule(resp["answers"]))
    return out


def fmt_probs(d: dict) -> str:
    return ", ".join(f"{k} {v:.2f}" for k, v in d.items())


def markdown(r: dict) -> str:
    if "error" in r:
        return f"- TypeSafe v6: not read ({r['error']}, sent {r['sent_utc']})."
    flags = []
    if r["boundary"]:
        flags.append(f"boundary between {r['runner_up_rung']} and {r['modal_rung']}")
    if r["model_near_tie"]:
        flags.append("model near tie")
    flag_txt = f" Flags: {'; '.join(flags)}." if flags else ""
    header = (f"- **TypeSafe v6** (sent {r['sent_utc']}): **{r['cell']}.** Effort score {r['score']:.2f} "
              f"(confidence {r['effort_confidence']:.2f}); rung probabilities {fmt_probs(r['rung_probabilities'])}. "
              f"Model probabilities {fmt_probs(r['model_probabilities'])} (confidence {r['model_confidence']:.2f}).{flag_txt}")
    notion = {
        "Version": "v6",
        "TypeSafe level": r["rung"],
        "TypeSafe model": r["model"],
        "Rung probabilities": f"score {r['score']:.2f}, confidence {r['effort_confidence']:.2f}: {fmt_probs(r['rung_probabilities'])}",
        "Model probabilities": f"{fmt_probs(r['model_probabilities'])}, confidence {r['model_confidence']:.2f}",
        "TypeSafe detail": (f"v6 sent {r['sent_utc']}; HTTP 200 in {r['latency_s']} s; {r['usage'].get('input_tokens')} input and "
                            f"{r['usage'].get('output_tokens')} output tokens; {r['response_model']}. Rung by rule: {r['rung']} (nearest to the score, halves up)."
                            + (f" Flags: {'; '.join(flags)}." if flags else "")),
        "Input tokens": r["usage"].get("input_tokens"),
        "Output tokens": r["usage"].get("output_tokens"),
    }
    return header + "\n\nNotion row fields:\n" + json.dumps(notion, indent=1, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--action")
    g.add_argument("--action-file")
    g.add_argument("--batch", help="JSON file: list of {label, action}")
    ap.add_argument("--label", default="")
    ap.add_argument("--request", default=str(REQUEST_PATH))
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out", help="write the JSON results to this file as well")
    a = ap.parse_args()
    rp = Path(a.request)
    if a.batch:
        cases = json.loads(Path(a.batch).read_text())
        results = [score_one(c["action"], c.get("label", ""), rp) for c in cases]
    else:
        action = a.action if a.action is not None else Path(a.action_file).read_text().strip()
        results = [score_one(action, a.label, rp)]
    if a.out:
        Path(a.out).write_text(json.dumps(results, indent=1, ensure_ascii=False))
    if a.markdown:
        for r in results:
            print(f"### {r.get('label') or '(unlabelled)'}\n{markdown(r)}\n")
    else:
        print(json.dumps(results, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
