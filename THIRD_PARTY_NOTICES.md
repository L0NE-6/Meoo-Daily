# Third-Party Notices

This project reuses the publicly documented Meoo daily-login protocol from
`shadyrispy/magpie-meoo`.

## Meoo protocol source

- Source: `shadyrispy/magpie-meoo`
- Reference: `src/meoo.mjs`, `dailyLogin`
- Commit reviewed by the source project: `078c04440696f91ecac47496af135c9687f6a451`
- License: MIT
- Reused for: the `GET /api/mc/entitlement/init` request and the semantics of
  `dailyLoginGranted`, `dailyLoginGrantAmount`, `dailyLoginSkipReason`, and
  `dailyLoginBalanceAfter`
- Local implementation: `meoo_daily.py`

The upstream LICENSE file was published with this literal copyright line:

```text
Copyright (c) 2026 YOUR NAME
```

That line is preserved as published. This project does not invent or replace
the upstream author name.

## Upstream MIT license text

```text
MIT License

Copyright (c) 2026 YOUR NAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
