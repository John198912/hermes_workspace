#!/usr/bin/env python3
"""Probe volces-ark/deepseek-v4-pro reasoning_effort to verify which tier is actually active.

Usage:
  python3 scripts/probe_reasoning_effort.py [env_var_name]

Default env var: VOLCES_ARK_API_KEY
Output: side-by-side table of reasoning_tokens for {None, low, medium, high, max}

Why this script exists (2026-07-08):
  - cronjob(action='update', model={"reasoning_effort":"max"}) does NOT propagate to actual API request
  - Only by *measuring* reasoning_tokens can we know which tier is active
  - Without this probe, agent assumes "inherits max" but actually gets medium (21-36 tokens)

Verified data (2026-07-08):
  | effort        | reasoning_tokens |
  |---------------|------------------|
  | not set (cron default) | 21-36 (medium) |
  | low           | 28               |
  | medium        | 21               |
  | high          | 70               |
  | max           | 89               |
"""
import os
import sys
import json
import warnings
warnings.filterwarnings('ignore')

# Disable hermes-agent venv interference (PYTHONPATH from Hermes hijacks imports)
os.environ.pop('PYTHONPATH', None)
os.environ.pop('VIRTUAL_ENV', None)

import requests

ENV_VAR = sys.argv[1] if len(sys.argv) > 1 else 'VOLCES_ARK_API_KEY'
api_key = os.environ.get(ENV_VAR, '')

if not api_key:
    print(f'ERROR: env var {ENV_VAR} not set', file=sys.stderr)
    sys.exit(1)

print(f'Using api_key length={len(api_key)}, starts={api_key[:8]}, ends={api_key[-6:]}')
print()

def probe(effort):
    body = {
        'model': 'deepseek-v4-pro',
        'messages': [{'role': 'user', 'content': '回答：1+1=?'}],
        'max_tokens': 50,
    }
    if effort:
        body['reasoning_effort'] = effort
    r = requests.post(
        'https://ark.cn-beijing.volces.com/api/plan/v3/chat/completions',
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
        json=body, verify=False, timeout=20,
    )
    try:
        d = r.json()
        return {
            'http': r.status_code,
            'finish': d.get('choices', [{}])[0].get('finish_reason'),
            'reasoning_tokens': d.get('usage', {}).get('completion_tokens_details', {}).get('reasoning_tokens', '?'),
            'completion_tokens': d.get('usage', {}).get('completion_tokens', '?'),
            'total_tokens': d.get('usage', {}).get('total_tokens', '?'),
            'content': d.get('choices', [{}])[0].get('message', {}).get('content', '')[:50],
        }
    except Exception as e:
        return {'http': r.status_code, 'err': str(e)[:80], 'raw': r.text[:200]}


results = []
for e in [None, 'low', 'medium', 'high', 'max']:
    label = e if e else 'NONE (cron default)'
    r = probe(e)
    results.append((label, r))

print(f'{"effort":25} {"http":6} {"finish":10} {"reason_tok":12} {"comp_tok":10} {"total_tok":10}')
print('-' * 80)
for label, r in results:
    print(f'{label:25} {str(r.get("http")):6} {str(r.get("finish"))[:10]:10} '
          f'{str(r.get("reasoning_tokens")):12} {str(r.get("completion_tokens")):10} {str(r.get("total_tokens")):10}')

print()
print('Diagnostic:')
none_rt = results[0][1].get('reasoning_tokens', 0)
max_rt = results[-1][1].get('reasoning_tokens', 0)
if isinstance(none_rt, int) and isinstance(max_rt, int):
    if none_rt >= max_rt * 0.9:
        print(f'⚠️  cron default (NONE, {none_rt} tokens) ≈ max ({max_rt} tokens) → likely inheriting max OK')
    elif none_rt <= 30:
        print(f'🟡  cron default (NONE, {none_rt} tokens) = low/medium → NOT inheriting max. Add hard prompt instruction.')
    else:
        print(f'🟡  cron default (NONE, {none_rt} tokens) = mid-tier; max would be {max_rt}. Consider prompt injection.')